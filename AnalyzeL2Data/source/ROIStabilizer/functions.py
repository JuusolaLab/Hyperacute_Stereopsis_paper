import numpy as np
import cv2
import sys
sys.path.insert(1, "C:/Users/Diana/Documents/GitHub/analysis")
import matplotlib.pyplot as plt
import variabling as vr
import common

def correlation_coefficient(patch1, patch2):
    product = np.mean((patch1 - patch1.mean()) * (patch2 - patch2.mean()))
    stds = patch1.std() * patch2.std()
		
    if stds == 0:
        return 0
    else:
        product /= stds
        return product

def cross_corr(frame_piece, old_piece,points_rois):
	x1,x2,y1,y2 = points_rois[0],points_rois[2],points_rois[1],points_rois[3]

	im1 = common.gac(old_piece)['gray']
	sh_row, sh_col = im1.shape
	im2 = common.gac(frame_piece)['gray']

	d = (x2-x1)//2

	correlation = np.zeros((sh_row,sh_col))

	for i in range(d, sh_row - (d + 1)):
		for j in range(d, sh_col - (d + 1)):
			correlation[i, j] = correlation_coefficient(im1[y1:y2,x1:x2],
														im2[i - d: i + d,
															j - d: j + d])
															
	cv2.imshow("cross correlation", common.mat_to_frame(correlation,scaling = True,bits = 16))

def stab_frame(frame_piece, old_piece, lk_params,x1,x2,y1,y2,old_tx,old_ty,out_trans,method = 'frame_to_frame',dist_tresh = 10000):
	# Create some random colors
	color = np.random.randint(0,255,(200,3))
	old_gray = common.gac(old_piece)['gray']
	old_piece = common.gac(old_piece)['color']
	
	
	p0 = None
	min_features = 1
	qlevel = 1
	#p0 is for the old frame. If oldframe is the same (as in the first frame), then it is useless to recalculate p0 all the time
	while p0 is None or len(p0)<min_features:
		qlevel -= 0.1
		# params for ShiTomasi corner detection
		feature_params = dict( maxCorners = 100,qualityLevel = qlevel, minDistance = 15, blockSize = 15 )
		p0 = cv2.goodFeaturesToTrack(old_gray[int(y1):int(y2),int(x1):int(x2)], mask = None, **feature_params)

	# Create a mask image for drawing purposes
	mask = np.zeros_like(old_piece)
	frame_gray = common.gac(frame_piece)['gray']
	frame_piece = common.gac(frame_piece)['color']
	
	frame_piece2 = np.copy(frame_piece)

	# calculate optical flow
	p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray[int(y1):int(y2),int(x1):int(x2)], frame_gray[int(y1):int(y2),int(x1):int(x2)], p0, None, **lk_params)
	# Select good points
	good_new = p1[st==1]
	good_old = p0[st==1]
	# draw the tracks
	tx = 0
	ty = 0 
	#print(good_new,good_old)
	for i,(new,old) in enumerate(zip(good_new,good_old)):
		a,b = new.ravel()
		c,d = old.ravel()
		mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
		frame_piece = cv2.circle(frame_piece,(int(c+x1),int(d+y1)),1,color[i].tolist(),-1)
		frame_piece = cv2.circle(frame_piece,(int(a+x1),int(b+y1)),1,color[2*i].tolist(),-1)
		tx += c-a
		ty += d-b
	
   # img = cv2.add(frame,mask)
	img = frame_piece
	tx = 1*tx/(i+1)
	ty = 1*ty/(i+1)
	out_trans.write(str(tx)+' '+str(ty))
	out_trans.write("\n")
	num_rows, num_cols = img.shape[:2]
	if method == 'frame_to_frame':
		translation_matrix = np.float32([ [1,0,int(tx+old_tx)], [0,1,int(ty+old_ty)] ])
		old_tx += tx
		old_ty += ty
	else:
		if np.abs((tx-old_tx)**2+(ty-old_ty)**2)<dist_tresh:
			translation_matrix = np.float32([ [1,0,int(tx)], [0,1,int(ty)] ])
			old_tx = tx
			old_ty = ty
		else:
			print('big difference in translation!!')
			translation_matrix = np.float32([ [1,0,int(old_tx)], [0,1,int(old_ty)] ])
	img = cv2.warpAffine(img, translation_matrix, (num_cols, num_rows))
	img2 = cv2.warpAffine(frame_piece2, translation_matrix, (num_cols, num_rows))
	
	return {'img':img, 'img2':img2, 'old_tx':old_tx,'old_ty':old_ty}
	
