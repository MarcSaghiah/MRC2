import numpy as np
import subprocess
from medpy.io import load
import os


def run_hd_bet(input_nii, output_prefix):
    """
    Runs HD-BET to generate a brain mask.
    Returns the path to the generated mask.
    """
    output_path = output_prefix
    subprocess.run([
        "hd-bet",
        "-i", input_nii,
        "-o", output_path,
        "-tta", "0",
        "-mode", "fast"
    ], check=True)

    mask_path = output_path + "_mask.nii.gz"
    if not os.path.exists(mask_path):
        raise FileNotFoundError(f"HD-BET did not generate the mask: {mask_path}")

    return mask_path


def load_volume(nii_path):
    """
    Loads a NIfTI image (3D only).
    """
    data, _ = load(nii_path)
    data = data.astype(np.float32)

    if data.ndim != 3:
        raise ValueError("QC metrics require a 3D NIfTI volume.")

    return data


def compute_qc_metrics(image, mask):
    """
    Computes QC metrics inspired by MRQy.
    Returns a dict.
    """

    fg = image[mask > 0]      # foreground (brain)
    bg = image[mask == 0]     # background

    metrics = {}

    # -----------------------------
    # Basic statistics
    # -----------------------------
    metrics["MEAN"] = float(np.mean(fg))
    metrics["RNG"] = float(np.ptp(fg))                    # max-min
    metrics["VAR"] = float(np.var(fg))
    metrics["CV"] = float(np.std(fg) / np.mean(fg)) if np.mean(fg) != 0 else 0

    # -----------------------------
    # CPP
    # -----------------------------
    metrics["CPP"] = float(np.mean(fg) / np.max(fg)) if np.max(fg) != 0 else 0

    # -----------------------------
    # PSNR
    # -----------------------------
    mse = np.mean((fg - np.mean(fg)) ** 2)
    metrics["PSNR"] = float(20 * np.log10(np.max(fg) / np.sqrt(mse))) if mse > 0 else 0

    # -----------------------------
    # SNR variants
    # -----------------------------
    std_bg = np.std(bg)
    std_fg = np.std(fg)

    metrics["SNR1"] = float(np.mean(fg) / std_bg) if std_bg != 0 else 0
    metrics["SNR2"] = float(np.mean(fg) / std_fg) if std_fg != 0 else 0
    metrics["SNR3"] = float(np.max(fg) / std_bg) if std_bg != 0 else 0
    metrics["SNR4"] = float(np.percentile(fg, 95) / std_bg) if std_bg != 0 else 0

    # -----------------------------
    # CNR
    # -----------------------------
    denom = np.sqrt(np.var(fg) + np.var(bg))
    metrics["CNR"] = float((np.mean(fg) - np.mean(bg)) / denom) if denom != 0 else 0

    # -----------------------------
    # CVP
    # -----------------------------
    metrics["CVP"] = float(std_bg / np.mean(bg)) if np.mean(bg) != 0 else 0

    # -----------------------------
    # CJV
    # -----------------------------
    metrics["CJV"] = float((std_fg + std_bg) / abs(np.mean(fg))) if np.mean(fg) != 0 else 0

    # -----------------------------
    # EFC (Entropy Focus Criterion)
    # -----------------------------
    x = image.flatten()
    x = x / np.max(np.abs(x)) if np.max(np.abs(x)) != 0 else x
    x = x[x > 0]
    efc = -np.sum(x * np.log(x))
    metrics["EFC"] = float(efc)

    # -----------------------------
    # FBER
    # -----------------------------
    num = np.mean(fg ** 2)
    den = np.mean(bg ** 2)
    metrics["FBER"] = float(num / den) if den != 0 else 0

    return metrics


def extract_qc_metrics(nii_path):
    """
    Main public function used by MRC2.
    - Runs HD-BET
    - Loads image + mask
    - Computes QC metrics
    - Returns a dict
    """

    temp_prefix = nii_path.replace(".nii.gz", "").replace(".nii", "") + "_bet"

    # 1) Brain extraction
    mask_path = run_hd_bet(nii_path, temp_prefix)

    # 2) Load image & mask
    img = load_volume(nii_path)
    mask = load_volume(mask_path)

    # 3) Compute QC metrics
    return compute_qc_metrics(img, mask)
