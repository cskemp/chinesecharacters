This repository contains code, data and experimental materials for:
Han, S. J, Kelly, P., Winters, J., & Kemp, C. (2022). Simplification is not dominant in the evolution of Chinese characters. *Open Mind*.

## Folder Structure

#### analysis
This folder contains all of our analysis code, packaged into notebooks for either Python or R.

#### data
This folder contains all of our data, including our raw image data.
Because our datasets are extremely large, this repository only contains a sample of each dataset in order to illustrate its file structure. Important files such as the full CSVs for character complexities are also missing due to their size.

A complete folder with the same file structure can be found on [Zenodo](https://zenodo.org/)

#### data_generation
This folder contains all of our Python code for scraping, processing and evaluating our image datasets. Please refer to its README for details on how to run our pipeline.

#### experiment
This folder contains all of the materials for our behavioural experiment.

#### figures
This folder contains all of the figures for both the main paper and the supplementary materials.

## Notes

#### Unexplained complexity differences
We obtained slightly different pixel and perimetric complexity scores for 62878 of the images in our dataset when we ran our final code compared to when we ran our initial experiments. 305 of these images were padded images and the rest were stretched. All differences are documented in the 'unexplained_complexity_differences.csv' file, in which the 'old_X_complexity' column details the complexity that we found during experimentation, and the 'new_X_complexity' column details the complexity scores that we are finding while running our final cleaned up code. These differences are small, with most typically being a difference of only one or two pixels.