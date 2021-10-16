from perimetric_complexity import perimetricComplexity
from multiprocessing import Pool
from typing import Tuple

import pandas as pd

import config
import os
import logging

def get_image_complexity(image_path: str) -> Tuple[str, float, float]:
    perimetric, pixel = perimetricComplexity(image_path)
    return image_path, perimetric, pixel

def generate_dataframes(limit_dataset: str) -> None:

    logging.info("  Generating image complexity dataframes...")
    measure_complexity(limit_dataset)

    measure_discriminability()

    return

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

                    pool = Pool(os.cpu_count())
                    complexities = pool.map(get_image_complexity, image_paths)
                    pool. ose()
                    pool.join()

                    df = pd.DataFrame(complexities, columns=["image_path", "perimetric_complexity", "pixel_complexity"])
                    df.to_csv(complexity_dataset_path)

                else:
                    df = pd.read_csv(complexity_dataset_path, index_col=0)
                    logging.info(f"      Found {df.shape[0]} perimetric and pixel complexities for {'stretched' if stretch else 'padded'} {dataset} images.")

    #### Vector-based Descriptive Complexity

    #### Time-based Writing Complexity

    return

def measure_discriminability():
    return