if __name__ == '__main__':
	import gui4
	gui4.Get_files(None).get_vars()
class Get_files(object):
	def __init__(self,files):
		if files is None:
			from tkinter import filedialog
			from tkinter import Tk
			import common
			input_path = common.input_path
			root = Tk()
			root.withdraw()
			self.files = root.tk.splitlist(filedialog.askopenfilenames(parent=root,initialdir=input_path,title='Please select your files'))

		else:
			self.files = files
	def get_files(self):
		return self.files
	def get_vars(self):
		import sys
		#from PyQt5.QtWidgets import (QFileDialog, QAbstractItemView, QListView,QTreeView, QApplication, QDialog)
		import os
		from os import listdir
		from os.path import isfile, join

		video = None
		mat = None
		rois = None
		neuron = None
		stimuli = None
		find_roi = None
		trans = None
		stab_trans = None
		rf = None
		params = None
		files = self.files
		rec_path = '/'.join(files[0].split('/')[0:-1])
		dirname = rec_path
		fly_path = '/'.join(files[0].split('/')[0:-2])
		#get the find_roi file if exist
		for r, d, f in os.walk('/'.join(dirname.split('/')[0:-1])):
			for file in f:
				if 'find_roi100' in file:
					find_roi = '/'.join(dirname.split('/')[0:-1])+'/'+file.split('.')[0]+'/'+file
				if 'rf' in file:
					rf = '/'.join(dirname.split('/')[0:-1])+'/'+file
		for f in files:
			#get the file name.type only
			justfile = f.split('/')[-1]
			#just check the name of file
			name = justfile.split('.')[0]
			#check the type
			type = justfile.split('.')[-1]
			#do not process the file neuron
			if type == 'txt':
				if name.split('_')[-1] == 'trans':
					trans = f
				elif name.split('_')[-1] == 'trans1':
					stab_trans = f
				elif '_' not in name: 
					rois = f
				elif 'params' in name:
					params = f
				elif '_mean_' in name:
					neuron = f
			elif type == 'tif':
				neuron = f
			elif type== 'mat':
					mat = f
			elif type == 'avi':
				if name != 'neuron':
					if name[0:4]=='data':
						if name.split('_')[-1] == 'flycourse':
							stimuli = f
						else:
							video = f
					else:
						neuron = f
						
		#print name of recording
		if mat is None:
			print('no mat file')
		else:
			print(mat.split('/')[-1].split('.')[0])
		return {'video':video,'mat':mat,'rois':rois,'neuron':neuron,'stimuli':stimuli,'find_roi':find_roi,'trans':trans,'stab_trans':stab_trans,'rf':rf,'fly_path':fly_path,'rec_path':rec_path,'params':params}