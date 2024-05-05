class WebcamCamera {
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
                alert('Erro ao acessar a webcam ou câmera: ', err);
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

class WebcamImageLoader {
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
    const describeImageBtn = document.getElementById('describeImageBtn'); // Novo botão
    const fileInput = document.getElementById('fileInput');
    const imagePreview = document.getElementById('imagePreview');
    const imageDescription = document.getElementById('imageDescription');

    const webcamCamera = new WebcamCamera(video);
    const webcamImageLoader = new WebcamImageLoader(fileInput, imagePreview);

    startWebcamBtn.addEventListener('click', function() {
        webcamCamera.start();
    });

    takePhotoBtn.addEventListener('click', function() {
        const imageDataURL = webcamCamera.takePhoto();
        webcamImageLoader.showImagePreview(imageDataURL);
        webcamCamera.stop();
    });

    loadImageBtn.addEventListener('click', function() {
        webcamImageLoader.loadImage();
    });

    describeImageBtn.addEventListener('click', function() { // Nova funcionalidade para descrever a imagem
        const imageDataURL = webcamCamera.takePhoto();
        describeImage(imageDataURL);
    });

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        const reader = new FileReader();

        reader.onload = function() {
            webcamImageLoader.showImagePreview(reader.result);
        };

        reader.readAsDataURL(file);
    });

    webcamCamera.start(); // Inicie a webcam assim que a página for carregada
});

// Função para descrever a imagem
async function describeImage(imageDataURL) {
    // Adicione aqui a lógica para descrever a imagem usando o TensorFlow.js ou outra biblioteca de reconhecimento de imagens
    // Por enquanto, esta função apenas exibe uma mensagem de exemplo
    const description = "Este é o rosto de uma pessoa branca e calva sorrindo, com o fundo verde."; // Descrição de exemplo
    displayDescription(description);
}

// Função para exibir a descrição na interface do usuário
function displayDescription(description) {
    const imageDescription = document.getElementById('imageDescription');
    imageDescription.textContent = description;
}
