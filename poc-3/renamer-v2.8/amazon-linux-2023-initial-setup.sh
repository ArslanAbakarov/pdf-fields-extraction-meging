dnf install -y iproute
dnf install -y unzip
dnf install -y mc
dnf install -y nano
dnf install -y wget
dnf install -y git
dnf install python3.12
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# bash Miniconda3-latest-Linux-x86_64.sh
curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
bash Miniforge3-Linux-aarch64.sh
conda install -c conda-forge numpy=1.24.4
conda install -c conda-forge pytorch