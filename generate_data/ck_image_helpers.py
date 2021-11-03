import os

import config
import logging
import cairosvg

import numpy as np
import skimage.io as io

from skimage import img_as_ubyte
from shutil import copyfile
from typing import List
from skimage.transform import resize
from skimage.filters import threshold_otsu
from skimage.morphology import thin, skeletonize, dilation, disk
from skimage.util import img_as_ubyte, invert


def get_all_image_paths(folder: str) -> List[str]:
    images = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.endswith((".png", ".svg")):
                images.append(os.path.join(root, filename))
    return images


def svg_to_png(from_image_path, to_image_path):
    """Rasterises an svg file to a new location"""
    cairosvg.svg2png(url=from_image_path, write_to=to_image_path, scale=10.0)


def copy_image(from_image_path, to_folder, character, period, img_id):
    """Copy an image tp a new folder"""

    to_image_path = f"{to_folder}/{character}_{period}_{img_id}.png"
    
    if from_image_path[-3:] == "svg":
        svg_to_png(from_image_path, to_image_path)
    else:
        copyfile(from_image_path, to_image_path)


def clean_image(image_path: str) -> int: 
    """Deletes an image if it does not contain any black pixels"""
    image = img_as_ubyte(io.imread(image_path, as_gray=True))
    if np.sum(image)/255 == image.shape[0]*image.shape[1]:
        os.remove(image_path)
        return 1
    else:
        return 0


def crop_and_scale_image(image, stretch=False):
    """
        First, crops the image so that its leftmost, topmost, bottommost and rightmost pixels are touching the image border. Then, stretches or pads the image to become square.
    """

    # Get top-most pixel row index
    def getTopMostPixel(image):
        for i in range(0, len(image)):
            if np.sum(image[i]) != 0:
                return i
        return 0

    # Get bottom-most pixel row index
    def getBottomMostPixel(image):
        for i in range(len(image)-1, -1, -1):
            if np.sum(image[i]) != 0:
                return i
        return len(image)-1

    # Get left-most pixel column index
    def getLeftMostPixel(image):
        for i in range(0, image.shape[1]):
            for j in range(0, len(image)):
                if image[j][i] != 0:
                    return i
        return 0

    # Get right-most pixel column index
    def getRightMostPixel(image):
        for i in range(image.shape[1]-1,-1,-1):
            for j in range(0, len(image)):
                if image[j][i] != 0:
                    return i
        return image.shape[1]-1

    r = getRightMostPixel(image)
    l = getLeftMostPixel(image)
    t = getTopMostPixel(image)
    b = getBottomMostPixel(image)

    width = r-l
    height = b-t
    image = image[t:b+1,l:r+1]
    
    if stretch:
        # Stretch image to become square
        dim = np.max([width, height])
        newimage = resize(image, (dim, dim), mode="constant")
    else:
        # Pad image to become square
        diff = abs(width - height)
        if width > height:
            top = int(diff/2)
            bottom = diff - top
            if top > 0 and bottom > 0:
                newimage = np.concatenate([top*[np.zeros(image.shape[1])], image, bottom*[np.zeros(image.shape[1])]])
            elif top == 0 and bottom > 0:
                newimage = np.concatenate([image, bottom*[np.zeros(image.shape[1])]])
            elif top > 0 and bottom == 0:
                newimage = np.concatenate([top*[np.zeros(image.shape[1])], image])
            else:
                newimage = image
        else:
            left = int(diff/2)
            right = diff-left
            newimage = np.array([np.concatenate([np.zeros(left), row, np.zeros(right)]) for row in image])

    return img_as_ubyte(newimage)


def rescale_and_skeletonise_image_variant(image, size, stretch=False, method="orig", final=False, pad=10, dilate=False): 
    
    # Scale image and rebinarise
    j = resize(image, (size-pad,size-pad), mode="constant")  
    # CK: add padding all around image to avoid skeletonization artifacts
    j = np.pad(j, (int(pad/2),int(pad/2)), 'constant', constant_values=(0.0,0.0) )

    if method == "none":
        return(img_as_ubyte(invert(j)))


    thresh = threshold_otsu(j) 
    binary = j > thresh
    
    # Skeletonise image
    if not dilate:
        if method == "zhang":
            skelbinary = skeletonize(binary)
        elif method == "lee":
            skelbinary = skeletonize(binary, method="lee")
        elif method == "thin":
            skelbinary = thin(binary)
        else:
            skelbinary = binary
    else:
        selem = disk(5)
        skelbinary = dilation(binary, selem)

    skel1= invert(skelbinary)

    # CK: if skel1 is the initial skeleton then scale again, because characters with thick strokes will end up smaller after skeletonization
    if not(final):
    # Binarise image
        skelbinary = np.array([np.array([True if px != 255 else False for px in row]) for row in skel1])
        selem = disk(1)
        # dilation useful so that stretching doesn't introduce gaps
        skelbinary = dilation(skelbinary, selem)
        skelbinary = crop_and_scale_image(skelbinary, stretch)
        skel2 = rescale_and_skeletonise_image_variant(skelbinary, size, False, method, True)
        #skel2 = rescale_and_skeletonise_image_variant(skelbinary, size, False, method, True, 40, True) 
        return(skel2)
    else:
        return(img_as_ubyte(skel1))

