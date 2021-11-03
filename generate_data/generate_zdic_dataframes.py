import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import time
import config
import logging
import os

import pandas as pd

from bs4 import BeautifulSoup
from typing import Optional
from PIL import Image

TEMP_GIF_FILE = "test.gif"

def get_page(url: str) -> Optional[str]:
        # Retrieves the html of a webpage given by 'url' and returns it as a string
        for _ in range(config.SCRAPER_MAX_TRIES):
            try:
                req = requests.get(url, verify=False)
                req.encoding = "utf-8"
                return req.text
            except:
                pass
        return None


def download_image(img_url: str, filepath: str, character: str) -> bool:
        # Downloads an image located at 'img_url' to a location given by 
        # 'filepath' (includes file name)

        if not img_url:
            return False

        session = requests.Session()
        headers = {
            "USER_AGENT": config.common_scraper_headers["USER_AGENT"],
            "CONNECTION": config.common_scraper_headers["CONNECTION"],
            "REFERER": (config.ZDIC_BASE + character).encode("utf-8"),
        }

        # Try a max of 10 times to retrieve the image, give up if server keeps breaking connection
        for _ in range(config.SCRAPER_MAX_TRIES):
            try:
                response = session.get(img_url, headers=headers)
                if not response.ok:
                    return False
                else:
                    with open(filepath, 'wb') as handle:
                        handle.write(response.content)
                    handle.close()
                    
                    # Don't want to overload the website
                    time.sleep(config.SCRAPER_SLEEP_TIME)

                    return True
            except:
                pass

        return False


def download_stroke_gif(character: str) -> bool:
        # downloads the character stroke guide gif on zdic.net for a given character

        # Retrieve character page first
        page = get_page(config.ZDIC_BASE + character)

        # ID of img tag on zdic for the gif
        IMG_ID = "bhbs"

        # Get gif link
        if page != None:
            for _ in range(config.SCRAPER_MAX_TRIES):
                try:
                    soup = BeautifulSoup(page, 'html.parser')
                    res = soup.find_all("img", {"id":IMG_ID})
                    if len(res) > 0:  
                        gif_link = "https:" + res[0]["data-gif"]
                        return download_image(gif_link, TEMP_GIF_FILE, character)
                    else:
                        return False
                except:
                    pass
        
        return False


def get_stroke_gif_complexity(character: str) -> Optional[int]:

    stroke_gif = download_stroke_gif(character)
    if stroke_gif:
        with Image.open(TEMP_GIF_FILE) as im:
            return im.n_frames
    else:
        return None


def get_stroke_gif_complexities() -> None:
    """Finds stroke gif complexitie s (number of frames in stroke gif) for as many rendered characters as possible, saves to a dataframe"""

    cld = pd.read_csv(config.data_file_locations["cld_processed"], index_col=0)
    cld_characters = set(cld["Character"])

    if os.path.exists(config.data_file_locations["zdic_stroke_gif_csv"]):
        stroke_gif_complexity_df = pd.read_csv(config.data_file_locations["zdic_stroke_gif_csv"], index_col=0)
        stroke_gif_exists = True
        characters = cld_characters.difference(set(stroke_gif_complexity_df["rendered_character"]))
    else:
        stroke_gif_exists = False
        characters = cld_characters

    rows = []
    for i, character in enumerate(characters): 
        stroke_gif_complexity = get_stroke_gif_complexity(character) 
        rows.append((character, stroke_gif_complexity))
        
        if (i+1) % 50 == 0:     
            logging.info(f"  Scraped gif complexities for {i+1}/{len(characters)} characters...")
    
            df = pd.DataFrame(rows, columns=["rendered_character", "stroke_gif_complexity"])
            if stroke_gif_exists:
                stroke_gif_complexity_df = pd.concat([df, stroke_gif_complexity_df], axis=0, ignore_index=True)
            else:
                stroke_gif_exists = True
                stroke_gif_complexity_df = df
            stroke_gif_complexity_df.to_csv(config.data_file_locations["zdic_stroke_gif_csv"])

            rows = []

            time.sleep(10)

    df = pd.DataFrame(rows, columns=["rendered_character", "stroke_gif_complexity"])
    stroke_gif_complexity_df = pd.concat([df, stroke_gif_complexity_df], axis=0, ignore_index=True)
    stroke_gif_complexity_df.to_csv(config.data_file_locations["zdic_stroke_gif_csv"])
    logging.info(f"  Stroke gif complexity file contains complexities for {stroke_gif_complexity_df.shape[0]} rendered characters.")