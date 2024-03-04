import fiftyone as fo
import fiftyone.zoo as foz

dataset = foz.load_zoo_dataset(
    "open-images-v6",
    split="validation",
    max_samples=1000,
    label_types=["detections"],
    classes=["Human head", "Human body"],
    only_matching=True,
)

dataset.export(
    export_dir="/Users/anthonyzheng/Desktop/datasets",
    dataset_type=fo.types.COCODetectionDataset,
    label_field="ground_truth",
)

session = fo.launch_app(dataset)
session.wait()
