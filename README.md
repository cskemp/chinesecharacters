This repository contains code, data and experimental materials for:

Han, S. J, Kelly, P., Winters, J., & Kemp, C. (2022). Simplification is not dominant in the evolution of Chinese characters. *Open Mind*.

## Folder Structure

#### analysis
This folder contains all of our analysis code, packaged into notebooks for either Python or R.

#### data
This folder contains all of our data, including our raw image data.
Because our datasets are extremely large, this repository only contains a sample of each dataset in order to illustrate its file structure. Important files such as the full CSVs for character complexities are also missing due to their size.

A complete folder with the same file structure can be found on [Zenodo]( https://doi.org/10.5281/zenodo.7185331 )

#### data_generation
This folder contains all of our Python code for scraping, processing and evaluating our image datasets. Please refer to its README for details on how to run our pipeline.

#### experiment
This folder contains all of the materials for our behavioural experiment, including data and source code for experiment 

#### figures
This folder contains all of the figures for both the main paper and the supplementary materials.

#### tables
This folder contains tables presented in the supplementary materials.


#### complexity_change_shiny
Code for a Shiny [app]( https://www.charleskemp.com/code/chinese_complexity_change.html ) that allows users to visualize changes in complexity over time for individual characters. 

#### root level scripts
'generate_sample_data_folder.py': generates the 'data' folder within this repo, which holds a sample of our full dataset (sample of 20 images of 20 characters for every period/dataset). This is provided for convenience.
