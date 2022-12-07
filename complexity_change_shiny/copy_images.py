from PIL import Image, ImageOps
import pandas as pd
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import opencc


IMAGE_ROOT = "C:/Users/User/Downloads/hanzi_data_final/data/images"
s2t = opencc.OpenCC('s2t.json')

def process_and_save_image(file_path: str, save_path: str):
    
    # Open the image
    if file_path.endswith(".svg"):
        # If the image is an SVG, convert it to a PNG
        drawing = svg2rlg(file_path)
        renderPM.drawToFile(drawing, save_path, fmt="png", dpi=800)
        img = Image.open(save_path)
    else:
        # Otherwise, just open the image
        img = Image.open(file_path)

    img = ImageOps.invert(img)

    # Crop the image to its edge pixels
    img = img.crop(img.getbbox())

    # Calculate the width and height of the image
    width, height = img.size

    # Calculate the maximum dimension (width or height)
    max_dim = max(width, height)

    # Pad the image with a white background
    img = ImageOps.pad(img, (max_dim, max_dim), centering=(0.5, 0.5), color="black")

    # Scale the image to be 300 x 300 px
    img = img.resize((300, 300))

    img = ImageOps.invert(img)

    # Save the processed image to the specified location
    img.save(save_path)


if __name__ == "__main__":

    df = pd.read_csv("complexity_change.csv")

    missing = []
    for i, row in df.iterrows():
        print(i)

        character = row["character"]
        dataset = row["dataset"]
        image_id = row["image_ID"]
        period = row["period"]

        destpath = f"images_full/{character}_{period}_{image_id}_{dataset}.png"
        if dataset == "hzy":
            imagepath = f"{IMAGE_ROOT}/hanziyuan_raw/{character}/{period}/{image_id}.svg"
            process_and_save_image(imagepath, destpath)
        elif dataset == "casia":
            imagepath = f"{IMAGE_ROOT}/handwritten_simplified_raw/{character}/{image_id}.png"
            process_and_save_image(imagepath, destpath)
        elif dataset == "traditional":

            # This is some error in the original dataset
            if character == "幕":
                imagepath = f"{IMAGE_ROOT}/handwritten_traditional_raw/p/{image_id}.png"
                process_and_save_image(imagepath, destpath)
            else:
                try:
                    imagepath = f"{IMAGE_ROOT}/handwritten_traditional_raw/{s2t.convert(character)}/{image_id}.png"
                    process_and_save_image(imagepath, destpath)
                except:
                    imagepath = f"{IMAGE_ROOT}/handwritten_traditional_raw/{character}/{image_id}.png"
                    process_and_save_image(imagepath, destpath)
    
    missing_df = pd.DataFrame(missing, columns=["character", "dataset", "image_id", "period"])
    missing_df.to_csv("missing_images.csv")
        

        
