import os
import json

ycbv_real_path = "/home/shared_data/datasets/YCBV/ycbv/train_real"

# object_scene_count = {}
# train_test_split = {}
#
# for img_dataset in os.listdir(ycbv_real_path):
#     object_scene_count[img_dataset] = {}
#     scene_gt_json = os.path.join(ycbv_real_path, img_dataset, "scene_gt.json")
#     scene_gt = json.load(open(scene_gt_json))
#     for image in scene_gt:
#         for object in range(len(scene_gt[image])):
#             object_id = scene_gt[image][object]["obj_id"]
#             if object_id not in object_scene_count[img_dataset]:
#                 object_scene_count[img_dataset][object_id] = 1
#             else:
#                 object_scene_count[img_dataset][object_id] += 1
#
# print("saving the object_scene_count")
# object_scene_count_json = os.path.join(ycbv_real_path, "object_scene_count.json")
# with open(object_scene_count_json, 'w') as file:
#     json.dump(object_scene_count, file, indent=4)
#
# # sort the object_scene_count based on the number of instances

object_scene_count_json = os.path.join(ycbv_real_path, "object_scene_count.json")
object_scene_count = json.load(open(object_scene_count_json))

sorted_object_scene_count = {}
for img_dataset in object_scene_count:
    for object_id in object_scene_count[img_dataset]:
        if object_id not in sorted_object_scene_count:
            sorted_object_scene_count[object_id] = {}
            if img_dataset not in sorted_object_scene_count[object_id]:
                sorted_object_scene_count[object_id][img_dataset] = object_scene_count[img_dataset][object_id]
        else:
            if img_dataset not in sorted_object_scene_count[object_id]:
                sorted_object_scene_count[object_id][img_dataset] = object_scene_count[img_dataset][object_id]

# sort the object_scene_count based on the number of instances
for object_id in sorted_object_scene_count:
    sorted_object_scene_count[object_id] = {k: v for k, v in sorted(sorted_object_scene_count[object_id].items(), key=lambda item: item[1], reverse=True)}


print("saving the sorted object_scene_count")
sorted_object_scene_count_json = os.path.join(ycbv_real_path, "sorted_object_scene_count.json")
with open(sorted_object_scene_count_json, 'w') as file:
    json.dump(sorted_object_scene_count, file, indent=4)

# # find maximum number of instance of an object in a scene
# max_instances = {}
# for object_id in sorted_object_scene_count:
#     max_count = 0
#     max_instances[object_id] = 0
#     for img_dataset in sorted_object_scene_count[object_id]:
#         if sorted_object_scene_count[object_id][img_dataset] > max_count:
#             max_count = sorted_object_scene_count[object_id][img_dataset]
#             max_instances[object_id] = img_dataset
#
# print("saving the max_instances")
# max_instances_json = os.path.join(ycbv_real_path, "max_instances.json")
# with open(max_instances_json, 'w') as file:
#     json.dump(max_instances, file, indent=4)

imges_dataset = os.listdir(ycbv_real_path)
max_instance = {}

for object_id in sorted_object_scene_count:
    max_instance[object_id] = ""
    for img_dataset in sorted_object_scene_count[object_id]:
        if str(img_dataset) in imges_dataset:
            imges_dataset.remove(str(img_dataset))
            max_instance[object_id] = str(img_dataset)
            break


print("saving the max_instances")
max_instances_json = os.path.join(ycbv_real_path, "max_instances_inid.json")
with open(max_instances_json, 'w') as file:
    json.dump(max_instance, file, indent=4)





