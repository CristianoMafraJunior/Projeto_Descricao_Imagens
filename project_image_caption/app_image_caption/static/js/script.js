class Camera {
    constructor(videoElement) {
        this.video = videoElement;
    }

    start() {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then((stream) => {
                this.video.srcObject = stream;
                this.video.onloadedmetadata = () => {
                    this.video.play();
                };
            })
            .catch((err) => {
                console.log('Erro ao acessar a webcam ou câmera: ', err);
            });
    }

    stop() {
        const stream = this.video.srcObject;
        const tracks = stream.getTracks();

        tracks.forEach((track) => {
            track.stop();
        });

        this.video.srcObject = null;
    }

    takePhoto() {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        context.drawImage(this.video, 0, 0, canvas.width, canvas.height);

        const imageDataURL = canvas.toDataURL('image/png');
        return imageDataURL;
    }
}

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
    const video = document.getElementById('video');
    const loadImageBtn = document.getElementById('loadImageBtn');
    const takePhotoBtn = document.getElementById('takePhotoBtn');
    const startWebcamBtn = document.getElementById('startWebcamBtn');
    const fileInput = document.getElementById('fileInput');
    const imagePreview = document.getElementById('imagePreview');

    const camera = new Camera(video);
    const imageLoader = new ImageLoader(fileInput, imagePreview);

    startWebcamBtn.addEventListener('click', function() {
        camera.start();
    });

    takePhotoBtn.addEventListener('click', function() {
        const imageDataURL = camera.takePhoto();
        imageLoader.showImagePreview(imageDataURL);
        camera.stop();
    });

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

    camera.start();
});
