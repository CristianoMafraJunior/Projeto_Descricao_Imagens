import os

import matplotlib.pyplot as plt
from django.conf import settings
from django.shortcuts import render
from gluoncv import data, model_zoo, utils

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

    def _save_image(self):
        with open(self.image_path, "wb+") as destination:
            for chunk in self.image.chunks():
                destination.write(chunk)

    def _detect_classes(self):
        x, img = data.transforms.presets.ssd.load_test(self.image_path, short=724)
        class_IDs, scores, bounding_boxs = self.net(x)
        detected_classes = [
            self.net.classes[int(cls_id.asscalar())] for cls_id in class_IDs[0]
        ]
        return detected_classes, img, class_IDs, scores, bounding_boxs

    # TODO - Remover esse metodo na proxima correção
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

    # TODO - Usar a Lib "googletrans" futuramente (Isso ta uma gambiarra)
    def _translate_classes(self, classes):
        translate_class_pt_br = {
            "person": "pessoa",
            "dog": "cachorro",
            "bicycle": "bicicleta",
            "horse": "cavalo",
        }
        return [translate_class_pt_br.get(cls, cls) for cls in classes]

    def _save_detected_image(self, img, class_IDs, scores, bounding_boxs):
        utils.viz.plot_bbox(
            img, bounding_boxs[0], scores[0], class_IDs[0], class_names=self.net.classes
        )
        plt.savefig(self.output_image_path)
        plt.close()

    def process_image(self):
        self._save_image()
        detected_classes, img, class_IDs, scores, bounding_boxs = self._detect_classes()
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
