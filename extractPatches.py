'''
Reference: http://geospatialpython.com/2011/01/point-in-polygon.html
	   http://okomestudio.net/biboroku/?p=986
Script extracts patches from the images and polygon coordinates provided in the xml file
Images and xml files should be placed in the current working directiory
Create a directory with results to save the patches
tolerance: percentage of pixels in path that can overlap with background pixels
Usage:
python <scriptName>.py patch_h patch_y stride_h stride_w tolerance
'''
import xml.etree.ElementTree as ET
from lxml import etree
from PIL import Image
import numpy as np
import argparse
import glob,os
import re
import sys

# function to check given coordinate lies within polygon
def point_in_poly(x,y,poly):
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

#update patch size here
patch_h=int(sys.argv[1])
patch_w=int(sys.argv[2])
stride_h=int(sys.argv[3])
stride_w=int(sys.argv[4])
tolerance=int(sys.argv[5])
fpath='sample'

# reading the files within the directory
files = glob.glob('*xml')
debug=0

print  "filename"," Number of pateches patches extracted"
for infile in files:
		file, ext = os.path.splitext(infile)
		imfile=file+".jpg"
		tree = ET.parse(infile)
		root = tree.getroot()
		img = Image.open(imfile)

		xc=[]
		yc=[]
		coordinate = []
		for object in root:
			for polygon in object:
				for xy in polygon.findall('pt'):
					x=xy.find('x').text
					y=xy.find('y').text
					coordinate.append((int(x),int(y)))
					xc.append(int(x))
					yc.append(int(y))
		xmin=np.min(xc)
		xmax=np.max(xc)
		ymin=np.min(yc)
		ymax=np.max(yc)
		
		# extracting the 
		img2=img.crop((xmin,ymin,xmax,ymax))
		if debug >0:
			print img2.size[0],img2.size[1]

		# creating an array in which coordinates inside polygon equal to 1 and background to 0
                imgbw=np.zeros((img.size[0],img.size[1]))
                for i in range(xmin,xmax):
                        for j in range(ymin,ymax):
                                if point_in_poly(int(i),int(j),coordinate):
                                        imgbw[i,j]=1

		fileName=re.split('(\d+)',file)
		count=0
		# saving the patches
		for i in range(0,(xmax-xmin)/stride_w):
			for j in range(0,(ymax-ymin)/stride_h):
				# calculating coordinates of the patch
				pointx_min=xmin+j*stride_w
				pointy_min=ymin+i*stride_h
				pointx_max=pointx_min+patch_w
				pointy_max=pointy_min+patch_h
				
				foregroundPixelCount=patch_w*patch_h*((100-tolerance)/100)
				# saving the patch if it meets all the conditions
				if np.sum(imgbw[pointx_min:pointx_max,pointy_min:pointy_max]) == foregroundPixelCount:
					img3=img.crop((xmin+j*stride_h,ymin+i*stride_w,xmin+j*stride_h+patch_h,ymin+i*stride_w+patch_w))
					outfile="results/"+fileName[1]+fileName[2]+"P"+str(i+j)+".jpg"
					img3.save(outfile)
					count+1
		print infile

