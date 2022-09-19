import os
os.environ['path'] += r";C:\Program Files\GTK3-Runtime Win64\bin"

import numpy as np

import cairosvg
import PIL
import itertools
import functools
import math
import skimage
import shutil

from typing import List


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


def copy_image(from_image_path, to_folder, character, period, img_id, dataset=None):
    """Copy an image tp a new folder"""

    to_image_path = f"{to_folder}/{character}_{period}_{img_id}{'_' + dataset if dataset else ''}.png"
    
    if from_image_path[-3:] == "svg":
        svg_to_png(from_image_path, to_image_path)
    else:
        shutil.copyfile(from_image_path, to_image_path)


def clean_image(image_path: str) -> int: 
    """Deletes an image if it does not contain any black pixels"""
    image = skimage.img_as_ubyte(skimage.io.imread(image_path, as_gray=True))
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
        newimage = skimage.transform.resize(image, (dim, dim), mode="constant")
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

    return skimage.img_as_ubyte(newimage)


def rescale_and_skeletonise_image_variant(image, size, stretch=False, method="orig", final=False, pad=10, dilate=False): 
    
    # Scale image and rebinarise
    j = skimage.transform.resize(image, (size-pad,size-pad), mode="constant")  
    # CK: add padding all around image to avoid skeletonization artifacts
    j = np.pad(j, (int(pad/2),int(pad/2)), 'constant', constant_values=(0.0,0.0) )

    if method == "none":
        return(skimage.img_as_ubyte(skimage.util.invert(j)))


    thresh = skimage.filters.threshold_otsu(j) 
    binary = j > thresh
    
    # Skeletonise image
    if not dilate:
        if method == "zhang":
            skelbinary = skimage.morphology.skeletonize(binary)
        elif method == "lee":
            skelbinary = skimage.morphology.skeletonize(binary, method="lee")
        elif method == "thin":
            skelbinary = skimage.morphology.thin(binary)
        else:
            skelbinary = binary
    else:
        selem = skimage.morphology.disk(5)
        skelbinary = skimage.morphology.dilation(binary, selem)

    skel1= skimage.util.invert(skelbinary)

    # CK: if skel1 is the initial skeleton then scale again, because characters with thick strokes will end up smaller after skeletonization
    if not(final):
    # Binarise image
        skelbinary = np.array([np.array([True if px != 255 else False for px in row]) for row in skel1])
        selem = skimage.morphology.disk(1)
        # dilation useful so that stretching doesn't introduce gaps
        skelbinary = skimage.morphology.dilation(skelbinary, selem)
        skelbinary = crop_and_scale_image(skelbinary, stretch)
        skel2 = rescale_and_skeletonise_image_variant(skelbinary, size, False, method, True)
        #skel2 = rescale_and_skeletonise_image_variant(skelbinary, size, False, method, True, 40, True) 
        return(skel2)
    else:
        return(skimage.img_as_ubyte(skel1))


def dilate_image(image_path: str):
    """
    Dilates an image using disk(5)
    """

    image = skimage.img_as_ubyte(skimage.io.imread(image_path, as_gray=True))
    binary = np.array([np.array([True if px != 255 else False for px in row]) for row in image])
    selem = skimage.morphology.disk(1)
    binary = skimage.morphology.dilation(binary, selem)
    binary = skimage.util.invert(binary)
    skimage.io.imsave(image_path, binary)


def perimetric_complexity(image_file):
    """
    Credit to Justin Sulik: # https://github.com/justinsulik/pythonScripts/blob/master/perimetricComplexity.py

    Calculates perimetric complexity of an image,
    based on the Pelli algorithm as described here:
    http://www.mathematica-journal.com/2012/02/perimetric-complexity-of-binary-digital-images/
    See the above link for a more detailed discussion of the offsets used below.
    I've only tried this out on images with the contrast ramped up, so there's only black & white, no grey. 
    Citation: D. G. Pelli, C. W. Burns, B. Farell, and D. C. Moore-Page,
    “Feature Detection and Letter Identification,”
    Vision Research, 46(28), 2006 pp. 4646-4674.
    www.psych.nyu.edu/pelli/pubs/pelli2006letters.pdf.
    args: image_file (str) path to image file.
    """
    img = PIL.Image.open(image_file)
    
    # See link above for description of these offsets. 
    # Briefly, they represent various ways an image can be shifted by one pixel (up, up&right, right, right&down, etc.)
    offsets1 = [x for x in itertools.product([-1,1,0], repeat=2) if x != (0,0)]
    offsets2 = [x for x in offsets1 if abs(x[0]-x[1]) == 1]

    # Get 1-pixel perimeter
    offsets = []
    offsets.append(img)
    for x_offset, y_offset in offsets1:
        offsets.append(PIL.ImageChops.offset(img, x_offset, y_offset))
    composite = functools.reduce(lambda x,y: PIL.ImageChops.darker(x, y), offsets)
    perimeter = PIL.ImageChops.subtract(img,composite)
    perimeter = PIL.ImageChops.invert(perimeter)

    # Thicken perimeter to 3 pixels
    offsets = []
    for x_offset, y_offset in offsets2:
        offsets.append(PIL.ImageChops.offset(perimeter, x_offset, y_offset))
    composite = functools.reduce(lambda x,y: PIL.ImageChops.darker(x, y), offsets)
    composite = PIL.ImageChops.invert(composite)
    perimeter = PIL.ImageStat.Stat(composite).sum[0]/(255*3) #adjusting for the fact that 255 is the max value in the RGB color system, and that we'd thickened the perimeter to 3 pixels

    # Calculate ink area
    img = PIL.ImageChops.invert(img)
    inkArea = PIL.ImageStat.Stat(img).sum[0]/255 #adjusting for the fact that 255 is the max value in the RGB color system
    try:
        PC = perimeter**2/(inkArea*4*math.pi)
    except:
        PC = 0
    
    return PC,inkArea