def stab_video(x1,x2,y1,y2,neuron,rois,method = 'frame_to_frame',window_frac = 1,time_frame0 = 0,num_frame0 = 0,crop=[0,1,0,1,0.25,0.6]):
	frames = vr.get_frames(neuron,crop)
	time_video = vr.get_time_video(rois,neuron)
	if rois is None:
		file = open('.'.join(neuron.split('.')[0:-1])+'.txt','w') 
		file.write('1 '+str(time_video))
		file.close()
	frame_rate = len(frames)/time_video
	frame_height = frames.shape[1]
	frame_width = frames.shape[2]
	print('frame rate is ',frame_rate)
	print(frame_height)
	fourcc = cv2.VideoWriter_fourcc('P','I','M','1')
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	x1 = int(0+window_frac*frame_width)
	x2 = int(frame_width-window_frac*frame_width)
	y1 = int(0+window_frac*frame_height)
	y2 = int(frame_height-window_frac*frame_height)
	
	old_frame_index = 0
	old_frame = frames[0]
	if method == 'from_maxframe':
		mf = vr.max_frame(frames)
		old_frame_index = mf['index']
		old_frame = mf['frame']
	if method == 'from_timeframe0':
		old_frame_index = int(time_frame0*frame_rate)
		old_frame = frames[old_frame_index]
	if method == 'from_numframe0':
		old_frame_index = num_frame0
		old_frame = frames[old_frame_index]
	print('frame0 :',old_frame_index)

	id = neuron.split('/')[-1].split('.')[0]+'_frame'+str(old_frame_index)
	out = cv2.VideoWriter('C:/Users/Diana/Desktop/Data Analysis/'+id+'_stab.avi',fourcc, fps=frame_rate, frameSize=(frame_width,frame_height))
	out2 = cv2.VideoWriter('C:/Users/Diana/Desktop/Data Analysis/'+id+'_stabcomb.avi',fourcc, fps=frame_rate, frameSize=(frame_width,2*frame_height))
	# Take first frame and find corners in it
	# Parameters for lucas kanade optical flow
	lk_params = dict( winSize  = (frame_width,frame_height),maxLevel = 10, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10000, 0.03))

		


		#img = cv2.circle(img,(int(frame_width/2),int(frame_height/2)),5,color[i-1].tolist(),-1)
		#img = cv2.circle(img,(int(frame_width/2+tx),int(frame_height/2+ty)),5,color[i].tolist(),-1)


	i = 0
	old_tx = 0
	old_ty = 0
	mean_tx = 0
	mean_ty = 0
	txs = []
	tys = []
	out_trans = open('C:/Users/Diana/Desktop/Data Analysis/'+id+'_trans.txt', "w")

	old_frame =  common.mat_to_frame(old_frame,scaling=True)
	old_frame = common.to8(old_frame)
	if method != 'frame_to_frame':
		cv2.imshow("reference frame", old_frame)
		cv2.waitKey(0)
	rois_search = vr.auto_means(common.mat_to_frame(old_frame,bits = 16),40,40,12,1,bkgpos=[0,0],plot=True,scaling_bar=False) #bkgpos:[down,right]; rois:16,16,12 usually
	points_rois = rois_search['points'][1]
	print(points_rois)
	for i in range(0,len(frames)):
		frame = frames[i]
		frame =  common.mat_to_frame(frame,scaling=True)
		frame = common.to8(frame)
		frame = common.gac(frame)['color']
		if i == 0:
			dist_tresh = 100000
		else:
			dist_tresh = 10000
		sf = stab_frame(frame,old_frame,lk_params,x1,x2,y1,y2,old_tx,old_ty,out_trans,method = method,dist_tresh = dist_tresh)

		cross_corr(frame, old_frame,points_rois)
		old_tx = sf['old_tx']
		old_ty = sf['old_ty']
		mean_tx+=sf['old_tx']
		mean_ty+=sf['old_ty']
		txs.append(sf['old_tx'])
		tys.append(sf['old_ty'])
		if method == 'frame_to_frame':
			old_frame = frame
		img = sf['img']
		img2 = sf['img2']
		combined = np.concatenate((frame,img), axis=0)
		i = i+1
		out.write(img2)
		out2.write(combined)
		cv2.imshow('frame',combined)
		k = cv2.waitKey(1) & 0xff
		if k == 27:
			break
	#test2
		# Now update the previous frame and previous points
		#old_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).copy()
		#p0 = good_new.reshape(-1,1,2)
	mean_tx = mean_tx/len(txs)
	mean_ty = mean_ty/len(tys)
	distances = np.abs((np.array(txs)-mean_tx)**2+(np.array(tys)-mean_ty)**2)
	index = np.argmin(distances)
	indexes = np.argsort(distances)
	out_trans.close()
	out.release()
	cv2.destroyAllWindows()
	plt.plot(np.arange(0,len(distances))/frame_rate,distances)
	plt.ylabel('time')
	plt.ylabel('distances translations vs average trans')
	plt.show()
