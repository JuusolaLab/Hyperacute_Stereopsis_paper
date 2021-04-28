import os
import numpy as np
import scipy.io as sio

EXAMPLE = '/home/joni/code/biosystfiles/empty_100ms.mat'

def stimulus_to_zero(mat, time_length):
    '''
    Replace STIMULUS and SWEEP_SEQ in Biosyst stimulusfile with zeros,
    creating a zero stimulus with length time_length.
    Sampling frequency is read from the original stimulus file.
    
    mat             Object returned by scipy.io.loadmat
    time_length     In seconds
    '''
    
    fs = float(mat['STIMRATE'])
    #mat = sio.loadmat(EXAMPLE, mat_dtype=True)
    
    # MAKE STIMULUS LONGER/SHORTER
    orglen = len(mat['STIMULUS'][0])
    orgchans = len(mat['STIMULUS'])
    
    mat['STIMULUS'] = np.zeros((orgchans, int(fs * time_length)))
    
    #del mat['TEST_PATTERN']

    # MAKE SWEEPSEQ LONGER/SHORTER
    for i in range(orgchans):
        
        #print(mat['SWEEP_SEQ'][0][i]) 
    
        mat['SWEEP_SEQ'][0][i] = np.zeros((1, int(fs * time_length)))
    
        #print(mat['SWEEP_SEQ'][0][i]) 
    
    return mat


def main():
    dirr = input("Original bsfile directory >> ")
    time = input("Desired length (in seconds) >> ")

    files = [os.path.join(dirr, fn) for fn in os.listdir(dirr)]

    for fn in files:
        longmat = sio.loadmat(fn, mat_dtype=True)
        longmat = stimulus_to_zero(longmat, time)
        sio.savemat(fn.replace('.mat', '_{}s_.mat'.format(time)), longmat, do_compression=True)
    

if __name__ == "__main__":
    main()

   
