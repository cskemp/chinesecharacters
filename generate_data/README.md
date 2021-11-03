# Hanzi Project Data Generation

NOTE: This doc is a WIP, I intend to refactor our files into something a bit nicer

This folder contains the complete codebase for retrieving our image datasets, preprocessing these datasets and then measuring complexity and discriminability. This file provides a high level overview of these processes and a description of the scripts used to complete them.

Data used for our study should be fully reproducible by running main.py, but note that complications with setting up certain packages resulted in us switching between Windows and MacOS operating systems from time to time. As much as possible of the data generation process is automated, but manual actions are still required at certain points.

## Running main.py
1. Download CLD, CASIA and handwritten datasets and paste raw folders into a new data folder. Instructions for each dataset can be found below. Do not rename anything.
2. Change ROOT in config.py to match the path of your data folder.
3. Run main.py!

## Character Data

Download CLD, CCD, HCCR and THD data from specified sources and dump the raw downloaded files into your data folder. Set ROOT as your data folder location in config.py, and then run the check_manual_setup() step in main.py.

CCD data isn't downloadable as a raw file -- you have to copy the raw tsv web page to a .tsv file and then manually delete everything that's not a part of the tsv format. 

#### CLD: Chinese Lexical Database

Download from http://www.chineselexicaldatabase.com/download.php

Instructions:
1. Dowload the .csv file from the above link
 
cld.csv spec:
shape: (X, X)
- Simplified Character (str): UTF-8 encoded simplified Chinese character
- Traditional Character (str): Based on 'Simplified Character' column, generated using OpenCC
- C1Type (str): Pictographic, Pictologic, Pictosynthetic, Pictophonetic or Other
- Pinyin (str): Pinyin pronounciation for character
- Frequency (float):
- C1Frequency (float):
- FrequencySUBTL (float):


#### CCD: Chinese Characters Decomposition

Generate adjusted character frequencies: preprocessing/Adjusted_Frequencies.ipynb
Generate decomposed character matrix: preprocessing/Character_Decomposition.ipynb

Download CCD data from here and paste in a .txt file: https://commons.wikimedia.org/wiki/User:Artsakenos/CCD-TSV

min_components_matrix.csv spec:
shape: (N, M)
- sparse matrix, where column 1 is a list of characters and all following columns are indexed by a specific root character component from CCD. '1' at position (n,m) indicates that root component 'm' is a component of 'n'

## Image Data

#### Ancient Chinese Character Images

Scrape from https://hanziyuan.net/ 
Script: hanzi final/preprocessing/scrape_hanziyuan_images.py

#### Traditional Handwritten Chinese Character Images

Download from https://github.com/AI-FREE-Team/Traditional-Chinese-Handwriting-Dataset

Instructions
1. Download the common words dataset using 'git clone https://github.com/AI-FREE-Team/Traditional-Chinese-Handwriting-Dataset.git'
2. Extract all four .zip files
3. Move the cleaned_data(50_50) folder into your image data folder

#### Simplified Handwritten Chinese Character Images

Use http://www.nlpr.ia.ac.cn/databases/handwriting/Home.html
Because it's easier, download from https://www.kaggle.com/pascalbliem/handwritten-chinese-character-hanzi-datasets

Instructions
1. Download the TEST dataset from the above kaggle link
2. Extract files from zip. If using windows, helpful to use WinRAR and remember to set character encoding to UTF-8!

#### Font-based Traditional and Simplified Chinese Character Images

Fonts: Hiragino Sans GB and SimSun
Script: processing/render_font.py

#### Traditional and Simplified Chinese Character GIFs

## Image Preprocessing

Need to install cairosvg! Steps:
1. 'pip install cairosvg' for the python package
2. Download and install GTK++ here https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

#### Pad vs Stretch

## Measuring Complexity

#### Perimetric and Pixel Complexity

Uses this implementation: https://github.com/justinsulik/pythonScripts/blob/master/perimetricComplexity.py
Script: processing/perimetric_complexity.py

