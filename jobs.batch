#!/usr/bin/bash
#SBATCH --job-name=Texpose_training
#SBATCH --account OPEN-29-7
#SBATCH --time=20:00:00
#SBATCH --partition=qgpu
#SBATCH --error=errors/002_master_chef_can.out
#SBATCH --output=logs/002_master_chef_can.err
#SBATCH --mail-user=varun.burde@cvut.cz
#SBATCH --mail-type=FAIL

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

cd /mnt/proj3/open-29-7/varun_ws/pose_estimator_ws/Texpose_self6d/TexPose_karolina

python3 compute_box.py --pred_loop init_calib --generate_pred --save_predbox --target_folder /mnt/proj3/open-29-7/varun_ws/datasets/YCB-V/ycbv/test/000051 --dataset=ycbv --root=/mnt/proj3/open-29-7/varun_ws/datasets/YCB-V/ --object_id 1


python3 compute_surfelinfo.py --model=nerf_adapt_st_gan --yaml=nerf_ycbv_adapt_gan --data.pose_source=predicted --data.pose_loop=init_calib --gan= --loss_weight.feat=  --batch_size=1 --data.root=/mnt/proj3/open-29-7/varun_ws/datasets/YCB-V/ --data.dataset=ycbv --render.geo_save_dir=/mnt/proj3/open-29-7/varun_ws/datasets/YCB-V/ycbv/test/000051  --data.name=002_master_chef_can


python3 train.py --model=nerf_adapt_st_gan --yaml=nerf_ycbv_adapt_gan --data.pose_source=predicted --data.preload=true --data.scene=scene_all  --data.name=002_master_chef_can

python3 evaluate.py --model=nerf_adapt_st_gan --yaml=nerf_ycbv_adapt_gan --batch_size=1 --data.preload=false --data.scene=scene_syn2real_layer --name=002_master_chef_can --data.image_size=[480,640] --resume --syn2real --render.save_path=render_test
