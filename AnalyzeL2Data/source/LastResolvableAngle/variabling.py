#in this library, we put into variables all the information we get from the files used by the user

import numpy as np 
import cv2
import scipy.io
import common as c
import os
from imageio import volread
import tifffile as tiff

input_path = c.input_path
output_path = c.output_path

#parse arena file: returns the x and y coordinates of each posts, their widths and heights
def parse_arena(arena):
	res = []
	with open(arena, 'r') as f:
		data = f.readlines()
	for line in data[:-1]:
		numbers = line.split()
		numbers = np.asarray(numbers)
		numbers = numbers.astype(float)
		res.append(numbers)
	return res

#parse rois file: returns a list of coordinates for each ROI rectangle
def parse_rois(rois):
	res = []
	with open(rois, 'r') as f:
		data = f.readlines()
	params = data[0].split()
	params = np.asarray(params)
	params = params.astype(float)
	res.append(params)
	for line in data[1:]:
		numbers = line.split()
		numbers = np.asarray(numbers)
		numbers = numbers.astype(int)
		numbers[2] += numbers[0]
		numbers[3] += numbers[1]
		res.append(numbers)
	return res
	
#parse trans file: returns two lists of coordinates for neurons translation
def parse_trans(trans):	
	x = []
	y = []
	with open(trans, 'r') as f:
		data = f.readlines()
	for line in data:
		numbers = line.split()
		numbers = np.asarray(numbers)
		numbers = numbers.astype(float)
		x.append(numbers[0])
		y.append(numbers[1])
	return {'x':x,'y':y}
		

#process the neuron file: returns the means of each ROI and the frames of the neuron video
def neuron_vars(neuron_frames,pts):
	if neuron_frames is None:
		print ('No neurons')
		return ({'background':np.ones(100),'means':[np.ones(100)], 'frames':[np.ones((2,2)) for i in range(100)], 'neuron_name':'no neuron'})
	
	nb_frames = len(neuron_frames)
	print('nbf: (full recording)',nb_frames)
	means = []
	if c.type_of_image(neuron_frames[0]) == 'color':
		for i in pts:
			means.append(np.zeros(nb_frames))
		for j in range(0,nb_frames):
			i=0
			for pt in pts:
				gray = cv2.cvtColor(neuron_frames[j], cv2.COLOR_BGR2GRAY)
				means[i][j] = gray[max(0,pt[1]):pt[3],max(0,pt[0]):pt[2]].mean()
				i+=1
	else:
		for pt in pts:
			gray = np.asarray(neuron_frames)
			means.append(np.mean(gray[:,max(0,pt[1]):pt[3],max(0,pt[0]):pt[2]],axis=(1,2)))

	return({'background':means[0],'means':means[1:]})
	
