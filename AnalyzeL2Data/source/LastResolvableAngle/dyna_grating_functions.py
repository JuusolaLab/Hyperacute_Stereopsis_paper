import numpy as np
import re
import cv2
import numpy.fft as fft
import matplotlib.pyplot as plt
def res_formula(trace,pmax1,pmax2,f0):
	pmin = min(pmax1,pmax2)+np.argmin(trace[min(pmax1,pmax2):(max(pmax1,pmax2)+1)])
	low = min(trace[pmin],f0)
	return (min(trace[pmax1],trace[pmax2])-trace[pmin])/(max(trace[pmax1],trace[pmax2])-low)

def res_formula_noise(trace,pmax1,pmax2,f0,thresh,count_lim,a):
	pmin = min(pmax1,pmax2)+np.argmin(trace[min(pmax1,pmax2):(max(pmax1,pmax2)+1)])
	motif = ''
	count = check_noise(trace[pmax1:pmin],a*(trace[pmax1]-trace[pmin]))+check_noise(trace[pmin:pmax2],a*(trace[pmax2]-trace[pmin]))
	if count>=1:
		motif = str(count)+' interpeaks! '
	if count>=count_lim:
		value = 0
	elif min(trace[pmax1],trace[pmax2])-trace[pmin]<thresh:
		value = 0
		motif+='smallest peak within noise margin'
	else:
		value = res_formula(trace,pmax1,pmax2,f0)
	return {'value':value,'motif':motif}
def resolvability(xaxis,trace,pmax):
	pmax1 = min(range(len(xaxis)), key=lambda i: abs(xaxis[i]-pmax[0]))
	pmax2 = min(range(len(xaxis)), key=lambda i: abs(xaxis[i]-pmax[1]))
	pmin = min(pmax1,pmax2)+np.argmin(trace[min(pmax1,pmax2):(max(pmax1,pmax2)+1)])
	resol = res_formula(trace,pmax1,pmax2,np.median(trace))
	return {'resol':resol, 'pmax1':pmax1,'pmax2':pmax2,'pmin':pmin}

def check_noise(trace,thresh):
	if len(trace)<3:
		return 0
	if trace[-1]-trace[0]==0:
		return 0
	count = 0
	opposite_dir = False
	sign = (trace[-1]-trace[0])/np.abs(trace[-1]-trace[0])
	yref = trace[0]
	for i in range(0,len(trace)-1):
		#when following the right way, check if it starts going the wrong way
		if not opposite_dir and sign*(trace[i+1]-trace[i])<0:
			#check if the trace followed the right way enough. If not, we don't update yref
			if sign*(trace[i]-yref)>0:
				yref = trace[i]
			opposite_dir = True
		#when following the wrong way, check if it starts going the right way
		if opposite_dir and sign*(trace[i+1]-trace[i])>0:
			if np.abs(trace[i]-yref)>thresh:
				count += 1
			opposite_dir = False
	return count

def allres(trace,times,f0,thresh,count_lim = 1,a=.6):
	values = np.zeros(len(times)-1)
	motifs = []
	for i in np.arange(0,len(values)):
		res = res_formula_noise(trace,times[i],times[i+1],f0,thresh,count_lim,a)
		values[i] = res['value']
		motifs.append(res['motif'])
	return {'values':values,'motifs':motifs}

def last_res_index(allres,err_lim,conseq_lim,invert=False):
	if invert:
		allres = allres[::-1]
	err = 0
	k = 0
	while k<len(allres) and err<err_lim:
		if allres[k]==0:
			err+=1
		k+=1
	index1 = k-1
	index2 = index1
	conseq = 0
	while k<len(allres):
		if allres[k]==0:
			conseq=0
		else:
			conseq+=1
		if conseq>=conseq_lim:
			index2=k
		k+=1
	if invert:
		return [len(allres)-index1,len(allres)-index2]
	return [index1,index2]
	
def peaks_time_interval(stim_filename):
	num = re.findall("\d+", stim_filename)
	bars_angle_thickness = int(num[0])/10
	bars_angle_sep = int(num[1])/10
	bars_angle_speed = 30/int(num[2])
	dtgauss = (bars_angle_sep+bars_angle_thickness)/bars_angle_speed
	return dtgauss
	
