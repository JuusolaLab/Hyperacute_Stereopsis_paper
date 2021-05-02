'''
Places where to save and load temporary files.
'''

import os
import platform

CODE_ROOTDIR = os.path.dirname(os.path.realpath(__file__))
USER_HOMEDIR = os.path.expanduser('~')

if platform.system() == "Windows":
    PUPILDIR = os.path.join(USER_HOMEDIR, 'GonioImsoft')
else:
    PUPILDIR = os.path.join(USER_HOMEDIR, '.gonioimsoft')