def get_frames(neuron,crop=None):
	if neuron is None:
		print ('Warning: no neuron file!!!')
		return None
	type = neuron.split('.')[-1]
	print('video type: ',type)
	if type=='avi':
		cap = cv2.VideoCapture(neuron)
		frame_width = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		frame_height = int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
		nb_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		frames = []
		while(cap.isOpened()):
			
			ret, frame = cap.read()
			try: 
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			except:
				break
			
			frames.append(frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		cap.release()
		cv2.destroyAllWindows()
		frames = np.asarray(frames)
	elif type=='tif':
		frames = c.read_tiffstacks(neuron,crop)
	else:
		print('neuron type unknown')
		frames = None
	return(frames)
	


def max_frame(frames,method = 'sum'):
	max_brightness = 0
	max_index = 0
	#print(cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY))
	for i in range(0,len(frames)):
		if c.type_of_image(frames[i]) == 'color':
			gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
		else:
			gray = frames[i]
		if method == 'sum':
			if max_brightness<gray.sum():
				max_brightness = gray.sum()
				max_index = i
		elif method == 'median':
			if max_brightness<np.median(gray):
				max_brightness = np.median(gray)
				max_index = i
		elif method == 'max':
			if max_brightness<gray.max():
				max_brightness = gray.max()
				max_index = i
		else:
			print('Warning: method for max_frame doesnt make sense')
	return {'frame':frames[max_index],'index':max_index}


def get_time_video(rois,neuron):
	if neuron is None:
		print('No neuron file here... Arbitrary chosen: 42s')
		return 42
	if rois is None:
		type = neuron.split('.')[-1]
		if type =='tif':
			print('tif metadata time: ',c.read_tiff_timevideo(neuron),'s')
			return c.read_tiff_timevideo(neuron)
		if type == 'avi':
			cap = cv2.VideoCapture(neuron)
			frame_rate = float(cap.get(cv2.CAP_PROP_FPS))
			nb_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
			print('avi calculated time: ',nb_frames/frame_rate,'s')
			return nb_frames/frame_rate
		else:
			print('type of neuron file not known, cannot calculate time video')
	positions_rois = [[0]]
	try:
		positions_rois = parse_rois(rois)
	except:
		print('cannot parse rois file')
	if (len(positions_rois[0])>1):
		time_video = positions_rois[0][1]
		print('time_video from roi file: ', positions_rois[0][1],'s')
	else:
		time_video = 42
		print('arbitrary chosen: ', time_video,'s')
	return time_video
def rois_means(rois):
	positions_rois = parse_rois(rois)
	pos_neu = positions_rois[1]
	pos_neu[2] = pos_neu[0]
	pos_neu[3] = pos_neu[1]
	pts = []
	for pos_roi in positions_rois[2:]:
		pts.append(np.zeros(4))
		pts[-1] = pos_roi-pos_neu
	return pts
	
def auto_means(frame,dx,dy,mindist,n,sorting = 'hor',size=40,cpx1=0,cpx2=1,bkgpos=[0,0],plot=True,scaling_bar=True):
	if frame is None:
		return {'points':None,'frame':None}
	if c.type_of_image(frame) == 'color':
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	else:
		gray = frame.copy()
		frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
	gray2 = gray
	means = np.zeros( (gray2.shape[0]-dx, gray2.shape[1]-dy) )
	for i in range(0,means.shape[0]):
		for j in range(0,means.shape[1]):
			means[i][j]=gray2[i:(i+dx),j:(j+dy)].mean()
	x = np.zeros(n)
	y = np.zeros(n)
	for i in range(0,n):
		print('mean for ROI',i)
		amax = means.argmax()
		x[i] = amax % means.shape[1]
		y[i] = (amax-x[i])/means.shape[1]
		for a in range(-mindist,mindist):
			d = int(np.sqrt(mindist**2-a**2))
			for b in range(-d,d):
				gray2[min(gray2.shape[0]-1,max(0,int(y[i]+dy/2+a))),min(gray2.shape[1]-1,max(0,int(x[i]+dx/2+b)))] = 0
		for i in range(0,means.shape[0]):
			for j in range(0,means.shape[1]):
				means[i][j]=gray2[i:(i+dx),j:(j+dy)].mean()
		#check if each neuron is well selected:
		#cv2.imshow("output", gray2)
		#cv2.waitKey(0)
	#list the points for each roi, and sort if necessary
	pts = []
	for i in range(0,n):
		pts.append([int(x[i]),int(y[i]),int(x[i])+dx, int(y[i])+dy])
	if sorting == 'hor':
		pts.sort(key = sortFirst)
	elif sorting == 'ver':
		pts.sort(key = sortSecond)
	else: print('Warning: sorting value makes no sense bro!')
	pts.insert(0,c.bkg_pos(size,bkgpos,frame.shape))
	frame = c.mat_to_frame(frame,scaling = True)
	frame = c.to8(frame)
	
	#displays image with rois
	output = frame.copy()
	# loop over the (x, y) coordinates and radius of the circles
	cv2.rectangle(output, (pts[0][0], pts[0][1]), (pts[0][2], pts[0][3]), (255,255,255), 2)
	i = 0
	for pt in pts[1:]:
		cv2.rectangle(output, (pt[0], pt[1]), (pt[2], pt[3]), c.colorsRGB_unlim(i), 2)
		i+=1
	#add scaling bar
	if scaling_bar:
		prec = int((cpx2-cpx1)*20)
		for i in range(0,prec):
			cv2.putText(frame, '|',(int(i/prec*frame.shape[1]),frame.shape[0]),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(200,200,200))
			cv2.putText(frame, str(c.trunc(cpx1+i/prec*(cpx2-cpx1),2)),(int(i/prec*frame.shape[1])+5,frame.shape[0]-5),cv2.FONT_HERSHEY_COMPLEX_SMALL,.5,(200,200,200))
	# show the output image
	image = np.hstack([frame, output])
	if plot:
		cv2.imshow("output", image)
		cv2.waitKey(0)
	return {'points':pts,'frame':image}
	
def fast_auto_means(frame,ds,n,sorting = 'hor',size=40,cpx1=0,cpx2=1,bkgpos=[0,0],plot=True,scaling_bar=True):
	if frame is None:
		return {'points':None,'frame':None}
	if c.type_of_image(frame) == 'color':
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	else:
		gray = frame.copy()
		frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
		
	gray2 = gray[:(gray.shape[0]-gray.shape[0]%ds),:(gray.shape[1]-gray.shape[1]%ds)]
	means = np.zeros((int(gray2.shape[0]/ds), int(gray2.shape[1]/ds)))

	for i in range(means.shape[0]):
		for j in range(means.shape[1]):
			means[i,j] = gray2[i*ds:(i+1)*ds,j*ds:(j+1)*ds].mean()
			
	indices = (-means).argpartition(n, axis=None)[:n]

	y, x = np.unravel_index(indices, means.shape)

	pts = []
	for i in range(0,n):
		pts.append([x[i]*ds,y[i]*ds,x[i]*ds+ds, y[i]*ds+ds])
	if sorting == 'hor':
		pts.sort(key = sortFirst)
	elif sorting == 'ver':
		pts.sort(key = sortSecond)
	else: print('Warning: sorting value makes no sense bro!')
	pts.insert(0,c.bkg_pos(size,bkgpos,frame.shape))
	frame = c.mat_to_frame(frame,scaling = True)
	frame = c.to8(frame)
	
	#displays image with rois
	output = frame.copy()
	# loop over the (x, y) coordinates and radius of the circles
	cv2.rectangle(output, (pts[0][0], pts[0][1]), (pts[0][2], pts[0][3]), (255,255,255), 2)
	i = 0
	for pt in pts[1:]:
		cv2.rectangle(output, (pt[0], pt[1]), (pt[2], pt[3]), (0,0,0), 2)
		i+=1
	#add scaling bar
	if scaling_bar:
		prec = int((cpx2-cpx1)*20)
		for i in range(0,prec):
			cv2.putText(frame, '|',(int(i/prec*frame.shape[1]),frame.shape[0]),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(200,200,200))
			cv2.putText(frame, str(c.trunc(cpx1+i/prec*(cpx2-cpx1),2)),(int(i/prec*frame.shape[1])+5,frame.shape[0]-5),cv2.FONT_HERSHEY_COMPLEX_SMALL,.5,(200,200,200))
	# show the output image
	image = np.hstack([frame, output])
	if plot:
		cv2.imshow("output", image)
		cv2.waitKey(0)
	return {'points':pts,'frame':image}
	


def sortFirst(val):
	return val[0]
def sortSecond(val):
	return val[1]
	
#import gui4 as gui
#f0 = get_frames(gui.neuron)
#f2 =  get_frames(gui.tif)
#print(len(f0),len(f2),f0[0].shape,f2[0].shape)
#print(c.mat_to_frame(c.std(f0),bits = 16))
#auto_means(c.mat_to_frame(c.std(f0),bits = 16),18,18,15,6,bits = 16)
#neuron_vars(f0,auto_means(max_frame(f0)['frame'],18,18,15,6,bits = 16)['points'],42)
#process the stimuli mat file: returns the frames 
def stim_vars(stim_mat):
	stimuli = scipy.io.loadmat(stim_mat)
	video_stim = stimuli['video']
	nb_fr = len(video_stim[0,0,:])
	images = []
	for i in np.arange(0,nb_fr,1):
		im = 255*video_stim[:,:,i]
		images.append(im)
	return(images)

#process the mat file: returns everything that is related to it
def ball_vars(mat):
	smat = scipy.io.loadmat(mat)
	df = smat['SEdata']
	param = smat['param']
	stim_filename = param[0][0][0][0]
	stim_angle = param[0][0][6][0][0]
	if (len(param[0][0])>10):
		size_arena = param[0][0][10][0]
	else: size_arena = None
	sample_rate = 4000
	time_stimulus = len(df[:,0])/sample_rate
	#opposite sign for forward component
	df[:,1] = -df[:,1]
	#in radians
	df[:,3] = 3.14/180*df[:,3]
	diameter = .006
	cumsum = np.cumsum(df,axis = 0)

	y = np.zeros(len(df))
	x = np.zeros(len(df))
	dir = np.zeros(len(df))

	for i in np.arange(0,len(df)-1,1):
		dir[i+1] = dir[i] + df[i,3]
		x[i+1] = x[i] + df[i,1]*1000*3.14/360*diameter*np.cos(dir[i+1]) - df[i,2]*1000*3.14/360*diameter*np.sin(dir[i+1])
		y[i+1] = y[i] + df[i,1]*1000*3.14/360*diameter*np.sin(dir[i+1]) + df[i,2]*1000*3.14/360*diameter*np.cos(dir[i+1])
	
	if (os.path.isfile(input_path+'Track ball/Stimuli/'+stim_filename)):
		images = stim_vars(input_path+'Track ball/Stimuli/'+stim_filename)
	else:
		print('cannot find stimulus in '+input_path+'Track ball/Stimuli/'+stim_filename)
		images = []
	
	return {'df':df, 'cumsum':cumsum, 'x':x, 'y':y, 'dir':dir, 'stim_video':images, 'stim_angle':stim_angle, 'stim_filename':stim_filename, 'time_stimulus':time_stimulus, 'size_arena':size_arena}

#read and write video into a list of frames: applicable for central video, stimuli video,... 
def video_vars(video):
	if video is None:
		return [np.ones((2,2)) for i in range(100)]
	images = []
	cap = cv2.VideoCapture(video)
	while(cap.isOpened()):
		ret, frame = cap.read()
		try: 
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		except:
			break
		images.append(frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	cap.release()
	cv2.destroyAllWindows()
	return images
	
