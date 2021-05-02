'''
Functions related to DrosoM data loading.

TODO
- clean the code
'''

import os
import ast

from gonioanalysis.rotary_encoders import to_degrees

REPETITION_INDICATOR  = 'rep'
POSITION_INDICATOR = 'pos'


def arange_fns(fns):
    '''
    Arange filenames based on REPETITION_INDICATOR and POSITION_INDICATOR
    in the time order (repeat 1, image1,2,3,4, repeat 2, image1,2,3,4, ...).
    
    If no indicators are found in the filenames then the ordering is
    at least alphabetical.
    '''
    
    # Sort by i_frame
    try:
        fns.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    except ValueError:
        # Here if image fn not enging with _somenumber.tif(f)
        pass
    
    # Sort by i_repeat
    fns.sort(key=lambda x: int(x.split('_')[-2][3:]))
    
    return fns


def angleFromFn(fn):
    '''
    Returns the horizontal and vertical angles from a given filename
    The filename must be IMSOFT formatted as
        im_pos(-30, 170)_rep0_0.tiff

    fn          Filename, from which to read the angles
    '''
    hor, ver = fn.split('(')[1].split(')')[0].split(',')
    hor = int(hor)
    ver = int(ver)
    
    angles = [[hor,ver]]
    to_degrees(angles)
    return angles[0]


def angles_from_fn(fn, prefix='pos'):
    '''
    Takes in a filename that somewhere contains string "pos(hor, ver)",
    for example "pos(-30, 170)" and returns tuple (-30, 170)
    '''
    try:
        i_start = fn.index(prefix) + len(prefix)
    except ValueError:
        raise ValueError("Cannot find prefix {} from filename {}".format(fn))

    try:
        i_end = fn[i_start:].index(')') + i_start + 1
    except ValueError:
        raise ValueError("Cannot find ')' after 'pos' in filename {}".format(fn))
    
    return ast.literal_eval(fn[i_start:i_end])



def load_data(drosom_folder):
    '''
    Loads DrosoM imaging data from the following save structure

    DrosoM2
        pos(0, 0)
            .tif files
        pos(20, 20)
            .tif files
        pos(0, 10)
            .tif files
        ...

    in a dictionary where the keys are str((horizontal, pitch)) and the items are
    a list of image stacks:
        
        stacks_dictionary = {"(hor1, pitch1): [[stack_rep1], [stack_rep2], ...]"},
        
        where stack_rep1 = [image1_fn, image2_fn, ...].
    
    Horizontal and pitch are given in rotatry encoder steps, not degrees.

    '''
    
    stacks_dictionary = {}

    pos_folders = [fn for fn in os.listdir(drosom_folder) if os.path.isdir(os.path.join(drosom_folder, fn))]

    # Import all tif images
    for folder in pos_folders:
        
        if not folder.startswith(POSITION_INDICATOR):
            continue
        
        str_angles = folder[len(POSITION_INDICATOR):]     # Should go from "pos(0, 0)" to "(0, 0)"
     
        files = os.listdir(os.path.join(drosom_folder, folder))
        tiff_files = [f for f in files if f.endswith('.tiff') or f.endswith('.tif')]
        
        if len(tiff_files) == 0:
            # Skip if no images in the folder
            continue

        tiff_files = arange_fns(tiff_files)

        stacks_dictionary[str_angles] = []

        # Subdivide into repetitions
        for tiff in tiff_files:
            try:
                i_repetition = int(tiff[tiff.index(REPETITION_INDICATOR)+len(REPETITION_INDICATOR):].split('_')[0])
            except ValueError:
                print('Warning: Cannot determine i_repetition for {}'.format(tiff))
            while i_repetition >= len(stacks_dictionary[str_angles]):
                stacks_dictionary[str_angles].append([])
            

                        
            stacks_dictionary[str_angles][i_repetition].append(os.path.join(drosom_folder, folder, tiff))
        
        # Remove empty lists, if one repetition index or more is missing from the data
        stacks_dictionary[str_angles] = [alist for alist in stacks_dictionary[str_angles] if not alist == []]

    return stacks_dictionary

