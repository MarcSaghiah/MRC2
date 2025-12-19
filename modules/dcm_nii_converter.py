import os
import subprocess
import tempfile
import shutil


def run_dcm2niix(input_path, output_dir):
    """
    Runs dcm2niix on the input DICOM directory.
    Returns the generated .nii.gz and .json paths.
    """

    command = [
        "dcm2niix",
        "-z", "y",            # gzip NIfTI
        "-o", output_dir,     # output folder
        "-f", "%p_%s",        # pattern: protocol_seriesnumber
        input_path            # input dicom folder
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise RuntimeError(
            "dcm2niix is not installed or not found in PATH. "
            "Install it via: sudo apt install dcm2niix OR use conda install -c conda-forge dcm2niix."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"dcm2niix failed: {e.stderr.decode()}")

    # Find generated files
    nii = json_file = None
    for f in os.listdir(output_dir):
        full = os.path.join(output_dir, f)
        if f.endswith(".nii") or f.endswith(".nii.gz"):
            nii = full
        elif f.endswith(".json"):
            json_file = full

    if nii is None:
        raise RuntimeError("dcm2niix produced no NIfTI file. Check your input DICOM.")

    return nii, json_file



def convert_dcm_to_nii(input_path):
    """
    Converts a DICOM series (folder or single file) to NIfTI.
    Returns: (nii_path, json_path).
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input DICOM path does not exist: {input_path}")

    # If the input is a DICOM file, copy it into a temporary directory
    cleanup_temp = False
    dicom_folder = input_path

    if os.path.isfile(input_path):
        temp_dir = tempfile.mkdtemp(prefix="dicom_")
        shutil.copy(input_path, os.path.join(temp_dir, os.path.basename(input_path)))
        dicom_folder = temp_dir
        cleanup_temp = True

    # Output temporary folder for dcm2niix
    output_dir = tempfile.mkdtemp(prefix="dcm2niix_out_")

    try:
        nii_path, json_path = run_dcm2niix(dicom_folder, output_dir)
        return nii_path, json_path

    finally:
        # Cleanup if input was a single file
        if cleanup_temp:
            shutil.rmtree(dicom_folder, ignore_errors=True)
        # Note: output_dir is NOT removed — we need the .nii and .json
