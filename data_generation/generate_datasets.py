import logging

import helpers
import image_dataset
import complexity_dataset
import distinctiveness_dataset
import descriptiveness_dataset
import zdic_dataset

logging.getLogger().setLevel(logging.INFO)

def main():
    """ 
        Generate image datasets and complexity dataframes for analysis.
    """
        
    logging.info("Checking/creating data folder structure...")
    manual_setup = helpers.check_manual_setup()
    assert manual_setup, "Setup failed :("
    logging.info("All data files and folder structures OK!")

    logging.info("Checking remaining data...")
    data_scraping = image_dataset.generate_data()
    assert data_scraping, "Data generation failed :("
    logging.info("All image data OK!")

    logging.info("Preprocessing all image data...")
    preprocessing = image_dataset.process_image_data()
    assert preprocessing, "Image preprocessing failed :("
    logging.info("Image preprocessing OK!")

    logging.info("Calculating image complexities...")
    complexity_dataset.generate_dataframes()

    logging.info("Cleaning image complexity dataframes...")
    complexity_dataset.postprocess_dataframes()
    logging.info("All image complexity dataframes OK!")

    logging.info("Generating image dataset for distinctiveness analysis...")
    distinctiveness_dataset.generate_distinctiveness_dataset()
    logging.info("Distinctiveness image dataset OK!")

    logging.info("Generating image dataset for descriptive complexity analysis...")
    descriptiveness_dataset.generate_descriptive_dataset()
    logging.info("Descriptive complexity data OK!")

    logging.info("Generating stroke gif complexities from ZDIC...")
    zdic_dataset.get_stroke_gif_complexities()
    logging.info("Stroke gif complexities OK!")

if __name__ == "__main__":
    main()