'''
Contains wrapper functions for scipy.io to extract
data traces from Biosyst data/stimulus files.
'''

import os

import scipy.io as sio
import numpy as np


def extract(fn, channel):
    '''
    Extracts data from biosyst datafiles of a specified channel.
    Returns data and fs
    
    ARGUMENTS       DESCRIPTION
    fn              Filename of the .mat file
    channel         The desired channel of extraction. Starts from 0
    '''

    # If fn is actually a list of filenames make a recursion
    if type(fn) == type([]) or type(fn) == type((0,0)):
        traces = []
        

        for single_fn in fn:
            print(single_fn)
            trace, fs = __extract_single(single_fn, channel)
            traces.append(trace)
        return traces, fs

    return __extract_single(fn, channel)



def __extract_single(fn, channel):
    '''
    Called from extract
    '''
    # Open a Biosyst generated file using scipy.io
    mat = sio.loadmat(os.path.join(os.getcwd(), fn))


    # If DATAFILE field not found (ie. is not recorded response but 
    # a stimulus file) open STIMULUS
    for key in ['DATAFILE', 'STIMULUS']:
        try:
            alldata = mat[key]
            break
        except KeyError:
            continue
    
    if key == 'STIMULUS':
        alldata = alldata.T

    # Pick needed parameters from the file
    if key == 'DATAFILE':
        fs = int(mat['RECORD_INFO'][0][2])
        N_channels = int(np.sum(mat['SETTINGS_INFO'][0][5]))
    elif key == 'STIMULUS':
        fs = int(mat['SAMPRATE'])
        N_channels = int(np.sum(mat['DA_STIM']))


    NoT = alldata.shape[1]
    N = alldata.shape[0]
    

    # --------------------------------------
    limits = range(channel, NoT, N_channels)
        
    # Number of Extracted traces
    NoE = 0
    for i in limits:
        NoE += 1
    extract = np.zeros((N, NoE))

    for j, i in enumerate(limits):
        extract[:, j] = alldata[:,i]
    
    return extract, fs



def extract_many(fn, channels):
    '''
    Wrapper for extract, extracting many channels at once

    channels        For example, [0,1,4,3]
    '''
    
    ex, fs = extract(fn, channels[0])
    for channel in channels[1:]:
        curex, fs = extract(fn, channel)
        
        ex = np.hstack((ex, curex))   

    return ex, fs


