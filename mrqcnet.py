import os
import argparse
import pandas as pd

# Modules
from modules.dcm_nii_converter import convert_dcm_to_nii
from modules.metadata_extractor import extract_metadata
from modules.qc_metrics_extractor import extract_qc_metrics
from modules.contrast_predictor import predict_contrast_from_results


def process_one_image(input_path):
    """
    Processes a single image and returns a dictionary of results
    (metadata + qc metrics + contrast prediction).
    """

    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    print(f"\n[INFO] Processing file: {input_path}")

    # Step 1: Convert DICOM to NIfTI
    if os.path.isdir(input_path) or ext in [".dcm", ".dicom"]:
        print(f"[INFO] Converting DICOM to NIfTI: {input_path}")
        nii_path, json_path = convert_dcm_to_nii(input_path)

    elif ext in [".nii", ".gz"] or input_path.endswith((".nii", ".nii.gz")):
        nii_path = input_path
        json_path = input_path.replace(".nii.gz", ".json").replace(".nii", ".json")
        if not os.path.exists(json_path):
            print(f"[WARNING] No JSON metadata file found.")
            json_path = None

    else:
        raise ValueError("Unsupported input format. Expected DICOM folder or NIfTI image.")

    # Step 2: Extract metadata
    metadata_dict = extract_metadata(nii_path, json_path)

    # Step 3: QC metrics
    qc_metrics_dict = extract_qc_metrics(nii_path)
    
    # Step 4: Combine metadata + QC to a results dict (required before prediction)
    results = {
        "input_source": input_path,
        "nii_file": nii_path
    }
    results.update(metadata_dict)
    results.update(qc_metrics_dict)

    # Step 5: Predict contrast (now that all features are available)
    try:
        contrast_prediction, confidence_score, all_probabilities = predict_contrast_from_results(results)
    except Exception as e:
        # Ne casse pas le pipeline si la prédiction échoue : on log l'erreur et continue
        print(f"[WARNING] Contrast prediction failed for {nii_path}: {e}")
        contrast_prediction, confidence_score, all_probabilities = None, None, None

    # Step 6: Add prediction outputs to results
    results.update({
        "predicted_contrast": contrast_prediction,
        "confidence_score": confidence_score
    })
    
    if all_probabilities is not None:
        for k, v in all_probabilities.items():
            results[f"prob_{k}"] = v

    return results


def find_all_images(input_dir):
    """
    Finds all supported images inside a directory.
    Returns a list of paths.
    """

    supported = []

    for root, _, files in os.walk(input_dir):
        for f in files:
            full = os.path.join(root, f)
            f_lower = f.lower()

            if f_lower.endswith((".nii", ".nii.gz", ".dcm", ".dicom")):
                supported.append(full)

    # If no known files → assume DICOM series folder
    if not supported:
        print("[INFO] No recognizable files. Treating folder as DICOM series.")
        supported.append(input_dir)

    return supported


def process_folder(input_dir):
    print(f"\n[INFO] Scanning folder: {input_dir}")
    files = find_all_images(input_dir)
    print(f"[INFO] Found {len(files)} images.")

    results = []
    for f in files:
        try:
            res = process_one_image(f)
            results.append(res)
        except Exception as e:
            print(f"[ERROR] Could not process {f}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="MRC2: Magnetic Resonance Contrast Classification")
    parser.add_argument("--input", required=True, help="Path to the input image or folder")
    parser.add_argument("--output", required=True, help="Output CSV file")
    args = parser.parse_args()

    outdir = os.path.dirname(args.output)
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    # Single file
    if os.path.isfile(args.input):
        results = [process_one_image(args.input)]

    # Folder → multiple images
    elif os.path.isdir(args.input):
        results = process_folder(args.input)

    else:
        raise ValueError("Input must be a file or a folder.")

    df = pd.DataFrame(results)
    df.to_csv(args.output, index=False)

    print(f"\n[SUCCESS] Final results saved to: {args.output}")


if __name__ == "__main__":
    main()