def gradient_pmax(xaxis,trace,dt):
	diff = np.gradient(trace)
	pmax1 = xaxis[np.argmax(diff)]+1
	res1 = {'resol':0, 'pmax1':0,'pmax2':0,'pmin':0}
	res2 = {'resol':0, 'pmax1':0,'pmax2':0,'pmin':0}
	if pmax1-dt>0:
		res1 = resolvability(xaxis,trace,[pmax1,pmax1-dt])
	if pmax1+dt<xaxis[-1]:
		res2 = resolvability(xaxis,trace,[pmax1,pmax1+dt])
	if res1['resol']>res2['resol']:
		return res1
	return res2
	
def detect_peaks(trace,prec):
	times = []
	diff = np.gradient(trace)
	for t in range(1,len(diff)):
		if diff[t-1]>0 and diff[t]<0 and diff[t-1]-diff[t]>prec:
			times.append(t)
	times = np.asarray(times)
	return times

def time_to_angles(tsec,a0,a1,speed,ytot,time_video,rfposx = None):
	ttot = 14400
	t = ttot/speed
	tf = tsec/time_video*t
	f = pow(a1/a0,1/t)
	af0 = a0*pow(f,tf)
	af12 = af0/pow(f,ytot/2)
	af1 = af0/pow(f,ytot)
	if rfposx is not None:
		afrf = af0/pow(f,rfposx)
	else:
		afrf = None
	return [af0,af12,af1,afrf]
#print(time_to_angles(20,2,80,2,1000,40))
#print(time_to_angles(20,2,80,2,1000,40,511))

	
def time_to_angles2(tsec,a0,a1,speed,screen_angle,time_video):
	f = pow(a1/a0,tsec/time_video)
	dt = screen_angle/speed
	af0 = a0*f
	af12 = af0/pow(f,dt/time_video)
	af1 = af0/pow(f,2*dt/time_video)
	return [af0,af12,af1]
#print(np.asarray(time_to_angles2(12,5,100,30,25,40))*0.13)
#print(np.asarray(time_to_angles2(30,2,80,20,25,40))*0.13)

def angle_rf(angle,a0,a1,speed,ytot,time_video,rfposx):
	ttot = 14400
	t_dim = ttot/speed
	time_angle = time_video*np.log(angle/a0)/np.log(a1/a0)+ytot/2/t_dim*time_video
	return time_to_angles(time_angle,a0,a1,speed,ytot,time_video,rfposx)[-1]

#print(np.asarray(time_to_angles(20,80,2,3,1000,40,420))*0.13)
#print(angle_rf(9.7905,2,80,2,1000,40,489))

def create_dyna_grating_frame(x,y,a0,a1):
	m = np.zeros((y,x))
	print('size of image:',m.shape)
	f = (a1/a0)**(1/x)
	a = a0
	color = 0
	dx=0
	for i in range(0,x):
		a = a*f
		dx+=1
		if dx>a:
			dx = 0
			color = 1-color
		for j in range(0,y):
			m[j,i]=color
	return m
def create_dyna_grating_video(x,y,t,a0,a1,speed):
	out = cv2.VideoWriter(output_path+'dyna_grating.avi',cv2.VideoWriter_fourcc('P','I','M','1'), 30, (x,y),False)
	m = np.zeros((y,x))
	for i in range(0,x-2*a0,2*a0):
		m[:,i:i+a0]=255
	out.write(m.astype('uint8'))
	f = (a1/a0)**(1/t)
	a = a0
	color = 0
	dx=0
	for i in range(1,t):
		a = a*f
		dx+=1
		if dx>a:
			dx = 0
			color = 255-color
		m[:,0]=color			
		m[:,1:] = m[:,:-1]
		if i%speed==0:
			out.write(m.astype('uint8'))
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	out.release()
	cv2.destroyAllWindows() 
	
def get_frequency(trace):
	spectrum = fft.fft(trace)
	freq = fft.fftfreq(len(spectrum))
	plt.plot(freq,abs(spectrum))
	plt.ylabel('frequencies')
	plt.ylabel('amplitude')
	plt.show()
	return freq[np.argmax(np.abs(spectrum))]
	
def moving_fft(trace,w):
	freqs = []
	for i in range(len(trace)-w):
		freqs.append(get_frequency(trace[i:i+w]))
	return freqs