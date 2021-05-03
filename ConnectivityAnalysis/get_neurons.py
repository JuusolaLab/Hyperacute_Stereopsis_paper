from neuprint import fetch_neurons, fetch_adjacencies, Client, NeuronCriteria as NC, fetch_synapses, SynapseCriteria as SC
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImphbWNtYW51czFAc2hlZmZpZWxkLmFjLnVrIiwibGV2ZWwiOiJub2F1dGgiLCJpbWFnZS11cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vLV9VbXJGaVZlRXZVL0FBQUFBQUFBQUFJL0FBQUFBQUFBQUFBL0FNWnV1Y21mSWU5V3ZScm9uQy1ZUUU0ZGRrOFhWZklUdGcvcGhvdG8uanBnP3N6PTUwP3N6PTUwIiwiZXhwIjoxNzcyNDgyNjIwfQ.18JDKwt_yLehRIESw-2PZHbt6Ml_7xiUH-6d6EgsY1E'
c = Client('neuprint.janelia.org', dataset='hemibrain:v1.1', token=TOKEN)

gamma_csv = r"C:\Users\James\OneDrive\Sheffield\Python\Neuprint\KCgd.csv"
lc14_csv = "/home/james/OneDrive/Sheffield/Python/Neuprint/LC14.csv"

def get_body_id_from_csv(csv_name):
    neuron_df = pd.read_csv(csv_name)
    return neuron_df["id"].to_list()

def body_ids_to_criterion(ids):
    return NC(bodyId=ids)
    
def neurons_from_csv(csv_name):
    crit = body_ids_to_criterion(get_body_id_from_csv(csv_name))
    neuron_df, roi_counts_df = fetch_neurons(crit)
    return neuron_df, roi_counts_df

def drop_empties(df):
	return df.mask(df == None, np.nan).dropna()

    
def plot_bodies(xs,ys,zs):
	fig = plt.figure()
	ax = Axes3D(fig)
	ax.scatter(xs, ys, zs, marker='o')
	plt.show()

def separate_xyz(locations):
	x = [sublist[0] for sublist in locations]
	y = [sublist[1] for sublist in locations]
	z = [sublist[2] for sublist in locations]
	return x, y, z

def get_skeletons(bodyIds):
	skeletons = []
	
	exceptions = []

	for i, bodyId in enumerate(bodyIds):
		print(i)
		try:
			s = c.fetch_skeleton(bodyId, format='pandas')
			s['bodyId'] = bodyId
			#s['color'] = bokeh.palettes.Accent[5][i]
			skeletons.append(s)
		except:
			exceptions.append(bodyId)


	# Combine into one big table for convenient processing
	skeletons = pd.concat(skeletons, ignore_index=True)
	skeletons.head()
	print(exceptions)
	return skeletons


def up_and_down_neurons(csv_name):

	ids = neurons_from_csv(csv_name)
	up_neurons, up_connections = fetch_adjacencies(None, ids)
	down_neurons, down_connections = fetch_adjacencies(ids, None)
	return up_neurons, up_connections, down_neurons, down_connections


def synapse_locations(csv_name, type):

	(neurons, rois) = neurons_from_csv(csv_name)
	synapse_criteria = SC(type=type)
	synapses = fetch_synapses(neurons.bodyId, synapse_criteria)
	return synapses