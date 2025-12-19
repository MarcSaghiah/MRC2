import json
import os

# Liste des champs sélectionnés
SELECTED_FIELDS = [
    "MagneticFieldStrength",
    "ImagingFrequency",
    "Manufacturer",
    "ManufacturersModelName",
    "BodyPartExamined",
    "MRAcquisitionType",
    "SeriesDescription",
    "ProtocolName",
    "ScanningSequence",
    "SequenceVariant",
    "ScanOptions",
    "SeriesNumber",
    "SliceThickness",
    "SpacingBetweenSlices",
    "EchoTime",
    "RepetitionTime",
    "FlipAngle",
    "EchoTrainLength",
    "PhaseEncodingSteps",
    "AcquisitionMatrixPE",
    "PixelBandwidth",
    "InPlanePhaseEncodingDirectionDICOM",
    "NumberOfAverages",
    "EchoNumber",
    "InversionTime"
]


def extract_metadata(nii_path, json_path):
    """
    MRC2-compatible function.
    Reads metadata from the JSON file if available.
    Returns a dict with:
        - Image_Name
        - all selected metadata fields (or None if not present)
    """

    result = {}

    # Add image name
    result["Image"] = os.path.basename(nii_path)

    # No JSON → return missing metadata
    if json_path is None or not os.path.exists(json_path):
        for field in SELECTED_FIELDS:
            result[field] = None
        return result

    # Load JSON
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception:
        # If JSON unreadable → fill with None
        for field in SELECTED_FIELDS:
            result[field] = None
        return result

    # Extract fields
    for field in SELECTED_FIELDS:
        result[field] = data.get(field, None)

    return result
