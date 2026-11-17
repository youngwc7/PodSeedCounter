"""Finding pods and their geometry: outline, centerline, bud and stem cuts, seed zone."""
from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np
from scipy import ndimage as ndi


@dataclass
class PodGeom:
    index: int
    bbox: tuple            # (y0, y1, x0, x1) in work pixels, exclusive end
    mask: np.ndarray       # bool, bbox crop
    x0: int                # first / last column of the pod (work pixels, absolute)
    x1: int
    top: np.ndarray        # per column x0..x1: top outline y (absolute)
    bot: np.ndarray
    center: np.ndarray     # smoothed centerline y per column
    width: np.ndarray
    body_width: float
    bud_x: float           # bud cut (absolute x): nothing left of this is counted
    stem_x: float          # stem cut (absolute x)
    bud_visible: bool = True
    stem_visible: bool = True
    warnings: list = field(default_factory=list)

    def center_at(self, xs):
        return np.interp(xs, np.arange(self.x0, self.x1 + 1), self.center)

    def outline_at(self, xs):
        cols = np.arange(self.x0, self.x1 + 1)
        return np.interp(xs, cols, self.top), np.interp(xs, cols, self.bot)


def pod_mask(rgb: np.ndarray, cfg: dict) -> np.ndarray:
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    sat = cv2.GaussianBlur(hsv[..., 1], (0, 0), 2).astype(np.float32)
    val = hsv[..., 2]
    background = val >= np.percentile(val, 60)
    bg_sat = float(np.median(sat[background])) if background.any() else 0.0
    mask = sat > bg_sat + cfg["pods"]["saturation_margin"]
    mask = ndi.binary_opening(mask, iterations=2)
    return ndi.binary_fill_holes(mask)


def _runs(col: np.ndarray) -> list[tuple[int, int]]:
    """Vertical runs [start, end) of True pixels in one mask column."""
    d = np.diff(np.r_[0, col.astype(np.int8), 0])
    return list(zip(np.nonzero(d == 1)[0].tolist(), np.nonzero(d == -1)[0].tolist()))


