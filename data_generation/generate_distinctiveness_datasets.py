import logging
import distinctiveness_dataset


def main():
    """ 
        Generate distinctiveness dataframes for analysis.
    """

    logging.info("Calculating distinctiveness data...")
    distinctiveness_dataset.calculate_distinctiveness()
    distinctiveness_dataset.calculate_persistent_stream_distinctiveness()
    distinctiveness_dataset.calculate_distinctiveness_dataset_complexities()
    logging.info("Distinctiveness data OK!")