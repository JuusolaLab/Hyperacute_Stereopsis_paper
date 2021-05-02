
import os
import ast

def list_macros():
    '''
    Lists all available macros by names that can be
    directly passed to load function in this module.
    '''

    return [fn[:-4] for fn in os.listdir('macros') if fn.endswith('.txt')]

def load(macro_name):
    '''
    Loads a macro from text file.

    macro_name is the name of a macro file inside macros folder,
    without the file ending.

    Loaded macro that is returned is a list whose items
    are macro commands understood by DynamicImaging in core.py
    '''

    macro = []

    with open(os.path.join('macros', macro_name+'.txt'), 'r') as fp:
        for line in fp:
            if line:
                macro.append(ast.literal_eval(line))
    
    return macro

def save(macro_name, macro):
    with open(os.path.join('macros', macro_name+'.txt'), 'w') as fp:
        for line in macro:
            fp.write(str(line)+'\n')

