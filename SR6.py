#SR5
#Luis Diego Fernandez

import sys
import bmp_processor
import numpy as np

# image
image = bmp_processor.bmpImage(600,600)

print(image.get_bmp_processor_info())

#Decide color
image.glClearColor(0,0,0)
image.glColor(0,0,0)
image.glClear()

image_skeleton = image.glObjReader("obj/earth")
image.glLoadTextureImage('obj/earth',2,1)

#Load model
# pipeline: readImage -> loadTextures -> writeObject

def lowangle():

    print("lowangle")

    imageLow = bmp_processor.bmpImage(400,400)
    imageLow.glLoadTextureImage('obj/earth',2,1)

    imageLow.glClearColor(0,0,0)
    imageLow.glColor(0,0,0)
    imageLow.glClear()

    imageLow.glObjWriter(image_skeleton,700,0.5,0.65,0)
    imageLow.writeImage("earth-lowangle")

    print("\n")

def mediumshot():
    print("mediumshot")

    imageMid = bmp_processor.bmpImage(400,400)
    imageMid.glLoadTextureImage('obj/earth',2,1)

    imageMid.glClearColor(0,0,0)
    imageMid.glColor(0,0,0)
    imageMid.glClear()

    imageMid.glObjWriter(image_skeleton,600,0.5,0.5,0)
    imageMid.writeImage("earth-mediumshot")

    print("\n")

def highangle():
    print("highangle")

    imageHigh = bmp_processor.bmpImage(400,400)
    imageHigh.glLoadTextureImage('obj/earth',2,1)

    imageHigh.glClearColor(0,0,0)
    imageHigh.glColor(0,0,0)
    imageHigh.glClear()

    imageHigh.glObjWriter(image_skeleton,1200,0.5,0.25,0)
    imageHigh.writeImage("earth-highangle")

    print("\n")

if len(sys.argv) == 2:
    if str.lower(sys.argv[1]) == "low":
        lowangle()
    elif str.lower(sys.argv[1]) == "mid":
        mediumshot()
    elif str.lower(sys.argv[1]) == "high":
        highangle()
    elif str.lower(sys.argv[1]) == "all":
        lowangle()
        mediumshot()
        highangle()
    else:
        print("Es necesario un argumento valido, elija: low, mid, high o all")
else:
    print("Es necesario uno de los siguientes argumentos: low, mid, high o all")
