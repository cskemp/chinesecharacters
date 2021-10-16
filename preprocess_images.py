import os

import config
import logging

import numpy as np
import skimage.io as io

from skimage import img_as_ubyte
from multiprocessing import Pool
from typing import List

from image_helpers import (
    get_all_image_paths,
    copy_image,
    clean_image,
    crop_and_scale_image,
    rescale_and_skeletonise_image_variant,
)


def setup_folders(stretch: bool, limit_dataset: str) -> bool:
    """Set up processed image folders, including copying raw images over and cleaning"""

    logging.info(f"  Setting up folders for processed {'stretch' if stretch else 'padded'} data...")
    for dataset in config.HANDWRITTEN_DATASETS + config.FONT_DATASETS:
        if not limit_dataset or dataset == limit_dataset:
            processed_folder = f"{config.IMAGES_LOCATION}/{dataset}_{'stretched' if stretch else 'padded'}_{config.SKELETONISE_METHOD}"
            if not os.path.exists(processed_folder):
                os.mkdir(processed_folder)
                copy_images(config.data_file_locations[f"{dataset}_raw"], processed_folder, dataset)
    
    return True


def copy_images(from_folder: str, to_folder: str, dataset: str):
    """Copy all images from folder to folder"""
    images = get_all_image_paths(from_folder)
    logging.info(f"    Copying {len(images)} raw images into {to_folder}...")

    files = []
    from_folder = config.data_file_locations[f"{dataset}_raw"]
    if dataset == "hzy":

        for character in os.listdir(from_folder):
            for period in os.listdir(f"{from_folder}/{character}"):
                for img in os.listdir(f"{from_folder}/{character}/{period}"):
                    img_id = img[:-4]
                    file_path = f"{from_folder}/{character}/{period}/{img}"
                    files.append((file_path, to_folder, character, period, img_id))

    elif dataset in ("casia", "traditional"):

        if dataset == "casia":
            period = "Simplified"
        else:
            period = "Traditional"

        for character in os.listdir(from_folder):
            for img in os.listdir(f"{from_folder}/{character}"):
                img_id = img[:-4]
                file_path = f"{from_folder}/{character}/{img}"
                files.append((file_path, to_folder, character, period, img_id))

    else:
        # Font
        for img in os.listdir(from_folder):
            character = img[0]
            file_path = f"{from_folder}/{img}"
            files.append((file_path, to_folder, character, "Simplified", character))

    pool = Pool(os.cpu_count())
    pool.starmap(copy_image, files)
    pool.close()
    pool.join()


def clean_images(stretch: bool, limit_dataset: str):
    """Delete images that have no black pixels"""

    logging.info(f"  Cleaning {'stretched' if stretch else 'padded'} folders of empty .png's...")
    for dataset in config.HANDWRITTEN_DATASETS + config.FONT_DATASETS:
        if not limit_dataset or dataset == limit_dataset:
            processed_folder = f"{config.IMAGES_LOCATION}/{dataset}_{'stretched' if stretch else 'padded'}_{config.SKELETONISE_METHOD}"
            image_paths = get_all_image_paths(processed_folder)

            logging.info(f"    Cleaning {'stretched' if stretch else 'padded'} {dataset}...")

            pool = Pool(os.cpu_count())  
            deleted = pool.map(clean_image, image_paths)
            pool.close()
            pool.join()

            logging.info(f"      Cleaned {sum(deleted)} empty images from {processed_folder}!")


def process_image(image_path, stretch, skeletonise_method=config.SKELETONISE_METHOD, size=config.IMG_SIZE):
    """
    Universal image processing function:
    1. Binarise image
    2. Crop image to become square, scale to standardised dimensions
    3. Skeletonise image
    """
    
    image = img_as_ubyte(io.imread(image_path, as_gray=True))
    
    # Binarise image
    image = np.array([np.array([True if px != 255 else False for px in row]) for row in image])
    
    # Crop and scale image (stretching not allowed yet)
    image = crop_and_scale_image(image, False)
    
    # Scale image to standard size and skeletonise
    image = rescale_and_skeletonise_image_variant(image, size, stretch, skeletonise_method)
        
    io.imsave(image_path, img_as_ubyte(image))


def process_images(stretch: bool, limit_dataset: str):

    logging.info(f"  Preprocessing datasets with {'stretching' if stretch else 'padding'}...")
    for dataset in config.HANDWRITTEN_DATASETS + config.FONT_DATASETS:
        if not limit_dataset or dataset == limit_dataset:
            logging.info(f"    Preprocessing {'stretched' if stretch else 'padded'} {dataset}...")
            processed_folder = f"{config.IMAGES_LOCATION}/{dataset}_{'stretched' if stretch else 'padded'}_{config.SKELETONISE_METHOD}"

            image_paths = get_all_image_paths(processed_folder)
            image_paths = [i.replace("\\", "/") for i in image_paths]

            for b in range(0, len(image_paths), config.PREPROCESSING_BATCH_SIZE):
                logging.info(f"      Preprocessing batch {1 + b // config.PREPROCESSING_BATCH_SIZE}/{1 + len(image_paths) // config.PREPROCESSING_BATCH_SIZE}...")
                batch = image_paths[b : b + config.PREPROCESSING_BATCH_SIZE]
                pool = Pool(os.cpu_count())  
                pool.starmap(process_image, [(b, stretch) for b in batch])
                pool.close()
                pool.join()


def preprocess_image_data(limit_dataset: str) -> bool:
    """Preprocesses all image data"""

    for stretch in (True, False):

        setup = setup_folders(stretch, limit_dataset)
        assert setup, "Could not successfully copy raw images into preprocessed image folders!"

        clean_images(stretch, limit_dataset)

        process_images(stretch, limit_dataset)

    return True