import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
from base64 import b64decode
from typing import Tuple, List, Set
from multiprocessing import Pool
from html2image import Html2Image
from shutil import copyfile

import time
import os
import requests
import logging
import re
import config
import opencc

import config

def scrape_hanziyuan_character(character: str) -> List[Tuple[str, str, str, str]]:
    """
        Scrapes hanziyuan.net for image data of a given character.

        This code is not great. I wrote it a while ago and I'm not sure how exactly it's breaking down the scraped html file anymore, but it apparently still works. Sorry.
    """

    output = []

    session = requests.Session()
    headers = {'Chinese':str(ord(character)),'User-Agent':config.common_scraper_headers["USER_AGENT"], 'Connection':config.common_scraper_headers["CONNECTION"], 'Host':config.hzy_scraper_headers["HZY_HOST"], 'Cookie':config.hzy_scraper_headers["COOKIE"], 'Content-Type':config.hzy_scraper_headers["CONTENT_TYPE"], 'Seal':config.hzy_scraper_headers["SEAL"], 'Referer':config.hzy_scraper_headers["HZY_REFERER"], 'Origin':config.hzy_scraper_headers["HZY_ORIGIN"]}
    payload = {'chinese':character, 'Bronze':config.hzy_scraper_headers["BRONZE"]}
    response = session.post(config.hzy_scraper_headers["HZY_BASE"], headers=headers, data=payload)

    soup = BeautifulSoup(response.text, 'html.parser')
    if len(soup.find_all("style", {"type":"text/css"})) > 0:
        uri_html = soup.find_all("style", {"type":"text/css"})[0]

        # Get id to image uri mappings for each image
        mappings = {}
        for mapping in str(uri_html)[24:].split("}"):
            image_id = mapping.strip()[1:7]
            url = mapping[52:-3]
            mappings[image_id] = url

        # Get image id to period mappings
        headers = [m.start() for m in re.finditer('<h3>', response.text)]
        period_sections = [response.text[headers[i]:headers[i+1]] if i != len(headers) - 1 else response.text[headers[i]:response.text.find("<style")] for i in range(0,len(headers))]
        for period_section in period_sections[:4]:
            psoup = BeautifulSoup(period_section, 'html.parser')
            header = psoup.find_all("h3")[0].contents[1]
            
            period = header.split(" ")[1]
            num_examples = int(header.split(" ")[-1][1:-1])
            
            if num_examples > 0 and period not in config.HZY_UNWANTED_PERIODS:
                ids = [i.contents[0] for i in psoup.find_all("div", {"data-target":"#etymologyModal"})]
                output += [(str(cid), character, period, mappings[cid].split(",")[1]) for cid in ids]

    time.sleep(config.common_scraper_headers["WAIT"])
    
    return output


def scrape_hanziyuan_images():
    """Scrapes image data from hanziyuan.net for every available single character in the CLD"""

    cld = pd.read_csv(config.data_file_locations["cld_processed"])
    chars = cld["Character"]
    logging.info(f"      {len(chars)} single characters found in CLD.")

    pool = Pool(os.cpu_count())

    image_data = []
    for b in range(0, len(chars), config.SCRAPER_BATCH_SIZE):

        logging.info(f"      Scraping batch {int(b/config.SCRAPER_BATCH_SIZE) + 1}/{int(len(chars)/config.SCRAPER_BATCH_SIZE) + 1} of characters from Hanziyuan.")
        batch = chars[b : b + config.SCRAPER_BATCH_SIZE]
        batch_image_data = pool.map(scrape_hanziyuan_character, batch)
        image_data += [i for j in batch_image_data for i in j]

    pool.close()
    pool.join()

    scraped_chars = set([i[1] for i in image_data])
    logging.info(f"      {len(scraped_chars)} characters successfully scraped from Hanziyuan")
    logging.info(f"      {len(image_data)} images successfully scraped from Hanziyuan")

    hzy_image_df = pd.DataFrame(image_data, columns=["characterID", "character", "period", "imageURI"])
    hzy_image_df.to_csv(config.data_file_locations["hzy_raw_csv"])


