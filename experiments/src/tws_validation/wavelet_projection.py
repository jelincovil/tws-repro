from __future__ import annotations
import numpy as np
import pywt


def _pad_for_boundary(x: np.ndarray, level: int, boundary: str) -> tuple[np.ndarray, tuple[slice, ...]]:
    """Pad for non-periodic boundary experiments while preserving SWT divisibility.

    PyWavelets SWT itself uses a shift-invariant periodic convention. For
    symmetric/zero boundary sensitivity checks we pad by one level block before
    applying the periodic SWT and crop back afterwards.
    """
    x = np.asarray(x, dtype=float)
    if boundary == "periodization":
        return x, tuple(slice(0, n) for n in x.shape)
    pad = 2 ** int(level)
    if boundary == "symmetric":
        mode = "reflect"
        kwargs = {}
    elif boundary == "zero":
        mode = "constant"
        kwargs = {"constant_values": 0.0}
    else:
        raise ValueError("boundary must be one of ['periodization', 'symmetric', 'zero']")
    pads = [(pad, pad) for _ in x.shape]
    y = np.pad(x, pads, mode=mode, **kwargs)
    crop = tuple(slice(pad, pad+n) for n in x.shape)
    return y, crop


def project_1d(x: np.ndarray, j: int, wavelet: str = "db2", boundary: str = "periodization") -> np.ndarray:
    """Coarse-retaining stationary wavelet projection P_j in 1D.

    Convention: retain the approximation block A_{j+1}; all details are set to
    zero and the stationary inverse transform reconstructs the coarse signal.
    """
    level = int(j) + 1
    if level < 1:
        raise ValueError("j must be >= 0")
    xp, crop = _pad_for_boundary(np.asarray(x, dtype=float), level, boundary)
    coeffs = pywt.swt(xp, wavelet, level=level, trim_approx=False, norm=False)
    # Zero the detail bands in place. Allocating a parallel set of zero arrays
    # doubles peak memory for no numerical benefit; the result is bit-identical.
    kept = []
    for cA, cD in coeffs:
        cD[...] = 0.0
        kept.append((cA, cD))
    y = pywt.iswt(kept, wavelet)
    return y[crop]


def project_2d(x: np.ndarray, j: int, wavelet: str = "db2", boundary: str = "periodization") -> np.ndarray:
    """Coarse-retaining stationary wavelet projection P_j in 2D.

    Convention: retain approximation coefficients and remove detail coefficients
    at levels 1..j+1. Inputs must have axes divisible by 2**(j+1), unless padded
    upstream.
    """
    level = int(j) + 1
    if level < 1:
        raise ValueError("j must be >= 0")
    xp, crop = _pad_for_boundary(np.asarray(x, dtype=float), level, boundary)
    coeffs = pywt.swt2(xp, wavelet, level=level, trim_approx=False, norm=False)
    # Zero the detail bands in place rather than allocating a parallel set of
    # zero arrays. The result is bit-identical, but peak memory drops by ~40%:
    # at j=6 on a padded 384x384 field the old form allocated 21 extra arrays
    # and could fail with MemoryError on an otherwise capable machine.
    kept = []
    for cA, details in coeffs:
        for d in details:
            d[...] = 0.0
        kept.append((cA, details))
    y = pywt.iswt2(kept, wavelet)
    return y[crop]


def pad_to_swt(x: np.ndarray, max_level: int, mode: str = "edge") -> tuple[np.ndarray, tuple[slice, ...]]:
    """Pad each axis to a multiple of 2**max_level; return padded array and crop slices."""
    x = np.asarray(x)
    mult = 2 ** int(max_level)
    pads = []
    slices = []
    for n in x.shape:
        extra = (-n) % mult
        before, after = 0, extra
        pads.append((before, after))
        slices.append(slice(0, n))
    return np.pad(x, pads, mode=mode), tuple(slices)
