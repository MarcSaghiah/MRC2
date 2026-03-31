# MRC2

**MRC2** (Magnetic Resonance Contrast Classification) is a Python pipeline designed to convert DICOM images to NIfTI, extract DICOM metadata from medical images, compute quality control (QC) metrics inspired by MRQy, automatically predict MRI contrast using a pre-trained model, and generate a summary CSV file containing all relevant information for each image.

## Requirements

* Python ≥ 3.10
* Python packages: pandas, numpy, nibabel, medpy, joblib, lightgbm
* External software:
  * dcm2niix (DICOM → NIfTI conversion)
  * hd-bet (brain extraction / brain mask)
* Pre-trained contrast prediction model:  
  `prediction_models/model7_lgbm_full_pipeline_dicom_qc_metrics_no_categorical.pkl`  
  You may replace this model with another compatible one if available.

Make sure that **dcm2niix** and **hd-bet** are accessible from your system PATH.

## Usage

### Run the pipeline on a single image or a folder

```bash
python mrqcnet.py --input <image_or_folder_path> --output <output_csv_path>
```

* `<image_or_folder_path>` : path to a NIfTI image, a DICOM image, or a folder containing multiple images.
* `<output_csv_path>` : path to the output CSV file.

### Supported input cases

* Unique DICOM image
* Multiple DICOM images
* Unique Nifti image
* Multiple Nifti images
* Mix of DICOM and Nifti images in the same folder

## Output

The generated CSV file contains the following columns :

**General information :** input_source, nii_file, Image name
**DICOM metadata :** MagneticFieldStrength, ImagingFrequency, Manufacturer, ManufacturersModelName, BodyPartExamined, MRAcquisitionType, SeriesDescription, ProtocolName, ScanningSequence, SequenceVariant, ScanOptions, SeriesNumber, SliceThickness, SpacingBetweenSlices, EchoTime, RepetitionTime, FlipAngle, EchoTrainLength, PhaseEncodingSteps, AcquisitionMatrixPE, PixelBandwidth, InPlanePhaseEncodingDirectionDICOM, NumberOfAverages, EchoNumber, InversionTime
**QC metrics :** mean, range, variance, cv, cpp, psnr, snr1, snr2, snr3, snr4, cnr, cvp, cjv, efc, fber
**Contrast prediction :** predicted_contrast, confidence_score

## Authors

Code developed by Marc Saghiah and Benjamin Lemasson.
