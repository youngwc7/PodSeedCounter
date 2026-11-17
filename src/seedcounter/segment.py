"""Seed detection inside one pod.

Two methods (``segmentation.method``):

* ``ellipse`` (default): seeds are found as ellipse-shaped dark spots. The seedness map is matched
  against a bank of elliptical templates (several sizes, aspect ratios and angles; dark inside, a
  lighter ring around it). Each local best match is a candidate seed with its own ellipse. Candidates
  are accepted strongest first; a candidate is rejected if its ellipse is not filled by a dark spot or
  if its core is already taken by an accepted seed. Neighbouring and slightly overlapping seeds are
  therefore separated by their shape, not by a fixed minimum distance. Each seed's border is its
  ellipse; where two ellipses overlap, a pixel goes to the ellipse whose centre it is relatively
  closer to.
* ``contrast``: the earlier method (darkest points, watershed borders, centerline split).
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.measure import regionprops
from skimage.segmentation import watershed


@dataclass
class Detection:
    labels: np.ndarray        # int label image (bbox crop), 0 = no seed
    split: set                # labels created by splitting a merged object
    smooth: np.ndarray        # smoothed seedness used for borders
    local: np.ndarray         # local (band-pass) contrast
    foreground: np.ndarray    # candidate seed pixels


def detect(s: np.ndarray, zone: np.ndarray, center_y: np.ndarray, r: float, cfg: dict) -> Detection:
    """s: seedness (crop); zone: allowed area; center_y: centerline row per crop column; r: seed radius."""
    if cfg["segmentation"].get("method", "ellipse") == "ellipse":
        return detect_ellipses(s, zone, center_y, r, cfg)
    return detect_contrast(s, zone, center_y, r, cfg)


def _rho(shape, cy, cx, a, b, th):
    """Normalised elliptical distance (1 = on the ellipse) of every pixel of an array of this shape."""
    yy, xx = np.ogrid[:shape[0], :shape[1]]
    c, sn = np.cos(th), np.sin(th)
    u = (xx - cx) * c + (yy - cy) * sn
    v = (yy - cy) * c - (xx - cx) * sn
    return (u / a) ** 2 + (v / b) ** 2


def ellipse_bank(r: float, ec: dict) -> list[tuple]:
    """Zero-sum elliptical templates (kernel, semi-major, semi-minor, angle), all with seed area x scale^2."""
    bank = []
    ring = ec["surround"]
    for sc in ec["scales"]:
        for q in ec["aspects"]:
            a, b = sc * r / np.sqrt(q), sc * r * np.sqrt(q)
            n = 1 if q > 0.9 else int(ec["angles"])
            for i in range(n):
                th = np.pi * i / n
                R = int(np.ceil(ring * a)) + 1
                rho = _rho((2 * R + 1, 2 * R + 1), R, R, a, b, th)
                inside = rho <= 1
                rim = (rho > 1.1 ** 2) & (rho <= ring ** 2)
                k = inside / inside.sum() - ec["surround_weight"] * rim / rim.sum()
                bank.append((k.astype(np.float32), a, b, th))
    return bank


def detect_ellipses(s: np.ndarray, zone: np.ndarray, center_y: np.ndarray, r: float, cfg: dict) -> Detection:
    sc, ec = cfg["segmentation"], cfg["segmentation"]["ellipse"]
    H, W = s.shape
    s1 = cv2.GaussianBlur(s, (0, 0), max(sc["peak_sigma"] * r, 0.5))
    s2 = cv2.GaussianBlur(s, (0, 0), max(sc["dog_sigma"] * r, 0.5))
    local = np.where(zone, s1 - s2, 0)
    fg = (local > 0) & (s1 > sc["seed_threshold"]) & zone

    # 1. match every pixel against the elliptical templates; keep the best template per pixel.
    #    Seeds lie lengthwise in the pod, so the long axis may deviate from the pod axis only so much.
    slope = np.polyfit(np.arange(W), center_y, 1)[0] if W > 1 else 0.0
    pod_angle = float(np.arctan(slope))
    lim = np.radians(ec.get("max_angle_to_pod", 90))
    bank = [k for k in ellipse_bank(r, ec)
            if k[1] / k[2] < 1.1 or abs((k[3] - pod_angle + np.pi / 2) % np.pi - np.pi / 2) <= lim + 1e-6]
    best = np.zeros(s.shape, np.float32)
    pose = np.zeros(s.shape, np.int32)
    for i, (k, *_rest) in enumerate(bank):
        resp = cv2.filter2D(s1, -1, k, borderType=cv2.BORDER_CONSTANT)
        better = resp > best
        best[better], pose[better] = resp[better], i
    best = np.where(zone, best, 0)

    # 2. candidates = local best matches, strong enough relative to the clear seeds of this pod
    cand = peak_local_max(best, min_distance=max(1, int(sc["min_distance"] * r)),
                          threshold_abs=ec["min_response"], exclude_border=False)
    cand = sorted((tuple(p) for p in cand), key=lambda p: -best[p])
    if cand:
        top = float(np.percentile([best[p] for p in cand], 90))
        cand = [p for p in cand if best[p] >= ec["relative_response"] * top]

    # 3. accept strongest first: filled by a dark spot, core not already taken
    taken = np.zeros(s.shape, bool)
    seeds = []                                     # (cy, cx, a, b, th)
    min_px = sc["min_area"] * np.pi * r * r
    for y, x in cand:
        _, a, b, th = bank[pose[y, x]]
        m = int(np.ceil(a)) + 2
        ys, xs = slice(max(y - m, 0), min(y + m + 1, H)), slice(max(x - m, 0), min(x + m + 1, W))
        rho = _rho((ys.stop - ys.start, xs.stop - xs.start), y - ys.start, x - xs.start, a, b, th)
        z = zone[ys, xs]
        inside, core = (rho <= 1) & z, (rho <= ec["core"] ** 2) & z
        if inside.sum() < min_px or not core.any():
            continue
        level = float(np.median(s1[ys, xs][core]))
        if level < ec["min_level"]:
            continue
        if (s1[ys, xs][inside] > 0.5 * level).mean() < ec["fill"]:
            continue                               # not one filled ellipse (e.g. a gap between seeds)
        if taken[ys, xs][core].mean() > ec["max_overlap"]:
            continue                               # same seed as an accepted one
        taken[ys, xs] |= core
        seeds.append((y, x, a, b, th, level))

    # pale spots: much lighter than the pod's typical accepted seed are not seeds
    if seeds:
        typical = float(np.median([q[5] for q in seeds]))
        seeds = [q[:5] for q in seeds if q[5] >= ec.get("relative_level", 0) * typical]

    # 4. borders: each seed's ellipse; overlapping pixels go to the relatively closer centre
    labels = np.zeros(s.shape, np.int32)
    nearest = np.full(s.shape, np.inf)
    for i, (y, x, a, b, th) in enumerate(seeds, start=1):
        m = int(np.ceil(a)) + 2
        ys, xs = slice(max(y - m, 0), min(y + m + 1, H)), slice(max(x - m, 0), min(x + m + 1, W))
        rho = _rho((ys.stop - ys.start, xs.stop - xs.start), y - ys.start, x - xs.start, a, b, th)
        win = (rho <= 1) & zone[ys, xs] & (rho < nearest[ys, xs])
        labels[ys, xs][win] = i
        nearest[ys, xs][win] = rho[win]

    # seeds that share one connected dark area with another seed were separated by shape
    blobs, _ = ndi.label(fg | (labels > 0))
    owner = {}
    for i, (y, x, *_e) in enumerate(seeds, start=1):
        owner.setdefault(blobs[y, x], []).append(i)
    split = {i for b, ids in owner.items() if b and len(ids) > 1 for i in ids}
    for p in regionprops(labels):                  # drop slivers left over after sharing
        if p.area < sc["min_area"] * np.pi * r * r:
            labels[labels == p.label] = 0
            split.discard(p.label)
    return Detection(labels, split, s1, local, fg)


def detect_contrast(s: np.ndarray, zone: np.ndarray, center_y: np.ndarray, r: float, cfg: dict) -> Detection:
    """Earlier method: darkest points as centres, watershed borders, centerline split."""
    rows = np.arange(s.shape[0])[:, None]
    top_side = rows < center_y[None, :]
    sc = cfg["segmentation"]
    s1 = cv2.GaussianBlur(s, (0, 0), max(sc["peak_sigma"] * r, 0.5))
    s2 = cv2.GaussianBlur(s, (0, 0), max(sc["dog_sigma"] * r, 0.5))
    local = np.where(zone, s1 - s2, 0)
    min_dist = max(1, int(sc["min_distance"] * r))

    # 1. seed centres = local maxima of smoothed darkness with enough local contrast
    peaks = peak_local_max(np.where(zone, s1, 0), min_distance=min_dist, exclude_border=False)
    peaks = [p for p in peaks if zone[p[0], p[1]] and local[p[0], p[1]] > sc["peak_contrast"]
             and s1[p[0], p[1]] > sc["seed_threshold"]]
    markers = np.zeros(s.shape, np.int32)
    for i, (y, x) in enumerate(peaks, start=1):
        markers[y, x] = i
    fg = (local > 0) & (s1 > sc["seed_threshold"]) & zone
    markers[~fg] = 0
    labels = watershed(-s1, markers, mask=fg)

    # 2. an object much larger than a seed that lies substantially on both sides of the
    #    centerline is two seeds (one per row): split it at the centerline
    area = np.pi * r * r
    split: set = set()
    nxt = int(labels.max()) + 1
    for p in regionprops(labels):
        if p.area < sc["split_area"] * area:
            continue
        region = labels == p.label
        frac_top = (region & top_side).sum() / p.area
        if min(frac_top, 1 - frac_top) < sc["split_side"]:
            continue
        parts = []
        for side in (top_side, ~top_side):
            half = region & side
            if half.sum() < sc["min_area"] * area:
                continue
            sh = np.where(half, s1, 0)
            # a real second seed has its own darkest point away from the centerline;
            # one seed lying across the line only peaks at the cut itself
            pk = [q for q in peak_local_max(sh, min_distance=min_dist, num_peaks=3, exclude_border=False)
                  if half[q[0], q[1]] and abs(q[0] - center_y[q[1]]) >= sc["split_offset"] * r]
            if not pk and p.area >= sc["split_area_large"] * area:
                # big enough for two seeds even without a second dark centre (faint seed
                # overlapping a darker one): use the darkest point of that side
                pk = [np.unravel_index(np.argmax(sh), sh.shape)]
            parts.append((half, pk))
        if len(parts) < 2 or any(not pk for _, pk in parts):
            continue
        if p.area < sc["split_area_large"] * area:
            # two seeds show a lighter gap between their centres; one elongated seed does not
            a = max(parts[0][1], key=lambda q: s1[q[0], q[1]])
            b = max(parts[1][1], key=lambda q: s1[q[0], q[1]])
            t = np.linspace(0, 1, 25)
            line = s1[np.round(a[0] + t * (b[0] - a[0])).astype(int), np.round(a[1] + t * (b[1] - a[1])).astype(int)]
            if 1 - line.min() / max(min(s1[a[0], a[1]], s1[b[0], b[1]]), 1e-6) < sc["split_dip"]:
                continue
        labels[region] = 0
        for half, pk in parts:
            mk = np.zeros(s.shape, np.int32)
            for q in pk:
                mk[q[0], q[1]] = nxt
                split.add(nxt)
                nxt += 1
            sub = watershed(-s1, mk, mask=half)
            labels[sub > 0] = sub[sub > 0]

    # 3. drop fragments that are too small to be a seed
    for p in regionprops(labels):
        if p.area < sc["min_area"] * area:
            labels[labels == p.label] = 0
            split.discard(p.label)
    return Detection(labels, split, s1, local, fg)
