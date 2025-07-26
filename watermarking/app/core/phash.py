from PIL import Image
import imagehash

def compute_phash(image_path: str) -> str:
    image = Image.open(image_path)
    phash = imagehash.phash(image)
    return str(phash) 