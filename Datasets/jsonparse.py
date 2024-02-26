import json
from collections import defaultdict


def convert():
    f = open("/Users/anthonyzheng/Desktop/datasets/labels.json", "r")
    s = f.read()
    j = json.loads(s)
    csv_arr = {}
    for image in j["images"]:
        csv_arr[image["id"]] = [image["file_name"], image["width"], image["height"]]
    annotations = defaultdict(set)
    for annotation in j["annotations"]:
        bbox = annotation["bbox"]
        image_w = csv_arr[annotation["image_id"]][1]
        image_h = csv_arr[annotation["image_id"]][2]
        annotations[annotation["image_id"]].add((max(0.0, bbox[0] / image_w),  # x min
                                                 max(0.0, bbox[1] / image_h),  # y min
                                                 min(1.0, (bbox[0] + bbox[2]) / image_w),  # x max
                                                 min(1.0, (bbox[1] + bbox[3]) / image_h)))
    new = open("labels200local.csv", "w")
    count = 0
    split = 'TRAIN'
    for image_id, annotation_set in annotations.items():
        if count == 175:
            split = 'VALIDATION'
        elif count == 200:
            split = 'TEST'
        if count == 225:
            break
        for annotation in annotation_set:
            new.write(str(split) +
                      ",/Users/anthonyzheng/Desktop/datasets/data/" +
                      str(csv_arr[image_id][0]) + ",Head," +
                      str(annotation[0])[:5] + "," +
                      str(annotation[1])[:5] + ",,," +
                      str(annotation[2])[:5] + "," +
                      str(annotation[3])[:5] + ",,\n")
        count += 1
    new.close()
    f.close()


convert()
