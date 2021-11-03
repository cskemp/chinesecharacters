import config
import image_helpers

import os
import logging

from multiprocessing import Pool

import pandas as pd

def generate_descriptive_dataset():
    """Copy median complexity imageas to a new folder for us to calculate descriptive complexity"""

    complexities = pd.read_csv(config.data_file_locations["all_complexities"], index_col=0)
    complexities = complexities[complexities["scale_method"] == "pad"].reset_index(drop=True)

    cld = pd.read_csv(config.data_file_locations["cld_processed"], index_col=0)
    cld_characters = set(cld["Character"])
    complexities = complexities[(complexities["rendered_character"].isin(cld_characters)) | (complexities["simplified_character"].isin(cld_characters))]

    rows = []
    for _, ddf in complexities.groupby("dataset"):
        for _, cdf in ddf.groupby("rendered_character"):
            df = cdf.sort_values(by="perimetric_complexity")
            row = tuple(df.iloc[int(df.shape[0]/2)].values)
            rows.append(row)

    descriptive_df = pd.DataFrame(rows, columns=complexities.columns)
    copy_rows = []
    for _, row in descriptive_df.iterrows():
        dataset = row['dataset']
        rendered_character = row['rendered_character']
        period = row['period']
        image_id = row['image_ID']
        image_path = f"{config.IMAGES_LOCATION}/{dataset}_padded_lee/{rendered_character}_{period}_{image_id}.png"

        # Correct errors in traditional dataset
        if dataset == "traditional":
            if rendered_character == "幕":
                image_path = f"{config.IMAGES_LOCATION}/{dataset}_padded_lee/p_{period}_{image_id}.png"
            elif rendered_character == "嶒":
                image_path = f"{config.IMAGES_LOCATION}/{dataset}_padded_lee/p_{period}__{image_id}.png"
            elif rendered_character == "濈":
                image_path = f"{config.IMAGES_LOCATION}/{dataset}_padded_lee/濈_{period}__{image_id}.png"

        if dataset in config.FONT_DATASETS and period != "Simplified":
            image_path = f"{config.IMAGES_LOCATION}/{dataset}_padded_lee/{rendered_character}_Simplified_{image_id}.png"

        copy_rows.append((image_path, config.data_file_locations["descriptive_images"], rendered_character, period, image_id, dataset))

    if not os.path.exists(config.data_file_locations["descriptive_images"]):
        os.mkdir(config.data_file_locations["descriptive_images"])

    pool = Pool(os.cpu_count())
    pool.starmap(image_helpers.copy_image, copy_rows)
    pool.close()
    pool.join()

    for ds in config.FONT_DATASETS + config.HANDWRITTEN_DATASETS:
        logging.info(f"  Copied {descriptive_df[descriptive_df['dataset'] == ds].shape[0]} skeletons over for descriptive complexity analysis for {ds} dataset.")

