# shared scraper stuff
common_scraper_headers = {
    "USER_AGENT" : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    "CONNECTION" : 'keep-alive',
    "WAIT" : 0.1,
}
SCRAPER_BATCH_SIZE = 64
SCRAPER_MAX_TRIES = 2
SCRAPER_SLEEP_TIME = 5

# Hanziyuan specific scraper stuff
hzy_scraper_headers = {
    "HZY_BASE" : "https://hanziyuan.net/etymology",
    "HZY_HOST" : 'hanziyuan.net',
    "HZY_REFERER" : 'https://hanziyuan.net/',
    "HZY_ORIGIN" : 'https://hanziyuan.net',
    "COOKIE" : 'Oracle=CfDJ8CgM53I9KiBLpeycp49iYPNuRrfuF88uuVKqUX_QuQw2ztpi6OSg7I9ZjF7zkBVkrtT7KtcR_XyO8KaKu6k6CGXYd6VgsI8B9iYtMaX6G1slrYYNV3gPk0H9hi2tB2RSjUgGIVD54RdwGeX-So0wivc; _ga=GA1.2.651426570.1595821518; _gid=GA1.2.700954979.1595821518; Hm_lvt_44bf35035989ecd905587eb98a45525e=1595821519; Bronze=CfDJ8CgM53I9KiBLpeycp49iYPOKIWpioL82m7SLH8GkCnCeua5dfFvytNRRGY9MVX7licNpQA8DOMhe4GRpLfeU8xcWfc6hRRNC7iC2FCoqJf4kesAxcVEp2jdDOBGOB08pqR8gXh3aQr5R-4Eb63i9mVA; _gat=1; Hm_lpvt_44bf35035989ecd905587eb98a45525e=1595823637',
    "BRONZE" : 'CfDJ8CgM53I9KiBLpeycp49iYPNcgLYffg92WRj696HqJ7g6ETW6XO5936oTDZ_KFQV4VPlzzUC_7k1r-ylG9UMEHUY4szqIPo_GeedCJ0LUwcVG0jzYOMSlpQ1BbqGwNdH4K21wdDCH7p5sVu8sGJxbW4o',
    "CONTENT_TYPE" : 'application/x-www-form-urlencoded; charset=UTF-8',
    "SEAL" : 'CfDJ8CgM53I9KiBLpeycp49iYPNcgLYffg92WRj696HqJ7g6ETW6XO5936oTDZ_KFQV4VPlzzUC_7k1r-ylG9UMEHUY4szqIPo_GeedCJ0LUwcVG0jzYOMSlpQ1BbqGwNdH4K21wdDCH7p5sVu8sGJxbW4o',
}
HZY_UNWANTED_PERIODS = set(["Liushutong"])

# ZDIC specific scraper stuff
ZDIC_BASE = "https://www.zdic.net/hans/"
ZDIC_UNWANTED_PERIODS = set(["kr", "jp", "hk", "kai", "qinwenzi", "chuwenzi"])
ZDIC_DATA_TYPE_BLOCK = "字源字形" # HTML header on the zdic website for the character origins section

# Datasets that we use
HANDWRITTEN_DATASETS = ["hzy", "casia", "traditional"]
FONT_DATASETS = ["Hiragino Sans GB", "SimSun"]

# Where is everything located?
ROOT = "" # Set me to something!
IMAGES_LOCATION = f"{ROOT}/images"
COMPLEXITIES_LOCATION = f"{ROOT}/complexities"
DISTINCTIVENESS_LOCATION = f"{ROOT}/distinctiveness"
data_file_locations = {
    "images" : f"{ROOT}/images",
    "hzy_raw_csv" : f"{IMAGES_LOCATION}/hanziyuan_raw.csv",
    "hzy_raw" : f"{IMAGES_LOCATION}/hanziyuan_raw",
    "zdic_raw" : f"{IMAGES_LOCATION}/zdic_raw",
    "hzy_processed" : f"{IMAGES_LOCATION}/hanziyuan_processed",
    "zdic_processed" : f"{IMAGES_LOCATION}/zdic_processed",
    "zdic_stroke_gif_csv" : f"{COMPLEXITIES_LOCATION}/zdic_stroke_gif_complexities.csv",
    "hzy_image_uris" : f"{IMAGES_LOCATION}/hanziyuan_raw_image_uris.csv",
    "casia_raw" : f"{IMAGES_LOCATION}/handwritten_simplified_raw",
    "traditional_raw" : f"{IMAGES_LOCATION}/handwritten_traditional_raw",
    "cld" : f"{ROOT}/cld.csv",
    "cld_processed": f"{ROOT}/cld_processed.csv",
    "Hiragino Sans GB_raw" : f"{IMAGES_LOCATION}/hiragino_sans_gb_raw",
    "SimSun_raw" : f"{IMAGES_LOCATION}/simsun_raw",
    "all_complexities" : f"{COMPLEXITIES_LOCATION}/all_complexities.csv",
    "ccd_raw": f"{ROOT}/ccd.tsv",
    "ccd": f"{ROOT}/ccd.csv",
    "distinctiveness_images": f"{IMAGES_LOCATION}/distinctiveness_images", 
    "embeddings": f"{DISTINCTIVENESS_LOCATION}/hccr_embeddings.csv",
    "distinctiveness_csv": f"{DISTINCTIVENESS_LOCATION}/distinctiveness.csv",
    "persistent_distinctiveness_csv": DISTINCTIVENESS_LOCATION + "/streamed_persistent_distinctiveness.csv",
    "descriptive_images": f"{IMAGES_LOCATION}/descriptive_images",
}

# Original folder/file names of datasets downloaded from the web
original_data_file_names = {
    "cld" : "chineselexicaldatabase2.1.csv",
    "casia" : "CASIA-HWDB_Test/Test",
    #"traditional" : "cleaned_data(50_50)",
    "traditional" : "cleaned_data",
}  

# Minimum size of our datasets, ie. their current size as of 15/08/21
dataset_min_size = {
    "cld": 48644,
    "cld_processed": 3913,
    "casia_chars" : 7330,
    "casia_images" : 776523,
    "traditional_chars" : 4803,
    "traditional_images" : 250712,
    "hzy_chars" : 2969,
    "hzy_images" : 38066,
    "Hiragino Sans GB_raw" : 3913,
    "SimSun_raw" : 3913,
}

# columns from CLD that we want to keep
CLD_KEEP_COLUMNS = [
    "Word", "Pinyin", "C1Type", "Strokes", "Frequency", "C1Frequency"
]

# Fonts that we generate images for
FONTS = ["Hiragino Sans GB", "SimSun"]

# Image preprocessing stuff
IMG_SIZE = 300
BLACK = 65535
CROP_DIST = 30
SKELETONISE_METHOD = "lee"
PERIODS = ["Oracle", "Bronze", "Seal", "Traditional", "Simplified"]
PREPROCESSING_BATCH_SIZE = 1024

# Distinctiveness stuff
DISTINCTIVENESS_NEIGHBOURS = 20
DISTINCTIVENESS_EXAMPLES = 10
