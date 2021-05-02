import variabling as vr
import transforming as tr
import common as c
import pandas as pd
def from_video(path_neuron,path_rois,time_stimulus,cp,nb_ROIs, bkgpos = [0,0], plot = True, ignore_rec_until = 0, start_delay = 0, end_delay = 0,time_offset = 0):
	time_neuron = vr.get_time_video(path_rois,path_neuron)
	time_neuron = time_neuron - time_offset
	if time_offset>0:
		print('WARNING! Manually adjusted time (with offset ',time_offset,'s) from ',time_neuron+time_offset,' to ',time_neuron,'s!') 
	cpx1,cpx2,cpy1,cpy2  = cp
	neuron_frames = vr.get_frames(path_neuron,crop=[0,1,cpy1,cpy2,cpx1,cpx2])
	neuron_frames = neuron_frames[ignore_rec_until:]
	rois_search = vr.auto_means(c.mat_to_frame(c.std(neuron_frames),bits = 16),25,25,16,nb_ROIs,cpx1 = cpx1,cpx2 = cpx2,bkgpos=bkgpos,plot=plot,scaling_bar=True) #bkgpos:[down,right]; rois:16,16,12 usually
	points_rois = rois_search['points']
	frame_rois = rois_search['frame']
	neuron_vars = vr.neuron_vars(neuron_frames,points_rois)
	traces = tr.neurons_stimuli_end(neuron_vars,time_stimulus,time_neuron,f0 = 'median',start_delay = start_delay,end_delay = end_delay)
	return traces, points_rois, frame_rois
def from_txt_values(path_neuron,time_stimulus,ignore_rec_until = 0, start_delay = 0, end_delay = 0):
	df = pd.read_csv(path_neuron)
	neuron_values = df.to_numpy().flatten()[6:]
	fps = len(neuron_values)/time_stimulus
	neuron_values = neuron_values[ignore_rec_until:]
	neuron_values = neuron_values[int(start_delay*fps):(int(end_delay*fps))]
	return {'means':[neuron_values]},None,None
