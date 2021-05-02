'''
Attribute ANALYSER_CMDS dict here contains functions that accept
the Analyser object as their only argument.
'''

import numpy as np

from gonioanalysis.drosom import plotting
from gonioanalysis.drosom.plotting.common import save_3d_animation
from gonioanalysis.drosom.plotting import basics
from gonioanalysis.drosom.plotting.plotter import MPlotter
from gonioanalysis.drosom.plotting import complete_flow_analysis, error_at_flight
from gonioanalysis.drosom.special.norpa_rescues import norpa_rescue_manyrepeats
from gonioanalysis.drosom.special.paired import cli_group_and_compare
import gonioanalysis.drosom.reports as reports

I_WORKER = None
N_WORKERS = None

plotter = MPlotter()


# Functions that take only one input argument that is the MAnalyser
ANALYSER_CMDS = {}
ANALYSER_CMDS['pass'] = print
ANALYSER_CMDS['vectormap'] = basics.plot_3d_vectormap
ANALYSER_CMDS['vectormap_mayavi'] = plotter.plot_3d_vectormap_mayavi
ANALYSER_CMDS['vectormap_video'] = lambda analyser: save_3d_animation(analyser, plot_function=basics.plot_3d_vectormap, guidance=True, i_worker=I_WORKER, N_workers=N_WORKERS) 
ANALYSER_CMDS['vectormap_oldvideo'] = lambda analyser: plotter.plot_3d_vectormap(analyser, animation=True)
ANALYSER_CMDS['magtrace'] = basics.plot_1d_magnitude
ANALYSER_CMDS['2d_vectormap'] =  plotter.plotDirection2D
ANALYSER_CMDS['trajectories'] = plotter.plot_2d_trajectories
ANALYSER_CMDS['2dmagnitude'] = plotter.plotMagnitude2D

# Analyser + image_folder
#ANALYSER_CMDS['1dmagnitude'] = plotter.plot_1d_magnitude_from_folder

ANALYSER_CMDS['illustrate_experiments_video'] = plotting.illustrate_experiments
ANALYSER_CMDS['norpa_rescue_manyrepeats'] = norpa_rescue_manyrepeats
ANALYSER_CMDS['compare_paired'] = cli_group_and_compare
ANALYSER_CMDS['lr_displacements'] = lambda analyser: reports.left_right_displacements(analyser, 'test')
ANALYSER_CMDS['left_right_summary'] = reports.left_right_summary
ANALYSER_CMDS['pdf_summary'] = reports.pdf_summary

rotations = np.linspace(-180,180, 360)
ANALYSER_CMDS['flow_analysis_yaw'] = lambda analyser: complete_flow_analysis(analyser, rotations, 'yaw')
ANALYSER_CMDS['flow_analysis_roll'] = lambda analyser: complete_flow_analysis(analyser, rotations, 'roll')
ANALYSER_CMDS['flow_analysis_pitch'] = lambda analyser: complete_flow_analysis(analyser, rotations, 'pitch')

ANALYSER_CMDS['error_at_flight'] = error_at_flight

ANALYSER_CMDS['export_vectormap'] = lambda analyser: analyser.export_3d_vectors()


# Functions that take two input arguments;
# MAanalyser object and the name of the imagefolder, in this order
IMAGEFOLDER_CMDS = {}
IMAGEFOLDER_CMDS['magtrace'] = basics.plot_1d_magnitude


# Functions that take two manalyser as input arguments
DUALANALYSER_CMDS = {}
DUALANALYSER_CMDS['difference'] = basics.plot_3d_differencemap

DUALANALYSER_CMDS['compare'] = basics.compare_3d_vectormaps
DUALANALYSER_CMDS['compare_compact'] = basics.compare_3d_vectormaps_compact
DUALANALYSER_CMDS['compare_manyviews'] = basics.compare_3d_vectormaps_manyviews

# Manyviews videos
for animation_type in ['rotate_plot', 'rotate_arrows', 'pitch_rot', 'yaw_rot', 'roll_rot']:
    DUALANALYSER_CMDS['compare_manyviews_{}_video'.format(animation_type.replace('_',''))] = lambda an1, an2, at=animation_type: save_3d_animation([an1, an2], plot_function=basics.compare_3d_vectormaps_manyviews, animation_type=at)

