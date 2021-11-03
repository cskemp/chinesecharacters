import os
from PIL import Image
import pandas as pd

ROOT = "descriptive_images"

if __name__ == "__main__":

    rows = []
    c = 0
    for t in os.listdir(ROOT):

        img = Image.open(f"{ROOT}/{t}")
        img = img.convert("L")
        img.save("t.bmp")

        os.system(f"potrace t.bmp -b svg")

        character, period, iid, dataset = t.split(".")[0].split("_")

        with open("t.svg", 'r') as r:
            rows.append((character, period, iid, dataset, len(r.read())))

        if c % 250 == 0:
            print(c)
        c += 1

    df = pd.DataFrame(rows, columns=["rendered_character", "period", "image_ID", "dataset", "SVG description length"])
    df.to_csv("descriptive_complexities.csv")
        