def split_touching(mask: np.ndarray, sat: np.ndarray, cfg: dict) -> tuple[np.ndarray, list[np.ndarray]]:
    """Separate pods that touch or overlap, i.e. with no background gap between them.

    A column whose mask run is much taller than one pod width holds two pods. Each stretch of such
    columns gets one seam: the smoothest palest (least saturated) path through it, found by dynamic
    programming. Where the pods part next to the stretch, the seam is pinned into that real gap, so
    the cut joins it; where they do not part (fused stem ends), the seam is followed further until
    they do or the image ends. Returns the cut mask and the seams (arrays of (x, y)).
    """
    pc = cfg["pods"]
    tall, stop = pc["touch_height"], pc["touch_stop_height"]
    smooth, max_step = pc["touch_smoothness"], 2
    H, W = mask.shape
    runs = [_runs(mask[:, x]) for x in range(W)]
    hs = np.array([e - s for r in runs for s, e in r])
    if hs.size == 0:
        return mask, []
    hs = hs[hs >= 0.4 * np.percentile(hs, 95)]
    w = float(np.median(hs))                       # typical width of one pod
    cost = cv2.GaussianBlur(sat.astype(np.float32), (0, 0), 1.0) / 255.0
    rows = np.arange(H)
    INF = 1e9
    out, seams = mask.copy(), []
    done = np.zeros(W, bool)

    def tall_run(x):
        return next(((s, e) for s, e in runs[x] if e - s > tall * w), None)

    def gap(x, r):
        """(g0, g1) background rows between two runs in column x that both overlap run r."""
        if not 0 <= x < W:
            return None
        ov = sorted((s, e) for s, e in runs[x] if s < r[1] + 2 and e > r[0] - 2)
        return (ov[0][1], ov[1][0]) if len(ov) >= 2 else None

    for x in range(W):
        if done[x] or tall_run(x) is None:
            continue
        seg = {x: tall_run(x)}
        for step in (-1, 1):                       # grow while the column is still one fused run
            xx, cur = x + step, seg[x]
            while 0 <= xx < W:
                ov = [(s, e) for s, e in runs[xx] if s < cur[1] and e > cur[0]]
                if len(ov) != 1 or ov[0][1] - ov[0][0] <= stop * w:
                    break
                seg[xx] = cur = ov[0]
                xx += step
        xs = sorted(seg)
        done[xs[0]:xs[-1] + 1] = True
        gl, gr = gap(xs[0] - 1, seg[xs[0]]), gap(xs[-1] + 1, seg[xs[-1]])

        def unary(i):
            s, e = seg[xs[i]]
            u = np.full(H, INF)
            m = min(int(0.3 * w), (e - s) // 5)    # keep the seam off the outer pod walls
            if e - m > s + m:
                u[s + m:e - m] = cost[s + m:e - m, xs[i]]
            return u

        n = len(xs)
        acc = np.empty((n, H))
        back = np.zeros((n, H), np.int32)
        acc[0] = unary(0)
        if gl is not None:
            acc[0][(rows < gl[0] - 1) | (rows > gl[1])] = INF
        for i in range(1, n):
            best, arg = np.full(H, INF), np.zeros(H, np.int32)
            for d in range(-max_step, max_step + 1):
                prev = np.roll(acc[i - 1], d) + smooth * abs(d)
                if d > 0:
                    prev[:d] = INF
                elif d < 0:
                    prev[d:] = INF
                better = prev < best
                best[better], arg[better] = prev[better], (rows - d)[better]
            acc[i], back[i] = best + unary(i), arg
        if gr is not None:
            acc[-1][(rows < gr[0] - 1) | (rows > gr[1])] = INF
        y = int(np.argmin(acc[-1]))
        if acc[-1, y] >= INF:
            continue
        path = [y]
        for i in range(n - 1, 0, -1):
            y = int(back[i, y])
            path.append(y)
        pts = list(zip(xs, path[::-1]))

        def follow(x, y, step):                    # no gap at this end: follow the seam onwards
            more = []
            x += step
            while 0 <= x < W:
                r = next(((s, e) for s, e in runs[x] if s <= y < e), None)
                if r is None or y - r[0] < 3 or r[1] - y < 3:
                    break
                lo, hi = max(r[0] + 2, y - max_step), min(r[1] - 2, y + max_step + 1)
                y = lo + int(np.argmin(cost[lo:hi, x]))
                more.append((x, y))
                x += step
            return more

        if gl is None:
            pts = follow(*pts[0], -1)[::-1] + pts
        if gr is None:
            pts = pts + follow(*pts[-1], 1)
        for xx, yy in pts:
            out[max(yy - 1, 0):yy + 2, xx] = False
        seams.append(np.array(pts))
    return out, seams


def _columns(mask: np.ndarray, y_off: int, x_off: int):
    ys, xs = np.nonzero(mask)
    x0, x1 = xs.min(), xs.max()
    n = x1 - x0 + 1
    top = np.full(n, np.nan)
    bot = np.full(n, np.nan)
    order = np.argsort(xs, kind="stable")
    xs_s, ys_s = xs[order], ys[order]
    idx = np.searchsorted(xs_s, np.arange(x0, x1 + 2))
    for i in range(n):
        col = ys_s[idx[i]:idx[i + 1]]
        if col.size:
            top[i], bot[i] = col.min(), col.max()
    good = ~np.isnan(top)
    cols = np.arange(n)
    top = np.interp(cols, cols[good], top[good])
    bot = np.interp(cols, cols[good], bot[good])
    return x0 + x_off, x1 + x_off, top + y_off, bot + y_off


def find_pods(rgb: np.ndarray, cfg: dict, seed_radius: float) -> tuple[list[PodGeom], list[str]]:
    """Pods in a (work-scale) RGB image, sorted top to bottom."""
    pc = cfg["pods"]
    warnings: list[str] = []
    mask = pod_mask(rgb, cfg)
    seams: list = []
    if pc.get("split_touching", True):
        sat = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[..., 1]
        mask, seams = split_touching(mask, sat, cfg)
    lab, n = ndi.label(mask)
    if n == 0:
        return [], ["no pods found"]
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    keep = [i + 1 for i in range(n) if sizes[i] >= pc["min_area_frac"] * sizes.max()]
    slices = ndi.find_objects(lab)
    H, W = mask.shape
    geoms = []
    for k in keep:
        sl = slices[k - 1]
        y0, y1 = max(sl[0].start - 2, 0), min(sl[0].stop + 2, H)
        x0, x1 = max(sl[1].start - 2, 0), min(sl[1].stop + 2, W)
        m = lab[y0:y1, x0:x1] == k
        px0, px1, top, bot = _columns(m, y0, x0)
        width = ndi.median_filter(bot - top + 1, 5)
        nn = len(width)
        body = float(np.median(width[int(nn * 0.2):max(int(nn * 0.8), int(nn * 0.2) + 1)]))
        win = max(5, int(0.6 * body))
        center = ndi.uniform_filter1d((top + bot) / 2.0, win, mode="nearest")
        wide_l = np.nonzero(width >= pc["left_body_frac"] * body)[0]
        wide_r = np.nonzero(width >= pc["right_body_frac"] * body)[0]
        bud_x = max(px0 + wide_l[0], px0 + pc["bud_frac"] * body)
        stem_x = px0 + wide_r[-1]
        g = PodGeom(0, (y0, y1, x0, x1), m, px0, px1, top, bot, center, width, body, float(bud_x), float(stem_x))
        if px0 <= 1:
            g.bud_visible = False
            g.warnings.append("bud end touches the image edge")
        if px1 >= W - 2 and width[-1] >= pc["right_body_frac"] * body:
            g.stem_visible = False
            g.warnings.append("stem end is outside the image")
        tilt = np.degrees(np.arctan(np.polyfit(np.arange(nn), center, 1)[0]))
        if abs(tilt) > pc["max_tilt_deg"]:
            g.warnings.append(f"pod tilted {tilt:.0f} degrees; results may be unreliable")
        if any(np.any(lab[np.clip(p[:, 1] + d, 0, H - 1), p[:, 0]] == k) for p in seams for d in (-2, 2)):
            g.warnings.append("pod touched another pod; separated automatically along the seam")
        if (y1 - y0) > 2.2 * body:
            g.warnings.append("pod outline is unusually tall; pods may be touching")
        if stem_x - bud_x < 4 * seed_radius:
            g.warnings.append("pod too short to analyse")
            continue
        geoms.append(g)
    geoms.sort(key=lambda g: float(np.mean(g.center)))
    for i, g in enumerate(geoms, start=1):
        g.index = i
    if not geoms:
        warnings.append("no pods found")
    return geoms, warnings


def seed_zone(g: PodGeom, cfg: dict, seed_radius: float) -> np.ndarray:
    """Where seeds may lie (bbox crop): inside the pod wall, between the bud and stem cuts."""
    pc = cfg["pods"]
    y0, y1, x0, x1 = g.bbox
    xs = np.arange(x0, x1)[None, :]
    dist = ndi.distance_transform_edt(g.mask)
    margin = pc["end_margin"] * seed_radius
    return g.mask & (xs >= g.bud_x + margin) & (xs <= g.stem_x - margin) & (dist >= pc["rim_frac"] * g.body_width)
