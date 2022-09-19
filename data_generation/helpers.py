import warnings
warnings.filterwarnings("ignore")

import logging
import os
import shutil

import pandas as pd

import config

def check_manual_setup() -> bool:
    """
        Check that the files and folders that need to be manually set up before the rest of the script is executed are good to go.
        If all files exist, makes sure folder structure is correct.
    """

    if not os.path.exists(config.ROOT):
        logging.error("Your data folder doesn't exist! Make sure to create a folder and set the location in the config file.")
        return False

    logging.info("  Looking for CLD data file...")
    if os.path.exists(config.data_file_locations["cld"]) or os.path.exists(config.data_file_locations["cld_processed"]):
        logging.info("    CLD folder structure OK!")
    elif os.path.exists(f"{config.ROOT}/{config.original_data_file_names['cld']}"):
        os.rename(f"{config.ROOT}/{config.original_data_file_names['cld']}", config.data_file_locations['cld'])
        logging.info(f"    CLD file {config.original_data_file_names['cld']} renamed to {config.data_file_locations['cld'].split('/')[-1]}")
        logging.info("    CLD file OK!")
    else:
        logging.error(f"    Correct CLD file not found. Download {config.original_data_file_names['cld']} from the CLD website and paste it into {config.ROOT}.")
        return False

    logging.info("  Looking for CASIA Handwritten Simplified Character dataset...")
    if os.path.exists(config.data_file_locations["casia_raw"]):
        logging.info("    CASIA folder structure OK!")
    elif os.path.exists(f"{config.ROOT}/{config.original_data_file_names['casia']}"):
        if not os.path.exists(config.IMAGES_LOCATION):
            os.mkdir(config.IMAGES_LOCATION)
        os.mkdir(config.data_file_locations["casia_raw"])
        for folder in os.listdir(f"{config.ROOT}/{config.original_data_file_names['casia']}"):
            os.rename(f"{config.ROOT}/{config.original_data_file_names['casia']}/{folder}", f"{config.data_file_locations['casia_raw']}/{folder}")
        shutil.rmtree(f"{config.ROOT}/{config.original_data_file_names['casia']}")
        logging.info(f"    CASIA folder {config.original_data_file_names['casia']} renamed to {config.data_file_locations['casia_raw'].split('/')[-1]}")
        logging.info("    CASIA folder structure OK!")
    else:
        logging.error(f"    Correct CASIA folder not found. Download {config.original_data_file_names['casia']} from the kaggle link specified in README.md and paste it into {config.ROOT}.")
        return False

    logging.info("  Looking for Handwritten Traditional Character dataset...")
    if os.path.exists(config.data_file_locations["traditional_raw"]):
        logging.info("    Handwritten Traditional folder structure OK!")
    elif os.path.exists(f"{config.ROOT}/{config.original_data_file_names['traditional']}"):
        os.mkdir(config.data_file_locations["traditional_raw"])
        characters = set()
        for folder in os.listdir(f"{config.ROOT}/{config.original_data_file_names['traditional']}"):
            images = os.listdir(f"{config.ROOT}/{config.original_data_file_names['traditional']}/{folder}")
            character = images[0][0]
            if character not in characters:
                os.mkdir(f"{config.data_file_locations['traditional_raw']}/{character}")
                characters.add(character)
            for image in images:
                os.rename(f"{config.ROOT}/{config.original_data_file_names['traditional']}/{folder}/{image}", f"{config.data_file_locations['traditional_raw']}/{character}/{image[2:]}")

        shutil.rmtree(f"{config.ROOT}/{config.original_data_file_names['traditional']}")
        logging.info(f"    Traditional Handwritten Character folder {config.original_data_file_names['traditional']} restructured and renamed to {config.data_file_locations['traditional_raw']}")
        logging.info("    Handwritten Traditional folder structure OK!")
    else:
        logging.error(f"    Correct Handwritten Traditional Character folder not found. Download {config.original_data_file_names['traditional']} from the GitHub link specified in README.md and paste it into {config.ROOT}.")
        return False

    logging.info("  Looking for CCD txt file...")
    if os.path.exists(config.data_file_locations["ccd_raw"]):
        logging.info("    CCD txt file OK!")
    else:
        logging.error("    Couldn't find CCD txt file :(")
        return False

    logging.info("Checking dataset sizes...")

    if os.path.exists(config.data_file_locations["cld_processed"]):
        cld_set = "cld_processed"
    else:
        cld_set = "cld"
    cld = pd.read_csv(config.data_file_locations[cld_set])
    if cld.shape[0] < config.dataset_min_size[cld_set]:
        logging.error(f"  CLD contains {cld.shape[0]} rows of character/word data but at least { config.dataset_min_size[cld_set]} rows were expected.")
        return False
    else:
        logging.info(f"  CLD contains {cld.shape[0]} rows of character/word data. At least { config.dataset_min_size[cld_set]} rows were expected.")

    for dataset in ("CASIA", "Traditional"):
        num_characters = len(os.listdir(config.data_file_locations[f"{dataset.lower()}_raw"]))
        num_images = sum([len(files) for _, _, files in os.walk(config.data_file_locations[f"{dataset.lower()}_raw"])])
        min_chars = config.dataset_min_size[f"{dataset.lower()}_chars"]
        min_images = config.dataset_min_size[f"{dataset.lower()}_images"]
        if num_characters < min_chars or num_images < min_images:
            logging.error(f"  {dataset} contains {num_characters} characters and {num_images} image files, but at least {min_chars} characters and {min_images} images were expected.")
            return False
        else:
            logging.info(f"  {dataset} Handwritten image dataset contains {num_characters} characters and {num_images} image files. At least {min_chars} characters and {min_images} images were expected.")

    return True