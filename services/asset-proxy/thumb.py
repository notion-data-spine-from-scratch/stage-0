import sys
from PIL import Image

if __name__ == "__main__":
    path = sys.argv[1]
    out = sys.argv[2]
    with Image.open(path) as img:
        img.thumbnail((320, 320))
        img.save(out)