def generate_hanziyuan_images():
    """Generates SVGs from image data scraped from hanziyuan.net"""

    hzy = pd.read_csv(config.data_file_locations["hzy_raw_csv"],  index_col=0)

    if not os.path.exists(config.data_file_locations["hzy_raw"]):
        os.mkdir(config.data_file_locations["hzy_raw"])

    for _, row in hzy.iterrows():
        charfolder = "{}/{}".format(config.data_file_locations["hzy_raw"], row["character"])
        pfolder = "{}/{}".format(charfolder, row["period"])
        if not os.path.exists(charfolder):
            os.mkdir(charfolder)
        if not os.path.exists(pfolder):
            os.mkdir(pfolder)
            
        data = b64decode(row["imageURI"])
        with open("{}/{}.svg".format(pfolder, row["characterID"]), "wb") as f:
            f.write(data)
        f.close()


def generate_font_image_data(font: str):
    """Generate font images of characters"""

    cld_characters = pd.read_csv(config.data_file_locations["cld_processed"])["Character"].tolist()

    s2t = opencc.OpenCC("s2t.json")
    traditional_characters = [s2t.convert(c) for c in cld_characters]
    characters = list(set(traditional_characters + cld_characters))
    logging.info(f"  Generating {font} images for {len(characters)} characters.")

    hti = Html2Image()

    font_folder = config.data_file_locations[f"{font}_raw"]

    if not os.path.exists(font_folder):
        os.mkdir(font_folder)

    for b in range(0, len(characters), config.SCRAPER_BATCH_SIZE):

        logging.info(f"    Generating batch {int(b/config.SCRAPER_BATCH_SIZE) + 1}/{int(len(characters)/config.SCRAPER_BATCH_SIZE) + 1} of characters for {font} images...")
        batch = characters[b : b + config.SCRAPER_BATCH_SIZE]
        for character in batch:
            hti.screenshot(
                html_str=character,
                css_str=['body {font-family: ' + font + '}', 'body {font-size: 500px;}'],
                save_as=f"temp.png"
            )

            copyfile("temp.png", f"{font_folder}/{character}.png")
    
    os.remove("temp.png")

    return


def generate_character_decomposition_matrix() -> None:
    """Generates and saves character component decomposition matrix using CCD tsv file."""

    def _decompose(character: str, components: Set[str], data: pd.DataFrame):
        if character in ("?", "*") or character not in components:
            return [character]
        row = data[data["Component"] == character]
        if row["CompositionType"].iloc[0] == "一":
            return [character]
        r = row["RightComponent"].iloc[0]
        l = row["LeftComponent"].iloc[0]
        right = []
        left = []
        
        if pd.isna(r) and not pd.isna(l):
            return _decompose(l, components, data) + [r]
        if pd.isna(l) and not pd.isna(r):
            return [l] + _decompose(r, components, data)

        if r:
            for c in r:
                right += _decompose(c, components, data)
        if l:
            for c in l:
                left += _decompose(c, components, data)
        
        return left + right

    ccd_data = pd.read_csv(config.data_file_locations["ccd_raw"], sep="\t")
    cld_data = pd.read_csv(config.data_file_locations["cld_processed"])
    components = set(ccd_data["Component"])
    characters = cld_data["Character"]
    decomposition_map = {}
    for character in characters:
        decomposed = _decompose(character, components, ccd_data)
        if decomposed:
            decomposition_map[character] = decomposed
    flatten = lambda l: [item for sublist in l for item in sublist]
    uniquecomponents = set(flatten(list(decomposition_map.values())))
    
    comp_count = {component:np.zeros(len(decomposition_map)) for component in uniquecomponents}
    comp_count["Character"] = []
    index = 0
    for character, component_list in decomposition_map.items():
        comp_count["Character"].append(character)
        for c in component_list:
            comp_count[c][index] += 1 
        index += 1
    
    compmatrix = pd.DataFrame(comp_count)
    cols = compmatrix.columns.tolist()
    cols.insert(0, cols.pop(cols.index('Character')))
    compmatrix = compmatrix[cols]
    compmatrix.to_csv(config.data_file_locations["ccd"])


