#!/bin/bash

ENV_NAME="xenex"

echo "[*] Deleting old env if exists"
conda remove -n "$ENV_NAME" --all -y

echo "[*] Creating new env: $ENV_NAME"
conda create -n "$ENV_NAME" python=3.12 numpy=1.26 -y

echo "[*] Installing pip packages"
pip install \
    pymupdf \
    sentence-transformers \
    opencv-python-headless \
    pytesseract \
    rapidfuzz \
    tqdm

pip install pymupdf

pip install numpy==1.24.4 scipy==1.10.1    

conda install -c conda-forge faiss-cpu
onda install -c conda-forge numpy=1.24.4
conda install -c conda-forge pytorch
conda install -c tqdm  
pip install paddlepaddle -f https://www.paddlepaddle.org.cn/whl/linux/mavl.html


pip install torch torchvision torchaudio sentence-transformers

conda install -c conda-forge opencv

echo "[*] Activating env"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

echo "[✓] Environment '$ENV_NAME' is ready."
conda activate xenex