all_complexities_skeletonised_analysis.csv spec: 
shape: (X, X)
- character id (str): non-UTF encoded ID of 'original character' used for programs that don't play nice with UTF-8 encoding. Maintains a 1:1 value mapping with the 'original character' column
- original character (str): UTF-8 encoded Chinese character from original datasets
- simplified character (str): modern simplified variant of 'original character'
- period (str): Oracle, Bronze, Seal, Traditional or Simplified
- ID (str): ID assigned to each image within its dataset
- scale method (str): 'pad' or 'stretch'
- skeletonise method (str): 'lee' or 'zhang' skeletonise method for skimage.morphology.skeletonize function
- dataset (str): Hanziyuan, Traditional or Simplified 
- perimetric complexity (float): perimetric complexity value
- pixel complexity (int): pixel complexity value
- character stream: Oracle, Bronze, Seal, Traditional or Simplified. First period in which this row's 'simplified character' value appears in this dataset.

#### Vector-based Descriptive Complexity

** Did this part on macOS, because potrace is much easier to install there **
Script (for font dataset): processing/font potrace.py 
Script for standard datasets is basically the same

svg_complexities.csv spec:
shape: (X, X)
- character id (str): same as above
- original character (str): same as above
- simplified character (str): same as above
- period (str): same as above
- ID (str): same as above
- perimetric complexity (float): same as above
- pixel complexity (float): same as above
- SVG description length (int): raw string length of SVG description generated by Potrace

font_complexity_SimSun.csv spec:
shape: (X, X)
- original character (str): same as above
- simplified character (str): same as above
- perimetric complexity (float): same as above
- pixel complexity (float): same as above
- SVG description length (int): same as above

font_complexity_HiraginoSansGB.csv spec:
shape: (X, X)
- original character (str): same as above
- simplified character (str): same as above
- perimetric complexity (float): same as above
- pixel complexity (float): same as above
- SVG description length (int): same as above

#### Time-based Writing Complexity

gif_complexities.csv spec:
shape: (X, X)
- character (str): raw UTF-8 encoded character from zdic.net
- gif complexity (int): number of frames for a given character's handwriting demo

## Measuring Discriminability

#### HCCR embeddings

** Need to install caffe, which sucks, so we used a Docker container with caffe set up already **
Script: Forgot to copy it from the container, which has now been killed, yet again. Need to quickly rewrite

Model downloaded from https://github.com/chongyangtao/DeepHCCR

How to run:
1. Install Docker!
2. Run 'docker run -ti bvlc/caffe:cpu'
3. In a separate terminal, copy distinctiveness folder into the docker image
4. Copy scripts into the docker image using 'docker cp C:/Users/Jerome/Documents/GitHub/hanzi/final/distinctiveness quirky_greider:distinctiveness'
5. Copy images into the docker image using 'docker cp C:/Users/Jerome/Documents/hanzi_data/images/distinctiveness_images quirky_greider:distinctiveness/distinctiveness_images'
6. Inside the docker container, run generate_embeddings.py
7. Once done, copy out embeddings.csv file using 'docker cp quirky_greider:distinctiveness/hccr_embeddings.csv C:/Users/Jerome/Documents/hanzi_data/hccr_embeddings.csv'

## Additional Post Processing

#### Mapping Characters to Simplified Forms

Script: processing/Update character columns.ipynb

#### Finding Representative Images for each Character

Script: CNN/determine characters to embed.ipynb

#### Behavioural Experiment Characters

#### Adjusted Frequency Counts

## Statistical Analysis

## Generating Figures

#### Figure 1

#### Figure 2

#### Figure 3

#### Figure 4

analysis/Figure 4.ipynb

#### Figure 5


# Notes

## Unexplained complexity differences
We obtained slightly different pixel and perimetric complexity scores for 62878 of the images in our dataset when we ran our final code compared to when we ran our initial experiments. 305 of these images were padded images and the rest were stretched. All differences are documented in the 'unexplained_complexity_differences.csv' file, in which the 'old_X_complexity' column details the complexity that we found during experimentation, and the 'new_X_complexity' column details the complexity scores that we are finding while running our final cleaned up code. These differences are small, with most typically being a difference of only one or two pixels.

## Manual corrections for the Traditional Handwritten Dataset
The source data for the traditional handwritten dataset contains two mislabelled characters, 嶒 and 幕, which appear as original character 'p' with no recorded image ID and original character 'p' with correct image IDs in the all_complexities.csv respectively. To correct this, we manually edited our csv file.