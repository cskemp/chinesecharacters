import logging
import click

from helpers import check_manual_setup
from generate_images import generate_data
from preprocess_images import preprocess_image_data
from generate_dataframes import generate_dataframes
from postprocess_dataframes import postprocess_dataframes
from distinctiveness_dataset import generate_distinctiveness_dataset, calculate_distinctiveness, calculate_persistent_stream_distinctiveness, calculate_distinctiveness_dataset_complexities
from descriptiveness_dataset import generate_descriptive_dataset
from generate_zdic_dataframes import get_stroke_gif_complexities

logging.getLogger().setLevel(logging.INFO)

@click.command()
@click.option('--preprocess', default=True, help='Whether or not to preprocess images before calculating complexity')
@click.option('--calculate-complexity', default=True, help='Whether or not to (re?)generate complexity dataframes')
@click.option('--limit-dataset', default=None, help='Limit preprocessing and complexity calculating to images of a single dataset')
@click.option('--generate-distinctiveness-data', default=True, help='Generate datasets for distinctiveness analysis')
@click.option('--calculate-character-distinctiveness', default=True, help='Calculate the distinctiveness of individual characters')
@click.option('--generate-descriptive-data', default=True, help='Copy median complexity images over to a new folder for calculating descriptive complexity')
def main(
    preprocess: bool,
    calculate_complexity: bool,
    limit_dataset: str,
    generate_distinctiveness_data: bool,
    calculate_character_distinctiveness: bool,
    generate_descriptive_data: bool,
    ):
    """ 
        Generate image datasets and complexity dataframes for analysis.
    """

    logging.info("Checking/creating data folder structure...")
    manual_setup = check_manual_setup()
    assert manual_setup, "Setup failed :("
    logging.info("All data files and folder structures OK!")

    logging.info("Checking remaining data...")
    data_scraping = generate_data(limit_dataset)
    assert data_scraping, "Data generation failed :("
    logging.info("All image data OK!")

    if preprocess:
        logging.info("Preprocessing all image data...")
        preprocessing = preprocess_image_data(limit_dataset)
        assert preprocessing, "Image preprocessing failed :("
        logging.info("Image preprocessing OK!")

    if calculate_complexity:
        logging.info("Calculating image complexities...")
        generate_dataframes(limit_dataset)

        logging.info("Cleaning image complexity dataframes...")
        postprocess_dataframes()
        logging.info("All image complexity dataframes OK!")

    if generate_distinctiveness_data:
        logging.info("Generating image dataset for distinctiveness analysis...")
        generate_distinctiveness_dataset()
        logging.info("Distinctiveness image dataset OK!")

    if calculate_character_distinctiveness:
        logging.info("Calculating distinctiveness data...")
        calculate_distinctiveness()
        calculate_persistent_stream_distinctiveness()
        calculate_distinctiveness_dataset_complexities()
        logging.info("Distinctiveness data OK!")

    if generate_descriptive_data:
        logging.info("Generating image dataset for descriptive complexity analysis...")
        generate_descriptive_dataset()
        logging.info("Descriptive complexity data OK!")

    logging.info("Generating stroke gif complexities from ZDIC...")
    get_stroke_gif_complexities()
    logging.info("Stroke gif complexities OK!")

if __name__ == "__main__":
    main()