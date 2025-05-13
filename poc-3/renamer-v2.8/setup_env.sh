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
    tqdm \
    uvicorn

pip install pymupdf

pip install paddleocr
python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR()"

pip install numpy==1.24.4 scipy==1.10.1    

conda install -c conda-forge faiss-cpu
onda install -c conda-forge numpy=1.24.4
conda install -c conda-forge pytorch
conda install -c tqdm  

pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0

pip install paddleocr==2.6.1.1
# pip install paddlepaddle==2.4.2 -f https://www.paddlepaddle.org.cn/whl/linux/mavl.html
pip install paddlepaddle==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/mavl.html

pip install torch torchvision torchaudio sentence-transformers

conda install -c conda-forge opencv

echo "[*] Activating env"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

echo "[✓] Environment '$ENV_NAME' is ready."
conda activate xenex