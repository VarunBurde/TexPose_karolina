#!/bin/bash

module purge
source /apps/all/Anaconda3/2023.09-0/etc/profile.d/conda.sh

module load CUDA
module load libglvnd/1.3.3-GCCcore-11.2.0
module load CMake/3.22.1-GCCcore-11.2.0
module load libGLU/9.0.2-GCCcore-11.2.0
module load Mesa/21.1.7-GCCcore-11.2.0
module load GLib/2.69.1-GCCcore-11.2.0
module load Python/3.9.6-GCCcore-11.2.0

conda activate texpose
