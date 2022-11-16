# Hanzi Project Data Generation

This folder contains the complete codebase for retrieving our image datasets, preprocessing these datasets and then measuring complexity and discriminability. 

## Generating our datasets
1. Download CLD, CASIA and handwritten datasets and paste raw folders into the folder. Instructions for each dataset can be found below. Do not rename anything.
2. Run generate_datasets.py to generate all image and complexity datasets, and generate_distinctiveness_datasets.py to generate the distinctiveness dataframes!

This process may take a while to run depending on how fast your machine is. It involves web scraping, so it cannot be run offline.

## Manually Downloaded Data

CLD, CCD, handwritten simplified and handwritten traditional data need to be downloaded and placed into the data folder manually, and then generate_datasets.py will take care of the rest.

Upon completing this step, your root datafolder should contain the following files:

    chineselexicaldatabase2.1.csv

    ccd.tsv

    CASIA-HWDB_Test

    cleaned_data

#### CLD: Chinese Lexical Database

CLD data can be downloaded from `http://www.chineselexicaldatabase.com/download.php`. Download the dataset in .csv format and then place it in your root data folder.

#### CCD: Chinese Characters Decomposition

CCD data can be downloaded from `https://commons.wikimedia.org/wiki/User:Artsakenos/CCD-TSV`. The fastest and easiest way to do this is to just manually copy the contents of the page into a .tsv file named `ccd.tsv` before manually cleaning the file by deleting the non-tsv looking parts (ie. the header and footer).

#### Simplified Handwritten Chinese Character Images

Handwritten simplified images are originally sourced from `http://www.nlpr.ia.ac.cn/databases/handwriting/Home.html`, but we downloaded them from `https://www.kaggle.com/pascalbliem/handwritten-chinese-character-hanzi-datasets`. Download only the TEST dataset from this link and extract the files into your root data folder. Make sure your character encoding is set to UTF-8!.

#### Traditional Handwritten Chinese Character Images

Handwritten traditional images can be downloaded from from `https://github.com/AI-FREE-Team/Traditional-Chinese-Handwriting-Dataset`. Specifically, you can first download the common words dataset using `git clone https://github.com/AI-FREE-Team/Traditional-Chinese-Handwriting-Dataset.git`. You should then extract all four .zip files before moving the `cleaned_data` folder into your root data folder.

#### Unexplained complexity differences
We obtained slightly different pixel and perimetric complexity scores for 62878 of the images in our dataset when we ran our final code compared to when we ran our initial experiments. 305 of these images were padded images and the rest were stretched. All differences are documented in the 'unexplained_complexity_differences.csv' file, in which the 'old_X_complexity' column details the complexity that we found during experimentation, and the 'new_X_complexity' column details the complexity scores that we are finding while running our final cleaned up code. These differences are small, with most typically being a difference of only one or two pixels.

## Measuring Discriminability

Our discriminability generation code is packaged separately in `generate_data/distinctiveness`. This is because this code depends on a caffe installation, so we run it in a Docker container. Instructions can be found below.

#### HCCR embeddings

The pretrained model that we use is downloaded from `https://github.com/chongyangtao/DeepHCCR`. No need to download anything on your own -- we've included the necessary .prototxt and .caffemodel files in the distinctiveness folder. To run the docker image, use the command `docker run -ti bvlc/caffe:cpu`. You should then copy the distinctiveness folder into the container, and then copy the distinctiveness images folder into the container's distinctiveness folder. Run `generate_embeddings.py`, and then copy the generated folder `hccr_embeddings.csv` into a 'distinctiveness' folder inside the root data folder.

## Measuring Descriptive Complexity

Our descriptive complexity code is also packaged separately in `generate_data/descriptive_complexity`. This is because this code depends on a Potrace installation, which is easiest to accomplish with homebrew. `generate_data/descriptive_complexity/potrace.py` can easily be run on MacOS (and Linux?) without any other setup effort. Once this is complete, copy the outputted .csv file `descriptive_complexities.csv` back into the data folder's complexity folder.
