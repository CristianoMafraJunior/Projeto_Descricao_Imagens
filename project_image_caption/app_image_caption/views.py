import os

from django.conf import settings
from django.shortcuts import render
from googletrans import Translator
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor
from ultralytics import YOLO

from .forms import UploadImageForm


class ImageCaptioner:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)
        self.translator = Translator()

    def generate_caption(self, image_path):
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        out = self.model.generate(**inputs)
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption

    def translate_caption(self, caption, dest_language="pt"):
        try:
            translated = self.translator.translate(caption, dest=dest_language)
            return translated.text
        except Exception:
            return caption


class ImageUploader:
    def __init__(self, image):
        self.image = image
        self.image_path = os.path.join(settings.MEDIA_ROOT, image.name)
        self.output_image_path = os.path.join(
            settings.MEDIA_ROOT, "output_" + image.name
        )
        self.model = YOLO("yolov8n.pt")
        self.captioner = ImageCaptioner()

        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

    def _save_image(self):
        try:
            with open(self.image_path, "wb+") as destination:
                for chunk in self.image.chunks():
                    destination.write(chunk)
        except Exception:
            pass

    def process_image(self):
        self._save_image()
        caption = self.captioner.generate_caption(self.image_path)
        translated_caption = self.captioner.translate_caption(caption)
        return translated_caption


def upload_image(request):
    if request.method == "POST":
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            uploader = ImageUploader(image)
            caption = uploader.process_image()
            context = {
                "form": form,
                "uploaded_image_url": settings.MEDIA_URL + image.name,
                "description": caption,
            }
            return render(request, "home/home.html", context)
    else:
        form = UploadImageForm()
    return render(request, "home/home.html", {"form": form})
