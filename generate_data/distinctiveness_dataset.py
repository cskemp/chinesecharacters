import logging
from math import dist
import config
import os
import logging

import image_helpers

import pandas as pd
import numpy as np

from multiprocessing import Pool
from sklearn.metrics.pairwise import euclidean_distances
from perimetric_complexity import perimetricComplexity

def generate_distinctiveness_dataset():
    """
    For each character in each period, picks out the median complexity image and copies to a new folder.
    """

    if os.path.exists(config.data_file_locations["distinctiveness_images"]):
        logging.info(f"  Found {len(os.listdir(config.data_file_locations['distinctiveness_images']))} images for distinctiveness analysis.")
    else:
        os.makedirs(config.data_file_locations["distinctiveness_images"])

        # Keep only characters that are in CLD
        complexities = pd.read_csv(config.data_file_locations["all_complexities"], index_col=0)
        complexities = complexities[complexities["scale_method"] == "pad"]
        complexities = complexities[complexities["dataset"].isin(config.HANDWRITTEN_DATASETS)]
        cld = pd.read_csv(config.data_file_locations["cld_processed"], index_col=0)
        simplified_characters = set(cld["Character"].tolist())
        complexities = complexities[complexities["simplified_character"].isin(simplified_characters)]

        # Find median complexity image for each character in each image
        rows = []
        for _, cdf in complexities.groupby("rendered_character"):
            for _, pdf in cdf.groupby("period"):
                sorted_pdf = pdf.sort_values(by="perimetric_complexity")
                median_row = sorted_pdf.iloc[int(pdf.shape[0]/2)]
                rows.append(tuple(median_row.values))
        median_complexity_df = pd.DataFrame(rows, columns=complexities.columns)

        # Copy images into a new folder
        images = []
        for _, row in median_complexity_df.iterrows():
            from_file_path = f"{config.data_file_locations['images']}/{row['dataset']}_padded_lee/{row['rendered_character']}_{row['period']}_{row['image_ID']}.png"
            to_folder = config.data_file_locations["distinctiveness_images"]
            character = row["rendered_character"]
            period = row["period"]
            image_id = row["image_ID"]
            if row["dataset"] == "traditional":
                # fix some errors specific to the traditional handwritten dataset
                if character == "幕":
                    from_file_path = f"{config.data_file_locations['images']}/{row['dataset']}_padded_lee/p_{row['period']}_{row['image_ID']}.png"
                elif character == "嶒":
                    from_file_path = f"{config.data_file_locations['images']}/{row['dataset']}_padded_lee/p_{row['period']}__{row['image_ID']}.png"
                elif character == "濈":
                    from_file_path = f"{config.data_file_locations['images']}/{row['dataset']}_padded_lee/濈_{row['period']}__{row['image_ID']}.png"
            images.append((from_file_path, to_folder, character, period, image_id))
        
        pool = Pool(os.cpu_count())
        pool.starmap(image_helpers.copy_image, images)
        pool.close()
        pool.join()

        pool = Pool(os.cpu_count())
        pool.map(image_helpers.dilate_image, [f"{config.data_file_locations['distinctiveness_images']}/{f}" for f in os.listdir(config.data_file_locations["distinctiveness_images"])])
        pool.close()
        pool.join()
        
        logging.info(f"  Copied {len(os.listdir(config.data_file_locations['distinctiveness_images']))} images for distinctiveness analysis.")


def _get_embedding_df() -> pd.DataFrame:
    """Reads in and preprocesses our HCCR embedding dataframe"""

    embedding_df = pd.read_csv(config.data_file_locations["embeddings"], index_col=0)
    embedding_df["fc1_embedding"] = embedding_df["fc1_embedding"].apply(lambda x: np.array(eval(x)))

    # Add simplified characters column to embedding df
    complexities_df = pd.read_csv(config.data_file_locations["all_complexities"], index_col=0)
    rendered2simplified = complexities_df.set_index("rendered_character").to_dict()["simplified_character"]
    embedding_df = embedding_df.rename({"character": "rendered_character"}, axis=1)
    embedding_df["simplified_character"] = embedding_df["rendered_character"].apply(lambda x: rendered2simplified[x])

    return embedding_df


