# in this library, we transform the variables from 'raw variables' to 'readytobeused' variables (for plotting for example)
import common
import numpy as np
import cv2
import scipy.io

#stops neuron variables at the end of the stimuli
def neurons_stimuli_end(neuron_vars, time_video, time_video_neuron, f0='median',start_delay = 0, end_delay = 0):
	background = neuron_vars['background']
	means = neuron_vars['means']
	time_video += end_delay
	print('time of stimulus: ',time_video)
	
	nb_frames = len(background)
	frame_rate = nb_frames/time_video_neuron

	print('frame_rate of recording = ', frame_rate)
	
	stimuli_end = int(time_video*frame_rate)
	stimuli_start = int(start_delay*frame_rate)
	#check if neuron video length is smaller than time_video:
	if stimuli_end>len(means[0]):
		print("recording shorter than",time_video,"s! Going to add zeros to the end")
	roismeans_avg = np.zeros(stimuli_end-stimuli_start)
	means_stim = []
	for mean in means:
		#substract background
		mean = dff0(mean,background,f0)
		means_stim.append(np.concatenate((mean,np.zeros(np.max((0,stimuli_end-len(mean))))))[stimuli_start:stimuli_end])
		#prepare averaging all the rois together
		roismeans_avg += means_stim[-1]
		
	#create the average between all rois
	roismeans_avg = roismeans_avg/len(means)
	
	return {'means':means_stim, 'background':np.concatenate((background,np.zeros(np.max((0,stimuli_end-len(background))))))[stimuli_start:stimuli_end], 'means_avg':roismeans_avg}

def vec_stimuli_end(vec,n):
	return np.concatenate((vec,np.zeros(np.max((0,n-len(vec))))))[:n]

def dff0(f,background,f0method):
	f = (f-background)
	if f0method == 'median':
		f0 = np.median(f)
	elif f0method == 'min':
		f0 = np.min(f)
	elif f0method == 'mean':
		f0 = np.mean(f)
	else:
		f0 = f[0]
	f = (f-f0)/f0
	return f
	
#process the stimuli frames: return the rotated/scaled/translated frames 
def stim_adjusting(stim_frames, mat):
	param = stim_param(mat)
	nb_fr = len(stim_frames[0,0,:])
	print()
	images = []
	for i in np.arange(0,nb_fr,1):
		im = 255*stim_frames[:,:,i]
		if angle == 90:
			im = np.rot90(im)
		images.append(im)
	return(images)

#aligns a vector to a chosen number n of frames
def time_aligned(x, n, array = False):
	times_float = np.linspace(0,len(x)-1,n)
	times = times_float.astype(int)
	list =  [x[i] for i in times]
	if array:
		list = np.asarray(list)
	return list

def resize(frames,f):
	new_frames = []
	for frame in frames:
		res = cv2.resize(frame,(int(frame.shape[1]*f),int(frame.shape[0]*f)))
		new_frames.append(res)
	return new_frames
	
def crop(frames,vec):
	new_frames = []
	for frame in frames:
		res = frame[int(frame.shape[0]*vec[0]):int(frame.shape[0]*vec[2])-1,int(frame.shape[1]*vec[1]):int(frame.shape[1]*vec[3])]
		new_frames.append(res)
	return new_frames
	
def resize_stim(frames,n):
	new_frames = []
	for frame in frames:
		x = frame
		for k in range(0,n,1):
			x = np.concatenate((x,frame))
		new_frames.append(x)
	return new_frames

#return a dictionnary of all the different parameters of stimuli
def stim_param(mat):
	smat = scipy.io.loadmat(mat)
	param = smat['param']
	if (len(param[0][0])>10):
		size_arena = param[0][0][10][0]
	else: size_arena = None
	return {'angle':param[0][0][6][0][0],
			'filename':param[0][0][0][0],
			'size_arena':size_arena,
			'xpos':int(param[0][0][2][0][0]),
			'ypos':int(param[0][0][3][0][0]),
			'dy':param[0][0][4][0][0],
			'dx':param[0][0][5][0][0],
			'frame_repetition':param[0][0][7][0][0]}