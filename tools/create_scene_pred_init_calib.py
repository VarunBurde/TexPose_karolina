import os
import argparse
import cv2
import json

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, required=True)
parser.add_argument('--object_id', type=str, required=True)
# parser.add_argument('--output_dir', type=str, required=True)

scene_pred_info = {}
scene_pred_init_calib = {}

if __name__ == '__main__':
    args = parser.parse_args()
    input_dir = args.input_dir

    scene_gt_info_json = os.path.join(input_dir, "scene_gt_info.json")
    scene_gt_info = json.load(open(scene_gt_info_json, 'r'))

    scene_gt_json = os.path.join(input_dir, "scene_gt.json")
    scene_gt = json.load(open(scene_gt_json, 'r'))

    for image_id in scene_gt.keys():
        for object_ind in range(len(scene_gt[image_id])):
            object_id = scene_gt[image_id][object_ind]['obj_id']
            if str(object_id) == str(args.object_id):
                scene_pred_info[image_id] = [scene_gt_info[image_id][object_ind]]
                scene_pred_init_calib[image_id] = [scene_gt[image_id][object_ind]]

    scene_pred_info_json = os.path.join(input_dir, "scene_pred_info.json")
    with open(scene_pred_info_json, 'w') as f:
        json.dump(scene_pred_info, f, indent=4)

    scene_pred_init_calib_json = os.path.join(input_dir, "scene_pred_init_calib.json")
    with open(scene_pred_init_calib_json, 'w') as f:
        json.dump(scene_pred_init_calib, f, indent=4)