def _calculate_distinctiveness(embedding_df: pd.DataFrame) -> pd.DataFrame:
    """For a given dataframe containing HCCR embeddings, calculate distinctiveness of each character in it"""

    distinctiveness_rows = []
    for period, pdf in embedding_df.groupby("period"):

        df = pdf.reset_index(drop=True)

        distances = euclidean_distances(df["fc1_embedding"].tolist())

        for i, row in df.iterrows():
            distinctiveness = np.mean(sorted(distances[i])[1:config.DISTINCTIVENESS_NEIGHBOURS+1])
            
            distance_index = [(distances[i][j], j) for j in range(len(distances[i]))]
            nearest_character_indices = [k[1] for k in sorted(distance_index)[1:config.DISTINCTIVENESS_EXAMPLES + 1]]
            nearest_characters = df.iloc[nearest_character_indices]["rendered_character"].tolist()

            distinctiveness_rows.append((row["rendered_character"], row["simplified_character"], period, row["image_id"], distinctiveness, nearest_characters))

    distinctiveness_df = pd.DataFrame(distinctiveness_rows, columns=["rendered_character", "simplified_character", "period", "image_id", "distinctiveness", "nearest neighbours"])

    return distinctiveness_df

def calculate_distinctiveness():
    """
    For each character in our distinctiveness dataset, calculates their distinctiveness as average euclidean distance between top 20 neighbours
    """

    if not os.path.exists(config.DISTINCTIVENESS_LOCATION):
        os.mkdir(config.DISTINCTIVENESS_LOCATION)

    embedding_df = _get_embedding_df()
    distinctiveness_df = _calculate_distinctiveness(embedding_df)
    distinctiveness_df.to_csv(config.data_file_locations["distinctiveness_csv"])

    logging.info(f"  {distinctiveness_df.shape[0]} distinctiveness scores generated.")


def calculate_persistent_stream_distinctiveness():
    """
    For each period in our dataset, generate a distinctiveness file of characters that originate from that period stream AND are present in every period stream after
    """

    embedding_df = _get_embedding_df()
    seen_characters = set()

    first_period = True
    df = None

    for i, period in enumerate(config.PERIODS):

        # Get characters that first appeared in this period
        period_stream_characters = set(
            embedding_df[embedding_df["period"] == period]["simplified_character"].unique()
            ).difference(seen_characters)
        seen_characters = seen_characters.union(period_stream_characters)
        period_df = embedding_df[embedding_df["simplified_character"].isin(period_stream_characters)]
        
        # Get characters that are available in every period after their first appearance
        persistent_characters = []
        for c, cdf in period_df.groupby("simplified_character"):
            if cdf.shape[0] >= len(config.PERIODS) - i:
                persistent_characters.append(c)
        
        persistent_stream_embedding_df = embedding_df[embedding_df["simplified_character"].isin(persistent_characters)].reset_index(drop=True)
        persistent_stream_distinctiveness_df = _calculate_distinctiveness(persistent_stream_embedding_df)
        persistent_stream_distinctiveness_df["period_stream"] = [period] * persistent_stream_distinctiveness_df.shape[0]

        if first_period:
            df = persistent_stream_distinctiveness_df
            first_period = False
        else:
            df = df.append(persistent_stream_distinctiveness_df, ignore_index=True)

        logging.info(f"  Added {persistent_stream_distinctiveness_df.shape[0]} distinctiveness datapoints for persistent {period} stream characters.")

    df.to_csv(config.data_file_locations["persistent_distinctiveness_csv"])


def calculate_distinctiveness_dataset_complexities():
    """For each dilated image in our distinctiveness dataset, calculates perimetric and pixel complexity"""

    distinctiveness_df = pd.read_csv(config.data_file_locations["distinctiveness_csv"], index_col=0)

    perimetric_complexities = []
    pixel_complexities = []
    for _, row in distinctiveness_df.iterrows():
        image_path = f"{config.data_file_locations['distinctiveness_images']}/{row['rendered_character']}_{row['period']}_{row['image_id']}.png"
        perimetric_complexity, pixel_complexity = perimetricComplexity(image_path)

        perimetric_complexities.append(perimetric_complexity)
        pixel_complexities.append(pixel_complexity)
    
    distinctiveness_df["perimetric_complexity"] = perimetric_complexities
    distinctiveness_df["pixel_complexity"] = pixel_complexities

    distinctiveness_df.to_csv(config.data_file_locations["distinctiveness_csv"])


