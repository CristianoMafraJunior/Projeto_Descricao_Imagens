class ImageLoader {
    constructor(inputElement, previewElement) {
        this.input = inputElement;
        this.preview = previewElement;
    }

    loadImage() {
        this.input.click();
    }

    showImagePreview(url) {
        this.preview.src = url;
        this.preview.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const loadImageBtn = document.getElementById('loadImageBtn');
    const fileInput = document.getElementById('fileInput');
    const imagePreview = document.getElementById('imagePreview');

    const imageLoader = new ImageLoader(fileInput, imagePreview);

    loadImageBtn.addEventListener('click', function() {
        imageLoader.loadImage();
    });

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        const reader = new FileReader();

        reader.onload = function() {
            imageLoader.showImagePreview(reader.result);
        };

        reader.readAsDataURL(file);
    });
});
