#!/bin/bash

ENV_NAME="xenex"

echo "[*] Deleting old env if exists"
conda remove -n "$ENV_NAME" --all -y

echo "[*] Creating new env: $ENV_NAME"
conda create -n "$ENV_NAME" python=3.9 numpy=1.26 -y

echo "[*] Activating env"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

echo "[*] Installing Conda packages"
conda install -y -c conda-forge faiss-cpu

echo "[*] Installing pip packages"
pip install \
    pymupdf \
    sentence-transformers \
    opencv-python-headless \
    pytesseract \
    rapidfuzz \
    tqdm

echo "[✓] Environment '$ENV_NAME' is ready."
