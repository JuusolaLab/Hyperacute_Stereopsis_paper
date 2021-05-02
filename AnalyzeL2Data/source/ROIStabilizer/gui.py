from tkinter import *
import tkinter.filedialog
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.widgets as widgets
import numpy as np
import cv2
from functions import *
import sys
sys.path.insert(1, "C:/Users/Diana/Documents/GitHub/analysis")
import gui4 as gui

vars = gui.Get_files(None).get_vars()
neuron = vars['neuron']
mat = vars['mat']
neuron = vars['neuron']
rois = vars['rois']
video = vars['video']
trans = vars['trans']
find_roi = vars['find_roi']
fly_path = vars['fly_path']

def onselect(eclick, erelease):
	global x1,x2,y1,y2
	if eclick.ydata>erelease.ydata:
		eclick.ydata,erelease.ydata=erelease.ydata,eclick.ydata
	if eclick.xdata>erelease.xdata:
		eclick.xdata,erelease.xdata=erelease.xdata,eclick.xdata
	x1,y1,x2,y2=eclick.xdata,eclick.ydata,erelease.xdata,erelease.ydata


def handle_close(evt):
	print(x1,x2,y1,y2)
	print('Closed Figure!')
	stab_video(cap,x1,x2,y1,y2,filename,method = 'from_timeframe0')
root = Tk()
root.withdraw()

print('neuron: ',neuron.split('/')[-1].split('.')[0])
print('rois: ',rois)
#stab_video(0,0,0,0,neuron,rois,method = 'from_timeframe0', window_frac = 0, time_frame0 = 27)
#stab_video(0,0,0,0,neuron,rois,method = 'from_numframe0', window_frac = 0, num_frame0 = 374)
stab_video(0,0,0,0,neuron,rois,method = 'from_maxframe', window_frac = 0)
#stab_video(0,0,0,0,neuron,rois,method = 'frame_to_frame', window_frac = 0)

#select ROI
#frame = max_frame(get_frames(filename))['frame']

#x1,x2,y1,y2=0,0,0,0



#fig = plt.figure()
#ax = fig.add_subplot(111)

#fig.canvas.mpl_connect('close_event', handle_close)

#im = Image.open(filename)
#arr = np.asarray(frame)
#plt_image=plt.imshow(arr)
#cap = cv2.VideoCapture(filename)
#ret,frame = cap.read()
#rs=widgets.RectangleSelector(
 #   ax, onselect, drawtype='box',
  #  rectprops = dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True))
#plt.show()

	