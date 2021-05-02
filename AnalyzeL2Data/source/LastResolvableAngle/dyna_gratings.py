#in this file, we create a figure of plots for dynamic grating stimuli
#The program automaticaly finds last resolvable angles
#It uses an algorithm with 6 extra-parameters:
#2 parameters for peak detection (m for relative distance from the stimulus interval, p for enabling search for neighbouring peak if the result was not a peak but just on a middle of a slope)
#2 parameters for noise (thresh for minimum distance between smallest peak and trough, based on standard deviation of part of trace, a for inter-peaks noise)
#2 parameter for false negative (err_lim, conseq_lim)
if __name__ == '__main__':
	import gui4 as gui
	vars = gui.Get_files(None).get_vars()
	from dyna_gratings import Analyse
	Analyse.process(vars,plot=True)
class Analyse: 
	def process(vars,plot=False):
	
		import variabling as vr
		import transforming as tr
		import common as c
		import dyna_grating_functions as dgf
		import staticplots as sp
		import neuron_trace as nt

		from plotly import subplots
		import numpy as np
		import plotly 
		import plotly.graph_objs as go
		from PIL import Image
		from pandas import DataFrame,concat
		import time as tm
		import matplotlib.pyplot as plt

		
		neuron = vars['neuron']
		mat = vars['mat']
		neuron = vars['neuron']
		rois = vars['rois']
		video = vars['video']
		trans = vars['trans']
		stab_trans = vars['stab_trans']
		find_roi = vars['find_roi']
		fly_path = vars['fly_path']
		rec_path = vars['rec_path']
		#create the figure
		fig = subplots.make_subplots(rows=5, cols=2)


		ball_vars = vr.ball_vars(mat)
		stim_filename = ball_vars['stim_filename']
		stim_angle = ball_vars['stim_angle']
		time_stimulus = ball_vars['time_stimulus']
		
		######	CONSTANTS	######
		
		#MODEL PARAMETERS:
		err_lim = 3 #usually 2
		conseq_lim = 7 #usually 7 
		noise_margin = 1.5 #usually 1.5
		interpeak_height = .6 #usually .6
		count_lim = 3 #number of interpeaks (above interpeaks_height) you don't allow, usually 1
		m = .25 #see top of page for explanations
		p=.2 #see top of page for explanations
		
		#OTHER CONSTANTS
		on_response = False
		time_offset = 6.5 #usually 0
		
		#ROI CROPPING
		cpx1 = 0.1
		cpx2 = .55
		cpy1 = 0
		cpy2 = 1
		
		
		
		
		cp = cpx1,cpx2,cpy1,cpy2
		neuron_vectors, points_rois, frame_rois = nt.from_video(neuron,rois,time_stimulus,cp,nb_ROIs = 3, bkgpos = [0,0], plot = plot, ignore_rec_until = 0,time_offset =time_offset)

		n = len(neuron_vectors['means'][0])
		if neuron is None:
			n = 4000
		print('number of frames (when aligned with the stimulus time): ',n)
		video_vars = vr.video_vars(video)


		if on_response:
			print('Analysing for ON responses')
		else:
			print('Analysing for OFF responses')
			
		#pixelsize = c.read_tiff_pixelsize(neuron)
		pixelsize = 0.25

		#constants 
		t_lim = 0.1 #found with blink stimuli
		adaptation_time = 2.5 #time before noise is taken into account
		rfpos_mat = find_roi
		#if rfpos_mat is not None:
		#	rfpos = [tr.stim_param(rfpos_mat)['xpos'],tr.stim_param(rfpos_mat)['ypos']]
		#else:
		print("Warning: no receptive field position detected")
		rfpos = [500,500]
		params = tr.stim_param(mat)
		dir_bars = params['angle']
		centerpos = [params['xpos'],params['ypos']]
		rfposx = c.rfmatrix(rfpos,centerpos,dir_bars,1000)

		neuron_name = mat.split('data')[1].split('_')[0]
		fly_dim = {'length': 3, 'width': 1.5}
		video_qual = 1
		neuron_video_qual = 1
		speed = params['frame_repetition']

		#all the vectors ready to be plotted
		min3 = 0
		max3 = 0
		neuron_activities = []
		for mean in neuron_vectors['means']:
			neuron_activities.append(tr.time_aligned(mean,n, array = True))
			min3 = min(min3,min(neuron_activities[-1]))
			max3 = max(max3,max(neuron_activities[-1]))
		neuron_activity = neuron_activities[0]
		'''
		fft_window = int(100*n/1000)
		freqs = dgf.moving_fft(neuron_activity,fft_window)
		plt.plot(np.arange(0,len(freqs)),freqs)
		plt.ylabel('frame')
		plt.ylabel('frequency')
		plt.show()
		'''
		if neuron is None:
			min3 = 0
			max3 = 1
		#smooth neuron activities
		N=int(50*n/1000)
		N_noise = 1
		smooth_activities = []
		nonoise_activities = []
		for i in range(0,len(neuron_activities)):	
			smooth_activities.append(np.convolve(neuron_activities[i], np.ones((N,))/N, mode='same'))
			nonoise_activities.append(np.convolve(neuron_activities[i], np.ones((N_noise,))/N_noise, mode='same'))

		forward = tr.time_aligned(ball_vars['cumsum'][:,1],n, array = True)
		roll = tr.time_aligned(ball_vars['cumsum'][:,2],n, array = True)
		yaw = tr.time_aligned(ball_vars['cumsum'][:,3],n, array = True)
		yaw = [i*180/3.14 for i in yaw] #back in degrees
		x = tr.time_aligned(ball_vars['x'],n, array = True)
		y = tr.time_aligned(ball_vars['y'],n, array = True)
		dir = tr.time_aligned(ball_vars['dir'],n, array = True)



		stim_video = tr.time_aligned(ball_vars['stim_video'],n, array = True)
		print('Stimulus dimensions: ',stim_video.shape)
		ball_vars = None #free memory
		
        
		ytot = stim_video.shape[2]
		time = np.linspace(0,time_stimulus,n)
		
		#speed
		fspeed = np.gradient(forward)
		rspeed = np.gradient(roll)
		yspeed = np.gradient(yaw)


		#min and max of behaviour and fluorescence
		min1 = min(min(forward),min(roll),min(yaw))
		max1 = max(max(forward),max(roll),max(yaw))
		min2 = min(min(fspeed),min(rspeed),min(yspeed))
		max2 = max(max(fspeed),max(rspeed),max(yspeed))


		#light to dark times and peaks times
		ltd_indexes = c.ltd_times(stim_video,rfposx,opposite = on_response)
		stim_video = None #free memory
        
		ltd_times = time[ltd_indexes]
		peaks_indexes = []
		peaks_times = []
		for i in range(0,len(neuron_activities)):	
			peaks_indexes.append(c.ltd_peaks(nonoise_activities[i],ltd_indexes,m=m,p=p))
			peaks_times.append(time[peaks_indexes[-1]])


		#noise of first seconds
		if len(stim_filename.split('noise'))==1:
			nt = 0
			print('no noise in filename')
		else:
			nt = int(stim_filename.split('noise')[1].split('.')[0])
			print(nt,' sec of noise first')

		#time to angles graph
		if 'algrating' in stim_filename and 'to' in stim_filename:
			text = stim_filename.split('algrating')[0].split('to')
			a0 = int(text[0])
			a1 = int(text[1])
		else:
			print("Error: NO 'ALGRATING' IN FILE NAME")
		angle_lim = t_lim*c.repet_to_speed_bars(speed) #minimum angle found with blink stimuli
		allangles = [dgf.time_to_angles(i-nt,a0,a1,speed,ytot,int(time_stimulus-nt)) for i in ltd_times]
		angles0 = [c.pixel_to_angle_bars2(allangles[i][0]) for i in np.arange(0,len(allangles))]
		angles12 = [c.pixel_to_angle_bars2(allangles[i][1]) for i in np.arange(0,len(allangles))]
		angles1 = [c.pixel_to_angle_bars2(allangles[i][2]) for i in np.arange(0,len(allangles))]
		last_idx = c.last_analysable_time(angle_lim,angles12)

		angles12_peaks = []
		for i in range(0,len(neuron_activities)):
			allangles = [dgf.time_to_angles(k-nt,a0,a1,speed,ytot,int(time_stimulus-nt)) for k in peaks_times[i]]
			angles12_peaks.append([c.pixel_to_angle_bars2(allangles[k][1]) for k in np.arange(0,len(allangles))])
		

			
		#resolvabilities
		allres = []
		last_resolvable_angles = np.zeros(len(neuron_activities))
		last_resolvable_angles2 = np.zeros(len(neuron_activities))
		last_resolvable_times1 = np.zeros(len(neuron_activities))
		last_resolvable_times2 = np.zeros(len(neuron_activities))
		nstds = np.zeros(len(neuron_activities))
		for i in range(0,len(neuron_activities)):	
			if nt==0:
				nstd = np.std((neuron_activities[i]-smooth_activities[i])[-100:-1])
			else:
				nstd = np.std((neuron_activities[i]-smooth_activities[i])[int(adaptation_time/time_stimulus*n):int((nt-0.5)/time_stimulus*n)])
			nstds[i]=nstd
			print('Neuron ',i+1,"'s std: ",nstd)
			allres.append(dgf.allres(nonoise_activities[i],peaks_indexes[i],max(neuron_activities[i]),thresh = noise_margin*nstd,count_lim = count_lim,a=interpeak_height))
			invert = a0<a1
			index = dgf.last_res_index(allres[-1]['values'],err_lim,conseq_lim,invert=invert)
			last_resolvable_angles[i] = angles12_peaks[i][index[0]]	
			last_resolvable_angles2[i] = angles12_peaks[i][index[1]]	
			last_resolvable_times1[i] = peaks_times[i][index[0]]
			last_resolvable_times2[i] = peaks_times[i][index[1]]
		print('angles: ',last_resolvable_angles)
		print('angles2: ',last_resolvable_angles2)



		title = neuron_name+' ('+str(stim_angle)+'°, '+str(int(c.repet_to_speed_bars(speed)))+'°/s, '+stim_filename.split('.')[0]+')'

		#add all the traces to the figure

		#add Gcamp limit to figure
		fig.append_trace(sp.plotbar(ltd_times[last_idx],min = min3, max = max3,width = 2,color = 'red',showlegend=True,name="Gcamp limit",legendgroup="group2"),5,1)
		fig.append_trace(sp.plotbar(ltd_times[last_idx],min = 0, max = max(angles1),color = 'red',legendgroup="group2"),1,1)

		#add ltd traces to figure
		fig.append_trace(sp.plotbar(ltd_times[0],min = min3, max = max3,color = 'grey',showlegend=True,legendgroup="group1"),5,1)
		for t in ltd_times[1:]:
			fig.append_trace(sp.plotbar(t,min = min3, max = max3,color = 'grey',legendgroup="group1"),5,1)
		if trans is not None:
			if 'C0_' in trans:
				title+=' '+trans.split('C0_')[1]
			else:
				title+=' '+trans.split('/')[-1]
			trans = vr.parse_trans(trans)
			trans = {'x':tr.vec_stimuli_end(trans['x'],n),'y':tr.vec_stimuli_end(trans['y'],n)}
			xtrans = tr.time_aligned(trans['x'],n,array = True)
			ytrans = tr.time_aligned(trans['y'],n,array = True)


			
			if stab_trans is not None:
				title+=' substracted by stab of stab'
				stab_trans = vr.parse_trans(stab_trans)
				stab_trans = {'x':tr.vec_stimuli_end(stab_trans['x'],n),'y':tr.vec_stimuli_end(stab_trans['y'],n)}
				xtrans -=tr.time_aligned(stab_trans['x'],n,array = True)
				ytrans -=tr.time_aligned(stab_trans['y'],n,array = True)
							

			from sklearn.decomposition import PCA
			xtrans_avg = xtrans-np.mean(xtrans)
			ytrans_avg = ytrans-np.mean(ytrans)
			pca = PCA(n_components=1)
			xytrans_train = np.vstack((xtrans_avg,ytrans_avg)).T
			pca.fit(xytrans_train)
			xytrans_pca = pca.transform(xytrans_train).reshape((len(xytrans_train),))
			rangetransxy = max(np.max(np.abs(xtrans_avg)),np.max(np.abs(ytrans_avg)))
			
			#plot neuron's position on a scatter graph, with PCA direction
			fig.append_trace(sp.plotpoints(pixelsize*xtrans_avg,pixelsize*ytrans_avg,'x5','y5','motion',showlegend = True,color = 'gray'),3,1)
			fig.append_trace(sp.plotline([0,pca.components_[0][0]],[0,pca.components_[0][1]],'x5','y5','PCA', color = 'blue'),3,1)
			fig.update_xaxes(range=[-pixelsize*rangetransxy, pixelsize*rangetransxy], row=3, col=1)
			fig.update_yaxes(range=[-pixelsize*rangetransxy, pixelsize*rangetransxy], row=3, col=1)
			
			maxtrans_pca = np.max(xytrans_pca)
			mintrans_pca = np.min(xytrans_pca)
			transline = (xytrans_pca-mintrans_pca)/(maxtrans_pca-mintrans_pca)*(max3-min3)+min3
			#plot reduced dimension coordinates of neuron's position
			fig.append_trace(sp.plotline(time,transline,'x5','y5','motion ('+str(int(100*pixelsize*(maxtrans_pca-mintrans_pca))/100)+'μm range)', color = 'gray'),5,1)
			fig.append_trace(sp.plotline(tr.time_aligned(time,900),tr.time_aligned(transline,900),'x5','y5','motion low sample rate', color = 'gray'),5,1)

		for i in range(0,len(neuron_activities)):	
			print('analysing neuron ', i+1,'...')
			#neurons traces
			fig.append_trace(sp.plotline(time,neuron_activities[i],'x5','y5',str(i+1)+'('+c.color_names(i)+')', color = c.colorsNames[7],legendgroup="peaks"+str(i+1)),5,1)
			fig.append_trace(sp.plotline(time,nonoise_activities[i],'x5','y5','neuron activity without noise'+str(i+1), color = 'green',width=1,legendgroup="peaks"+str(i+1)),5,1)
			#neurons noise margin
			fig.append_trace(sp.plotline(time,smooth_activities[i]-noise_margin*nstds[i]/2,'x5','y5','noise margin '+str(i+1), color = 'red',width=1,legendgroup="peaks"+str(i+1)),5,1)
			fig.append_trace(sp.plotline(time,smooth_activities[i]+noise_margin*nstds[i]/2,'x5','y5','noise margin '+str(i+1), color = 'red',width=1,legendgroup="peaks"+str(i+1)),5,1)
			#add peaks times to figure
			for j in range(0,len(allres[i]['motifs'])):
				peak_value = nonoise_activities[i][peaks_indexes[i][j]]
				if peaks_times[i][j] == last_resolvable_times1[i]:
					fig.append_trace(sp.plotbar(peaks_times[i][j],min = 0, max = max3/2,width = 2, color = 'green',text=['','last angle1: '+str(last_resolvable_angles[i])+' ('+allres[i]['motifs'][j]+')'],mode='lines+text',legendgroup="peaks"+str(i+1)),5,1)
				elif peaks_times[i][j] == last_resolvable_times2[i]:
					fig.append_trace(sp.plotbar(peaks_times[i][j],min = 0, max = max3/2,width = 2, color = 'orange',text=['','last angle2: '+str(last_resolvable_angles2[i])],mode='lines+text',legendgroup="peaks"+str(i+1)),5,1)
				elif allres[i]['motifs'][j]!='':
					if 'interpeak' in allres[i]['motifs'][j]:
						fig.append_trace(sp.plotbar(peaks_times[i][j],min = min(0,peak_value), max = max(0,peak_value),width = 1, color = 'orange',hovertext = allres[i]['motifs'][j],mode='lines',legendgroup="peaks"+str(i+1)),5,1)
					else:
						fig.append_trace(sp.plotbar(peaks_times[i][j],min = min(0,peak_value), max = max(0,peak_value),width = 1, color = 'red',hovertext = allres[i]['motifs'][j],mode='lines',legendgroup="peaks"+str(i+1)),5,1)
				else:
					fig.append_trace(sp.plotbar(peaks_times[i][j],min = min(0,peak_value), max = max(0,peak_value),width = 1, color = 'blue',mode='lines',legendgroup="peaks"+str(i+1)),5,1)
					
			#resolvability traces
			fig.append_trace(sp.plotline(angles12_peaks[i][0:-1],100*allres[i]['values'],'x4','y4',showlegend=True,name ='resolv '+str(i+1),legendgroup="peaks"+str(i+1)),1,2)
		print('neurons analysed successfully')
		fig.append_trace(sp.plotline(ltd_times,angles0,'x6','y6','angles at the edge of screen',width = 1, color = 'gray'),1,1)
		fig.append_trace(sp.plotline(ltd_times,angles12,'x6','y6','angle at the middle of screen'),1,1)
		fig.append_trace(sp.plotline(ltd_times,angles1,'x6','y6','time to angles',width = 1, color = 'gray', showlegend = False),1,1)	

		max_dim = max(max(abs(x)),max(abs(y)))+fly_dim['length']*2

		#add neurons images
		if neuron is not None:
			images= [dict(
					source=Image.fromarray(frame_rois[:,int(frame_rois.shape[1]/2):]),
					xref="paper", yref="paper",
					x=0.35, y=0.45,
					sizex=.5, sizey=1,
					xanchor="left", yanchor="bottom"
				)]
		else:
			images = None
		#layout for the figure
		size = 15
		fig.layout.update(
				go.Layout(
					images = images,
					title=title,
					xaxis1=dict(title='',titlefont=dict(size=size),tickfont=dict(size=size),showticklabels=False,domain = [0,.4]),
					yaxis1=dict(title='angles',titlefont=dict(size=size),tickfont=dict(size=size),domain = [.8,1]),
					xaxis2=dict(title='last angles = '+str(last_resolvable_angles),titlefont=dict(size=size),tickfont=dict(size=int(size/1.5)),domain = [.6, 1],autorange='reversed',dtick=.5),
					yaxis2=dict(title='resolvability',titlefont=dict(size=size),tickfont=dict(size=int(size/1.5)),domain = [.8, 1],dtick=10),
					xaxis3=dict(title='',titlefont=dict(size=size),tickfont=dict(size=size),showticklabels=False,domain = [0,1]),
					yaxis3=dict(title='',titlefont=dict(size=size),tickfont=dict(size=size),domain = [.7,.9]),
					xaxis5=dict(title='back to front (μm)',titlefont=dict(size=size),tickfont=dict(size=size),domain = [0,.25]),
					yaxis5=dict(title='right to left (μm)',titlefont=dict(size=size),tickfont=dict(size=size),domain = [.48,.78]),
					xaxis7=dict(title='',titlefont=dict(size=size),tickfont=dict(size=size),showticklabels=False,domain = [0,1]),
					yaxis7=dict(title='motion speed(px/s)',titlefont=dict(size=size),tickfont=dict(size=size),domain = [.4,.5]),
					xaxis9=dict(title='params: a='+str(interpeak_height)+',thresh='+str(noise_margin)+',m='+str(m)+',p='+str(p)+',err_lim='+str(err_lim)+',conseq_lim='+str(conseq_lim),titlefont=dict(size=size),tickfont=dict(size=size),domain = [0,1]),
					yaxis9=dict(title='ΔF/F',titlefont=dict(size=size),tickfont=dict(size=size),domain = [0,.4]),
					titlefont = dict(size=size),
					showlegend=True,
					autosize = False,
					width = int(800*6/4),
					height = 800,
					legend = dict(x=1, y=1)
				)
			)
		print('figure layout created')
		#save xlsx file containing the last resolbvable angles
		c.add_xlsx3(fly_path,fly_path.split('/')[-1],'angles',[neuron_name,c.trunc(c.repet_to_speed_bars(speed),1),stim_angle]+last_resolvable_angles.tolist(),save=False)
		#save xlsx file containing the calcium data
		timestr = tm.strftime("%Y%m%d%H%M%S")
		
		df_calcium = DataFrame([neuron_name,'time','']+['','','','']+time.tolist())
		if neuron is not None:
			#c.add_xlsx3(rec_path,neuron_name+'_'+timestr,'calcium',[neuron_name,'time','']+['','','','']+time.tolist(),save=False,disp = 'col')
			for i in range(0,len(neuron_activities)):
				#c.add_xlsx3(rec_path,neuron_name+'_'+timestr,'calcium',[neuron_name,c.trunc(c.repet_to_speed_bars(speed),1),stim_angle]+c.real_roi_pos(points_rois[i],cpx1,frame_rois.shape[1])+neuron_activities[i].tolist(),save=False,disp = 'col')
				#c.add_xlsx3(rec_path,neuron_name+'_'+timestr,'resolvability',[neuron_name,c.trunc(c.repet_to_speed_bars(speed),1),stim_angle]+c.real_roi_pos(points_rois[i],cpx1,frame_rois.shape[1])+angles12_peaks[i][0:-1],save=False,disp = 'col')
				#c.add_xlsx3(rec_path,neuron_name+'_'+timestr,'resolvability',[neuron_name,c.trunc(c.repet_to_speed_bars(speed),1),stim_angle]+c.real_roi_pos(points_rois[i],cpx1,frame_rois.shape[1])+(100*allres[i]['values']).tolist(),save=False,disp = 'col')
				df_calcium2 = DataFrame([neuron_name,c.trunc(c.repet_to_speed_bars(speed),1),stim_angle]+c.real_roi_pos(points_rois[i],cpx1,frame_rois.shape[1])+neuron_activities[i].tolist())
				df_calcium = concat([df_calcium,df_calcium2],axis=1)
			df_calcium.to_csv(rec_path+'/'+neuron_name+'_'+timestr+'.txt', header=None, index=None, sep=' ', mode='a')
		
		#plot static
		plotly.offline.plot(fig,filename = rec_path+'/'+neuron_name+'_'+timestr+'.html',auto_open=True)
