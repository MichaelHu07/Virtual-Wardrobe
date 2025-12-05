import os
import requests
import logging

logger = logging.getLogger(__name__)

MODEL_URLS = {
    "pixie.ckpt": "https://github.com/YadiraF/PIXIE/releases/download/v1.0/pixie_model.ckpt", # Placeholder URL
    "pifuhd.pth": "https://dl.fbaipublicfiles.com/pifuhd/pifuhd.pt", # Official PIFuHD weights
    # "classifier.onnx": "..." 
}

WEIGHTS_DIR = "./weights"

def download_weights():
    if not os.path.exists(WEIGHTS_DIR):
        os.makedirs(WEIGHTS_DIR)
        
    for filename, url in MODEL_URLS.items():
        path = os.path.join(WEIGHTS_DIR, filename)
        if os.path.exists(path):
            logger.info(f"Model {filename} already exists.")
            continue
            
        logger.info(f"Downloading {filename} from {url}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Downloaded {filename}.")
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_weights()

