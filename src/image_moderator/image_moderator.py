import cv2
from ultralytics import YOLO

def moderate_images(image_paths, model_path, output_dir):
    model = YOLO(model_path)
    detections = []

    for image_path in image_paths:
        image = cv2.imread(image_path)
        if image is None:
            continue

        results = model.predict(source=image_path)
        annotated = image.copy()

        for result in results:
            for box in result.boxes.xyxy:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 255, 255), -1)

                detections.append({
                    "type": "image",
                    "category": "license_plate",
                    "image": image_path
                })

        if detections:
            import os
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, "covered_" + image_path.split("\\")[-1])
            cv2.imwrite(out_path, annotated)
            # Добавим путь к покрытому файлу в последний detection для этого изображения
            detections[-1]["output_path"] = out_path

    return detections
