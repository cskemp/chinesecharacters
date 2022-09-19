#coding=utf-8
import numpy as np
import os
import skimage 

import caffe
import pandas as pd

def get_crop_image(imagepath, img_name):	
    img=skimage.io.imread(imagepath + img_name,as_grey=True)
    black_index = np.where(img < 255 )
    min_x = min(black_index[0])
    max_x = max(black_index[0])
    min_y = min(black_index[1])
    max_y = max(black_index[1])
    #print(min_x,max_x,min_y,max_y)
    image = caffe.io.load_image(imagepath+"//"+img_name)
    return image[min_x:max_x, min_y:max_y,:]


def evaluate(net, imagepath):
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2,0,1))
    transformer.set_raw_scale('data', 255)

    allimage=os.listdir(imagepath)

    count = 0
    total = len(allimage)
    rows = []
    errors = []
    for img_name in allimage:

        try:
            image = get_crop_image(imagepath,img_name)
            net.blobs['data'].data[...] = transformer.preprocess('data',image)
            _ = net.forward()

            character, period, image_id, dataset = img_name.split(".")[0].split("_")
            rows.append((character, period, image_id, dataset, list(net.blobs['cls3_fc1'].data[0])))
        except:
            print("ERROR")
            errors.append((character, period, image_id, dataset))

        count += 1
        print(count, total)
    
    df = pd.DataFrame(rows, columns=["character", "period", "image_id", "dataset", "fc1_embedding"])
    df.to_csv("hccr_embeddings.csv")

    edf = pd.DataFrame(errors, columns=["character", "period", "image_id", "dataset"])
    edf.to_csv("errors.csv")

if __name__ == '__main__':

    net_file = 'googlenet_deploy.prototxt'
    caffe_model = 'googlenet_hccr.caffemodel' 
    net = caffe.Net(net_file,caffe_model,caffe.TEST)

    imagepath='distinctiveness_images/'
    #imagepath = "images/"
    evaluate(net, imagepath)