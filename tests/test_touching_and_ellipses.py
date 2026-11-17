"""Synthetic checks (no example images needed): touching pods are separated, touching seeds are
counted one by one by the elliptical shape filter, and pale spots are not seeds."""
import cv2
import numpy as np
import pytest
from scipy import ndimage as ndi

from seedcounter.config import load_config
from seedcounter.pods import find_pods
from seedcounter.segment import detect


def _pod_image(touch: bool) -> np.ndarray:
    """White image with three long yellow pods. With touch=True the second pod is tilted so that
    it runs into the first one towards the right end (no background gap there)."""
    img = np.full((300, 900, 3), 250, np.uint8)
    pod = (225, 205, 120)
    cv2.ellipse(img, (450, 60), (400, 30), 0, 0, 360, pod, -1)
    cv2.ellipse(img, (450, 130), (400, 30), -5 if touch else 0, 0, 360, pod, -1)
    cv2.ellipse(img, (450, 230), (400, 30), 0, 0, 360, pod, -1)
    return img


@pytest.mark.nodata
@pytest.mark.parametrize("touch", [False, True])
def test_touching_pods_are_separated(touch):
    cfg = load_config()
    geoms, _ = find_pods(_pod_image(touch), cfg, seed_radius=8)
    assert len(geoms) == 3
    flagged = [any("separated" in w for w in g.warnings) for g in geoms]
    assert flagged == ([True, True, False] if touch else [False, False, False])


def _seed_field(centres, r=13, shape=(90, 400)):
    """Seedness map with elliptical seeds (long axis along the pod), touching each other."""
    s = np.zeros(shape, np.float32)
    for cy, cx in centres:
        cv2.ellipse(s, (cx, cy), (int(1.25 * r), int(0.85 * r)), 0, 0, 360, 0.3, -1)
    return cv2.GaussianBlur(s, (0, 0), 1.5)


@pytest.mark.nodata
def test_touching_seeds_counted_individually():
    cfg = load_config()
    r = 13
    centres = [(30, 60 + 30 * i) for i in range(8)] + [(60, 75 + 30 * i) for i in range(7)]
    s = _seed_field(centres, r)
    zone = np.ones_like(s, bool)
    det = detect(s, zone, np.full(s.shape[1], 45.0), r, cfg)
    assert det.labels.max() == len(centres)
    # every true seed centre lies inside a detected seed, and each detection holds one centre
    hits = [det.labels[cy, cx] for cy, cx in centres]
    assert 0 not in hits and len(set(hits)) == len(centres)


@pytest.mark.nodata
def test_pale_spot_is_not_a_seed():
    cfg = load_config()
    r = 13
    s = _seed_field([(30, 60), (30, 120), (60, 90)], r)
    cv2.ellipse(s, (300, 45), (16, 11), 0, 0, 360, 0.06, -1)      # faint spot, 1/5 of seed darkness
    det = detect(s, np.ones_like(s, bool), np.full(s.shape[1], 45.0), r, cfg)
    assert det.labels.max() == 3
    assert det.labels[45, 300] == 0


@pytest.mark.nodata
def test_contrast_method_still_available():
    cfg = load_config(overrides={"segmentation.method": "contrast"})
    s = _seed_field([(30, 60), (30, 140), (60, 100)])
    det = detect(s, np.ones_like(s, bool), np.full(s.shape[1], 45.0), 13, cfg)
    assert det.labels.max() >= 3
    assert ndi.label(det.labels > 0)[1] >= 1
