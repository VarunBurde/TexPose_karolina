import os
import csv
import json

YCB_data = {
    1: "002_master_chef_can", 2: "003_cracker_box", 3: "004_sugar_box", 4: "005_tomato_soup_can", 5: "006_mustard_bottle",
    6: "007_tuna_fish_can", 7: "008_pudding_box", 8: "009_gelatin_box", 9: "010_potted_meat_can", 10: "011_banana",
    11: "019_pitcher_base", 12: "021_bleach_cleanser", 13: "024_bowl", 14: "025_mug", 15: "035_power_drill",
    16: "036_wood_block", 17: "037_scissors", 18: "040_large_marker", 19: "051_large_clamp", 20: "052_extra_large_clamp",
    21: "061_foam_brick"
}

train_test_split = {}
scene_pred_init_calib = {}
scene_pred_info = {}
original_gt = {}
original_scene_gt_info = {}
object_scene_count = {}

if __name__ == '__main__':
    split_path = "/mnt/proj3/open-29-7/varun_ws/pose_estimator_ws/Texpose_self6d/TexPose_karolina/splits"
    split_name = "ycbv"
    csv_file = "/mnt/proj3/open-29-7/varun_ws/pose_estimator_ws/Texpose_self6d/TexPose_karolina/combine.csv"

    dataset_path = "/mnt/proj3/open-29-7/varun_ws/datasets/YCB-V/ycbv/test"

    ycbv_path = os.path.join(split_path, split_name)

    for key, value in YCB_data.items():
        train_test_split[value] = {'train': [], 'test': [], 'val': []}

    for dir in os.listdir(dataset_path):
        scene_id = dir
        scene_pred_init_calib[scene_id] = {}
        scene_pred_info[scene_id] = {}


    with open(csv_file, 'r') as file:
        # make reader and skip the header
        reader = csv.reader(file)
        next(reader)
        # iterate through the rows
        data_point = 0
        for row in reader:
            print("processing data point: ", data_point)
            scene_id = row[0]
            img_id = row[1]
            object_id = row[2]
            object_name = YCB_data[int(object_id)]

            # count the number of instances of the object in the scene
            if object_name in object_scene_count:
                if scene_id in object_scene_count[object_name]:
                    object_scene_count[object_name][scene_id] += 1
                else:
                    object_scene_count[object_name][scene_id] = 1
            else:
                object_scene_count[object_name] = {scene_id: 1}

            scene_path = os.path.join(dataset_path, str(scene_id).zfill(6))
            instance_data = object_name + " " + scene_path + " " + img_id
            train_test_split[object_name]['train'].append(instance_data)

            original_gt_json = os.path.join(dataset_path, str(scene_id).zfill(6), "scene_gt.json")
            orginal_gt = json.load(open(original_gt_json))

            original_scene_gt_info_json = os.path.join(dataset_path, str(scene_id).zfill(6), "scene_gt_info.json")
            orginal_scene_gt_info = json.load(open(original_scene_gt_info_json))

            # find index of the object in the scene_gt.json
            for index in range(len(orginal_gt[img_id])):
                if orginal_gt[img_id][index]["obj_id"] == int(object_id):
                    scene_pred_init_calib[str(scene_id).zfill(6)][img_id] = [orginal_gt[img_id][index]]
                    scene_pred_info[str(scene_id).zfill(6)][img_id] = [orginal_scene_gt_info[img_id][index]]

            data_point += 1

            # if data_point == 300:
            #     break

    print("saving the gt files ")
    for dir in os.listdir(dataset_path):
        scene_id = dir
        scene_id_dict =  scene_pred_init_calib[str(scene_id).zfill(6)]
        scene_pred_info_dict = scene_pred_info[str(scene_id).zfill(6)]

        scene_pred_init_calib_json = os.path.join(dataset_path, str(scene_id).zfill(6), "scene_pred_init_calib.json")
        with open(scene_pred_init_calib_json, 'w') as file:
            json.dump(scene_id_dict, file, indent=4)

        # create scene_pred_info.json
        scene_pred_info_json = os.path.join(dataset_path, str(scene_id).zfill(6), "scene_pred_info.json")
        with open(scene_pred_info_json, 'w') as file:
            json.dump(scene_pred_info_dict, file, indent=4)

    print("saving the object_scene_count")
    object_scene_count_json = os.path.join(ycbv_path, "object_scene_count.json")
    with open(object_scene_count_json, 'w') as file:
        json.dump(object_scene_count, file, indent=4)

    max_instances = {}
    for key, value in object_scene_count.items():
        max_count = 0
        max_instances[key] = 0
        for scene_id, count in value.items():
            if count > max_count:
                max_count = count
                max_instances[key] = scene_id

    # save the max_instances
    max_instances_json = os.path.join(ycbv_path, "max_instances.json")
    with open(max_instances_json, 'w') as file:
        json.dump(max_instances, file, indent=4)

    # create split of 10 percent to test and 90 percent to train
    for key, value in train_test_split.items():
        total_instances = len(value['train'])
        test_instances = int(0.1 * total_instances)
        value['test'] = value['train'][:test_instances]
        value['val'] = value['test']

    print("saving the split files")
    for key, value in train_test_split.items():
        instance_dir = os.path.join(ycbv_path, key)
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir)

        scene_all_dir = os.path.join(instance_dir, "scene_all")
        if not os.path.exists(scene_all_dir):
            os.makedirs(scene_all_dir)

        train_file = os.path.join(scene_all_dir, "train.txt")
        with open(train_file, 'w') as file:
            for instance in value['train']:
                # only save the scene with the maximum number of instances
                object_name = instance.split(" ")[0]
                scene_id = instance.split(" ")[1].split("/")[-1]
                if int(max_instances[object_name]) == int(scene_id):
                    file.write(instance + "\n")

        test_file = os.path.join(scene_all_dir, "test.txt")
        with open(test_file, 'w') as file:
            for instance in value['test']:
                object_name = instance.split(" ")[0]
                scene_id = instance.split(" ")[1].split("/")[-1]
                scene_id = int(scene_id)
                if int(max_instances[object_name]) == int(scene_id):
                    file.write(instance + "\n")

        val_file = os.path.join(scene_all_dir, "val.txt")
        with open(val_file, 'w') as file:
            for instance in value['test']:
                object_name = instance.split(" ")[0]
                scene_id = instance.split(" ")[1].split("/")[-1]
                scene_id = int(scene_id)
                if int(max_instances[object_name]) == int(scene_id):
                    file.write(instance + "\n")