# ============================================================
# Base image (stable, long-term support)
# ============================================================
FROM python:3.10-slim

# ============================================================
# Environment variables
# ============================================================
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# ============================================================
# System dependencies
# ============================================================
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    git \
    wget \
    curl \
    unzip \
    ca-certificates \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libstdc++6 \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Install dcm2niix (DICOM → NIfTI)
# ============================================================
RUN wget -q https://github.com/rordenlab/dcm2niix/releases/latest/download/dcm2niix_lnx.zip \
    && unzip dcm2niix_lnx.zip -d /usr/local/bin \
    && rm dcm2niix_lnx.zip \
    && chmod +x /usr/local/bin/dcm2niix

# ============================================================
# Install FSL (needed by some MRI tools)
# (light install, no GUI)
# ============================================================
RUN wget -q https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py \
    && python fslinstaller.py -d /opt/fsl -V 6.0.6 \
    && rm fslinstaller.py

ENV FSLDIR=/opt/fsl
ENV PATH=${FSLDIR}/bin:$PATH

# ============================================================
# Python dependencies
# ============================================================
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt

# ============================================================
# Install HD-BET (brain extraction)
# ============================================================
RUN pip install hd-bet \
    && hd-bet --help || true

# ============================================================
# Working directory
# ============================================================
WORKDIR /app

# ============================================================
# Copy project files
# ============================================================
COPY . /app

# ============================================================
# Default command
# ============================================================
ENTRYPOINT ["python", "mrc2.py"]