def calculate_adjusted_frequency(cld: pd.DataFrame, frequency:str) -> List[float]:
    """Calculate adjusted character frequencies, where the frequency of a character is its own frequency PLUS
    the frequency of all of its components"""
    
    characters = cld["Character"]
    frequencies = cld[frequency]

    frequency_map = dict(zip(characters, frequencies))
    ccd_matrix = pd.read_csv(config.data_file_locations["ccd"], index_col=0)
    component_characters = set(ccd_matrix.columns[1:])

    adjusted_frequencies = []
    for character in characters:
        adjusted_frequency = frequency_map[character]
        if character in component_characters:
            parents = ccd_matrix[["Character", character]]
            parents = parents[parents[character] != 0]
            parent_characters = parents["Character"].tolist()
            adjusted_frequency = cld[cld["Character"].isin(parent_characters)][frequency].sum()
        else:
            adjusted_frequency = frequency_map[character]
        adjusted_frequencies.append(adjusted_frequency)
    return adjusted_frequencies


def generate_data(limit_dataset: str) -> bool:

    #### Clean CLD data
    logging.info("  Checking CLD character data...")
    if not os.path.exists(config.data_file_locations["cld_processed"]):
        cld = pd.read_csv(config.data_file_locations["cld"])
        if cld.shape[1] != len(config.CLD_KEEP_COLUMNS) + 2:
            logging.info("    Processing CLD character data...")
            cld = cld[cld["Length"] == 1]
            cld = cld[config.CLD_KEEP_COLUMNS]
            cld = cld.rename({"Word": "Character"}, axis=1)
            cld = cld.reset_index(drop=True)
            for frequency in ["Frequency", "C1Frequency"]:
                cld[f"Adjusted{frequency}"] = calculate_adjusted_frequency(cld, frequency)
            cld.to_csv(config.data_file_locations["cld_processed"])
    logging.info("  CLD data OK!")
    
    #### Ancient Chinese Character Images
    if not limit_dataset or limit_dataset == "hzy":
        logging.info("  Checking Hanziyuan image data...")
        if not os.path.exists(config.data_file_locations["hzy_raw"]):
            logging.info("    Scraping Hanziyuan dataset...")
            scrape_hanziyuan_images()
            generate_hanziyuan_images()

        num_characters = len(os.listdir(config.data_file_locations["hzy_raw"]))
        num_images = sum([len(files) for _, _, files in os.walk(config.data_file_locations["hzy_raw"])])
        min_chars = config.dataset_min_size[f"hzy_chars"]
        min_images = config.dataset_min_size[f"hzy_images"]
        logging.info(f"    {num_characters} characters and {num_images} Hanziyuan SVGs available.")
        if num_characters < min_chars or num_images < min_images:
            logging.error(f"    Hanziyuan dataset contains {num_characters} characters and {num_images} image files, but at least {min_chars} characters and {min_images} images were expected.")
            return False


    #### Font-based Traditional and Simplified Chinese Character Images
    if not limit_dataset or limit_dataset in ("Hiragino Sans GB", "SimSun"):
        logging.info("  Checking font image data...")
        for font in config.FONTS:
            if not os.path.exists(config.data_file_locations[f"{font}_raw"]):
                logging.info(f"    Generating character images for {font}...")
                generate_font_image_data(font)
            num_images = len(os.listdir(config.data_file_locations[f"{font}_raw"]))
            logging.info(f"    {num_images} characters available for {font} image dataset.")
            min_chars = config.dataset_min_size[f"{font}_raw"]
            if num_images < min_chars:
                logging.error(f"    {font} image dataset contains {num_images} images but at least {min_chars} images expected.")
                return False

    
    #### CCD decomposition data
    logging.info("  Checking CCD character data...")
    if not os.path.exists(config.data_file_locations["ccd"]):
        logging.info(f"    Generating character decomposition matrix...")
        generate_character_decomposition_matrix()
        logging.info("    Character decomposition matrix generation OK!")
    logging.info("  CCD data OK!")

    #### Traditional and Simplified Chinese Character GIFs
    return True