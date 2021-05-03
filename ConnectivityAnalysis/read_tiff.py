from skimage import io
import numpy as np
import matplotlib.pyplot as plt


test_file = r"C:\Users\James\Desktop\gal4 images\VT047848-20171020_66_I1-f-40x-Brain-GAL4-JRC2018_Unisex_20x_HR-8235457-aligned_stack.tif"

def read_image(fname):
	im = io.imread(fname)
	print(im.shape)
	return im
# generally files laid out as z, y, x, c

def threshold(array, threshold):
	threshed = array > threshold
	return threshed * 255


def show_thresholded_image(im_stack, thresh):
	
	threshed = threshold(im_stack, thresh)
	plt.imshow(threshed[50,:,:])
	plt.show()


def pipe_line(fname):
	image = read_image(fname)
	threshed = threshold(image[:,:,:,0:4], 200)
	io.imsave(fname + "_thresholded.tiff")
