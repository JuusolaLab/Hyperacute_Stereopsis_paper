
import numpy as np
import scipy.io as sio

EXAMPLE = '/home/joni/code/biosystfiles/empty_100ms.mat'

def empty(t_length):
    '''
    fs = 1000 Hz
    '''
    
    fs = 1000


    mat = sio.loadmat(EXAMPLE, mat_dtype=True)
    
    # MAKE STIMULUS LONGER/SHORTER
    orglen = len(mat['STIMULUS'][0])
    orgchans = len(mat['STIMULUS'])
    
    mat['STIMULUS'] = np.zeros((orgchans, orglen * 10 * t_length))
    

    # MAKE SWEEPSEQ LONGER/SHORTER
    for i in range(orgchans):
        
        #print(mat['SWEEP_SEQ'][0][i]) 
    
        mat['SWEEP_SEQ'][0][i] = np.zeros((1, orglen * 10 * t_length))
    
        #print(mat['SWEEP_SEQ'][0][i]) 
    
    return mat

    

if __name__ == "__main__":
    longmat = empty(1)
    
    sio.savemat('longmattet.mat', longmat)

