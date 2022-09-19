from typing import Tuple

import pandas as pd

import config
import os
import logging
import opencc
import multiprocessing
import image_helpers


def generate_dataframes(limit_dataset: str) -> None:

    logging.info("  Generating image complexity dataframes...")
    measure_complexity(limit_dataset)

    return

def postprocess_dataframes():

    complexity_postprocessing()

    return


def get_image_complexity(image_path: str) -> Tuple[str, float, float]:
    perimetric, pixel = image_helpers.perimetric_complexity(image_path)
    return image_path, perimetric, pixel

def measure_complexity(limit_dataset: str):

    #### Perimetric and Pixel Complexity
    if not os.path.exists(config.COMPLEXITIES_LOCATION):
        os.mkdir(config.COMPLEXITIES_LOCATION)
    for stretch in (True, False):
        logging.info(f"    Generating perimetric and pixel complexity dataframes for {'stretched' if stretch else 'padded'} images...")
        for dataset in config.HANDWRITTEN_DATASETS + config.FONT_DATASETS:
            if not limit_dataset or dataset == limit_dataset:
                complexity_dataset_path = f"{config.COMPLEXITIES_LOCATION}/{dataset}_{'stretched' if stretch else 'padded'}_{config.SKELETONISE_METHOD}.csv"
                image_dataset_path = f"{config.IMAGES_LOCATION}/{dataset}_{'stretched' if stretch else 'padded'}_{config.SKELETONISE_METHOD}"
                image_paths = [f"{path}/{name}" for path, _, files in os.walk(image_dataset_path) for name in files]

                if not os.path.exists(complexity_dataset_path):

                    logging.info(f"      Generating perimetric and pixel complexities for {len(image_paths)} {'stretched' if stretch else 'padded'} {dataset} images...")

                    pool = multiprocessing.Pool(os.cpu_count())
                    complexities = pool.map(get_image_complexity, image_paths)
                    pool.close()
                    pool.join()

                    df = pd.DataFrame(complexities, columns=["image_path", "perimetric_complexity", "pixel_complexity"])
                    df.to_csv(complexity_dataset_path)

                else:
                    df = pd.read_csv(complexity_dataset_path, index_col=0)
                    logging.info(f"      Found {df.shape[0]} perimetric and pixel complexities for {'stretched' if stretch else 'padded'} {dataset} images.")

    return


def complexity_postprocessing():
    """Combine different CSV's into one csv"""
    logging.info("  Combining complexity csv's into one file...")
    combined_df = None
    first = True
    t2s = opencc.OpenCC('t2s.json')
    s2t = opencc.OpenCC('s2t.json')
    for stretch in (True, False):
        for dataset in config.HANDWRITTEN_DATASETS + config.FONT_DATASETS:
            complexity_dataset_path = f"{config.COMPLEXITIES_LOCATION}/{dataset}_{'stretched' if stretch else 'padded'}_{config.SKELETONISE_METHOD}.csv"
            df = pd.read_csv(complexity_dataset_path, index_col=0)
            
            # Add dataset, skeletonise method and stretch
            df["dataset"] = [dataset] * df.shape[0]
            df["scale_method"] = ["pad" if not stretch else "stretch"] * df.shape[0]
            df["skeletonise_method"] = [config.SKELETONISE_METHOD] * df.shape[0]

            # Break image path down into character, period and ID
            df["path_split"] = df["image_path"].apply(lambda x: x.split("/")[-1][:-4].split("_"))
            df["original_character"] = df["path_split"].apply(lambda x: x[0])
            df["period"] = df["path_split"].apply(lambda x: x[1])
            df["image_ID"] = df["path_split"].apply(lambda x: x[2])

            # Add simplified character column
            if dataset == "traditional":

                # Fix three errors that come from the original traditional dataset files
                # 幕 is listed as 'p'
                df["original_character"] = df["original_character"].apply(lambda x: "幕" if x == "p" else x)
                # 濈 is missing image IDs
                df_temp = df[df["original_character"] == "濈"].copy()
                df = df[df["original_character"] != "濈"]
                df_temp["image_ID"] = sorted(list(range(df_temp.shape[0])), key=lambda x: str(x))
                df = df.append(df_temp, ignore_index=True)
                # 嶒 is also listed as 'p' and has no image id
                df_p = df[(df["original_character"] == "幕") & (df["image_ID"] == "")].copy()
                df_p["original_character"] = ["嶒"] * df_p.shape[0]
                df_p["image_ID"] = sorted(list(range(df_p.shape[0])), key=lambda x: str(x))
                df = df[(df["original_character"] != "幕") | ~(df["image_ID"] == "")]
                df = df.append(df_p, ignore_index=True)

                df["simplified_character"] = [t2s.convert(c) for c in df["original_character"]]
                df["drop"] = [s2t.convert(row["simplified_character"]) != row["original_character"] for _, row in df.iterrows()]
                df = df[~df["drop"]]
            elif dataset in config.FONT_DATASETS:
                df["simplified_character"] = [t2s.convert(c) for c in df["original_character"]]
                df["period"] = ["Simplified" if row["simplified_character"] == row["original_character"] else "Traditional" for _, row in df.iterrows()]
                df["drop"] = [s2t.convert(row["simplified_character"]) != row["original_character"] if row["period"] == "Traditional" else False for _, row in df.iterrows()]
                df = df[~df["drop"]]

                traditional_simplified_characters = set(df[df["period"] == "Traditional"]["simplified_character"])
                df_traditional = df[(df["period"] == "Simplified") & ~(df["simplified_character"].isin(traditional_simplified_characters))].copy()
                df_traditional["period"] = ["Traditional"] * df_traditional.shape[0]
                df = df.append(df_traditional, ignore_index=True)
            else:
                df["simplified_character"] = df["original_character"]

            df = df[["original_character", "simplified_character", "period", "image_ID", "dataset", "scale_method", "skeletonise_method", "perimetric_complexity", "pixel_complexity"]]
            if first:   
                combined_df = df
                first = False
            else:
                combined_df = combined_df.append(df, ignore_index=True)
    
    logging.info(f"    Combined complexity dataframes into single file of with {combined_df.shape[0]} rows.")
    combined_df = combined_df.rename({"original_character":"rendered_character"}, axis=1)
    combined_df = combined_df[combined_df["period"].isin(config.PERIODS)].reset_index(drop=True)
    combined_df.to_csv(config.data_file_locations["all_complexities"])

    return
