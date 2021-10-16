# https://github.com/justinsulik/pythonScripts/blob/master/perimetricComplexity.py

from PIL import Image, ImageChops, ImageStat
import itertools, functools, os, fnmatch, re, pickle, math
#PIL can be difficult to install with pip. Try pip install Pillow instead.

def perimetricComplexity(image_file):
    """
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
    img = Image.open(image_file)
    
    # See link above for description of these offsets. 
    # Briefly, they represent various ways an image can be shifted by one pixel (up, up&right, right, right&down, etc.)
    offsets1 = [x for x in itertools.product([-1,1,0], repeat=2) if x != (0,0)]
    offsets2 = [x for x in offsets1 if abs(x[0]-x[1]) == 1]

    # Get 1-pixel perimeter
    offsets = []
    offsets.append(img)
    for x_offset, y_offset in offsets1:
        offsets.append(ImageChops.offset(img, x_offset, y_offset))
    composite = functools.reduce(lambda x,y: ImageChops.darker(x, y), offsets)
    perimeter = ImageChops.subtract(img,composite)
    perimeter = ImageChops.invert(perimeter)

    # Thicken perimeter to 3 pixels
    offsets = []
    for x_offset, y_offset in offsets2:
        offsets.append(ImageChops.offset(perimeter, x_offset, y_offset))
    composite = functools.reduce(lambda x,y: ImageChops.darker(x, y), offsets)
    composite = ImageChops.invert(composite)
    perimeter = ImageStat.Stat(composite).sum[0]/(255*3) #adjusting for the fact that 255 is the max value in the RGB color system, and that we'd thickened the perimeter to 3 pixels

    # Calculate ink area
    img = ImageChops.invert(img)
    inkArea = ImageStat.Stat(img).sum[0]/255 #adjusting for the fact that 255 is the max value in the RGB color system
    try:
        PC = perimeter**2/(inkArea*4*math.pi)
    except:
        PC = 0
    
    return PC,inkArea