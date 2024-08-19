import os

import matplotlib.pyplot as plt
from django.conf import settings
from django.shortcuts import render
from gluoncv import data, model_zoo, utils
from googletrans import Translator

from .forms import UploadImageForm


class ImageUploader:
    def __init__(self, image):
        self.image = image
        self.image_path = os.path.join(settings.MEDIA_ROOT, image.name)
        self.output_image_path = os.path.join(
            settings.MEDIA_ROOT, "output_" + image.name
        )
        self.net = model_zoo.get_model("ssd_512_resnet50_v1_voc", pretrained=True)
        self.form = UploadImageForm()

        # Ensure the media directory exists
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

    def _save_image(self):
        try:
            with open(self.image_path, "wb+") as destination:
                for chunk in self.image.chunks():
                    destination.write(chunk)
        except Exception as e:
            print(f"Error saving image: {e}")

    def _detect_classes(self):
        try:
            # Adjust image size if necessary
            x, img = data.transforms.presets.ssd.load_test(self.image_path, short=800)
            class_IDs, scores, bounding_boxs = self.net(x)

            # Adjust confidence threshold
            confidence_threshold = 0.5
            detected_classes = [
                self.net.classes[int(cls_id.asscalar())]
                for i, cls_id in enumerate(class_IDs[0])
                if scores[0][i].asscalar() > confidence_threshold
            ]
            return detected_classes, img, class_IDs, scores, bounding_boxs
        except Exception as e:
            print(f"Error detecting classes: {e}")
            return [], None, None, None, None

    def _remove_classes(self, classes):
        dict_remove = {
            "tvmonitor",
            "dog",
            "bird",
            "bottle",
            "diningtable",
            "motorbike",
            "pottedplant",
            "car",
            "sheep",
            "chair",
            "boat",
            "sofa",
            "horse",
        }
        return [cls for cls in classes if cls not in dict_remove]

    def _translate_classes(self, classes):
        translator = Translator()
        translated_classes = []
        for cls in classes:
            try:
                translated_text = translator.translate(cls, dest="pt").text
                if translated_text:
                    translated_classes.append(translated_text)
                else:
                    translated_classes.append(
                        cls
                    )  # Fallback to original class if translation fails
            except Exception as e:
                print(f"Error translating class '{cls}': {e}")
                translated_classes.append(
                    cls
                )  # Fallback to original class if translation fails
        return translated_classes

    def _save_detected_image(self, img, class_IDs, scores, bounding_boxs):
        try:
            utils.viz.plot_bbox(
                img,
                bounding_boxs[0],
                scores[0],
                class_IDs[0],
                class_names=self.net.classes,
            )
            plt.savefig(self.output_image_path)
        finally:
            plt.close()

    def process_image(self):
        self._save_image()
        detected_classes, img, class_IDs, scores, bounding_boxs = self._detect_classes()
        if img is None:
            return []  # Handle error or provide a default response

        detected_classes = self._remove_classes(detected_classes)
        detected_classes = list(set(detected_classes))
        detected_classes_pt = self._translate_classes(detected_classes)
        self._save_detected_image(img, class_IDs, scores, bounding_boxs)
        return detected_classes_pt


def upload_image(request):
    if request.method == "POST":
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            uploader = ImageUploader(image)
            detected_classes_pt = uploader.process_image()
            print("Detected objects:", detected_classes_pt)  # Debugging
            context = {
                "form": form,
                "uploaded_image_url": settings.MEDIA_URL + image.name,
                "output_image_url": settings.MEDIA_URL + "output_" + image.name,
                "detected_classes": detected_classes_pt,
            }
            return render(request, "home/home.html", context)
    else:
        form = UploadImageForm()
    return render(request, "home/home.html", {"form": form})
