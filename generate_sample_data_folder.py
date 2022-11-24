"""
Generates a sample data folder to upload to the repo by copying the file structure of the actual data folder, 
as well as the first 1000 lines of every csv and a random sample of 3 images in every image folder.
"""

import os
import shutil
import random
import pandas as pd

SOURCE_FOLDER = "C:/Users/User/Downloads/hanzi_data_final"
MAX_ROWS = 1000
NUM_SAMPLES = 20
random.seed(0)
 

def copy_file_samples(folder):

    files = os.listdir(f"{SOURCE_FOLDER}/{folder}")
    files = random.sample(files, k=min(len(files), NUM_SAMPLES))

    os.mkdir(folder)

    for f in files:
        if "." in f:
            file_source_path = f"{SOURCE_FOLDER}/{folder}/{f}"
            file_dest_path = f"{folder}/{f}"
            if "csv" in f or "tsv" in f:
                df = pd.read_csv(file_source_path, index_col=0).iloc[:MAX_ROWS]
                df.to_csv(file_dest_path)
            else:
                shutil.copyfile(file_source_path, file_dest_path)
        else:
            copy_file_samples(f"{folder}/{f}")


if __name__ == "__main__":

    copy_file_samples("data")
