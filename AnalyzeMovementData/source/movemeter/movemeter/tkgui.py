'''
A tkinter GUI for Movemeter.
'''

import os
import csv
import json
import datetime
import zipfile
import inspect

import numpy as np
import tifffile
import tkinter as tk
from tkinter import filedialog, simpledialog
import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib.cm
import matplotlib.colors
import matplotlib.transforms
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PIL import Image

from tk_steroids.elements import (
        Listbox,
        Tabs,
        TickboxFrame,
        ButtonsFrame,
        DropdownList,
        )
from tk_steroids.matplotlib import CanvasPlotter

from movemeter import __version__
from movemeter.directories import MOVEDIR
from movemeter.roi import (
        gen_grid,
        grid_along_ellipse,
        grid_along_line,
        grid_arc_from_points,
        grid_radial_line_from_points,
        _workout_circle,
        )
from movemeter import Movemeter
from movemeter.tk_heatmap import popup as open_httool


class ColormapSelector(tk.Frame):
    '''
    Widget to preview and select a matplotlib
    colormap.
    '''
    def __init__(self, tk_parent, callback, startmap=None):
        '''
        callback : callable
            When selected, the colormap passed to this callback function
        '''
        tk.Frame.__init__(self, tk_parent)
        
        self._callback = callback

        # Dict of all availbale colormap objects
        self.colormaps = {name: getattr(matplotlib.cm, name) for name in dir(matplotlib.cm) if isinstance(
            getattr(matplotlib.cm, name), matplotlib.colors.Colormap)}

       
        self.listbox = Listbox(self, list(self.colormaps.keys()), callback=self.on_selection)
        self.listbox.grid(row=1, column=1, sticky='NSWE')

        self.plotter = CanvasPlotter(self, text='Preview', figsize=(0.5,5))
        self.plotter.grid(row=1, column=2, sticky='NSWE')
        
        data = np.linspace(0,10)[:, np.newaxis]
        self.plotter.imshow(data)
        if startmap:
            self.on_selection(startmap)

        self.select_button = tk.Button(self, text='Ok', command=self.on_ok)
        self.select_button.grid(row=2, column=1, columnspan=2, sticky='NSWE')

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=10)
        self.grid_columnconfigure(1, weight=1)

    def on_selection(self, name):
        self._current = name
        self.plotter.imshow_obj.cmap = self.colormaps[name]
        self.plotter.update()
    
    def on_ok(self):
        self._callback(self.colormaps[self._current])



class MovemeterTkGui(tk.Frame):
    '''
    Class documentation TODO.
    
    
    exclude_images : list of integers and/or strings
        Images to skip by file name or by index
    '''

    def __init__(self, tk_parent):
        tk.Frame.__init__(self, tk_parent)
        self.parent = tk_parent

        self.current_folder = None
        self.folders = []
        self.image_fns = []
        self.images = None
        self.exclude_images = []

        self.selections = []
        self.mask_image = None
        self.roi_groups = []
        self.current_roi_group = 0
        self.roi_patches = []
        self.results = []
        
        self.heatmap_images = []
        
        self.movemeter = None
        self.fs = 100

        self.show_controls = False
        self.use_mask_image = False

        self.batch_name = 'batch_name'

        self.colors = matplotlib.cm.ScalarMappable(cmap=matplotlib.cm.tab10)
        self.colors.set_clim(0,10)
        

        # Top menu
        # --------------------------------
        self.menu = tk.Menu(self)
        
        filemenu = tk.Menu(self)
        filemenu.add_command(label='Add directory...', command=self.open_directory)
        filemenu.add_separator()
        filemenu.add_command(label='Load ROIs',
                command=lambda: self.apply_movzip(rois=True))
        filemenu.add_command(label='Save ROIs',
                command=lambda: self._save_movzip(only=['rois', 'selections']))
        
        filemenu.add_separator()
        filemenu.add_command(label='Save ROI view',
                command=self.save_roiview)
        
        filemenu.add_command(label='Save ROIs only view',
                command=lambda: self.save_roiview(only_rois=True))
        filemenu.add_separator()
        filemenu.add_command(label='Quit', command=self.parent.destroy) 
        
        self.menu.add_cascade(label='File', menu=filemenu)
        

        editmenu = tk.Menu(self)
        editmenu.add_command(label='Undo (latest ROI)', command=self.undo)
        editmenu.add_separator()
        editmenu.add_command(label='Global settings', command=self.open_settings)
        self.menu.add_cascade(label='Edit', menu=editmenu)

        viewmenu = tk.Menu(self)
        viewmenu.add_command(label='Show image controls', command=self.toggle_controls)
        self.menu.add_cascade(label='View', menu=viewmenu)
        
        batchmenu = tk.Menu(self)
        batchmenu.add_command(label='Batch measure & save all', command=self.batch_process)
        batchmenu.add_separator()
        batchmenu.add_command(label='Reprocess old', command=self.recalculate_old)
        batchmenu.add_command(label='Replot heatmap', command=self.replot_heatmap)
 
        self.menu.add_cascade(label='Batch', menu=batchmenu)

        toolmenu = tk.Menu(self)
        toolmenu.add_command(label='Heatmap tool', command=lambda: open_httool(self))
        self.menu.add_cascade(label='Tools', menu=toolmenu)
        


        self.parent.config(menu=self.menu)

        


        # Input folders

        self.folview = tk.LabelFrame(self, text='Input folders')
        self.folview.rowconfigure(2, weight=1)
        self.folview.columnconfigure(1, weight=1)
        self.folview.grid(row=0, column=1, sticky='NSWE')

        self.folders_listbox = Listbox(self.folview, ['No folders selected'], self.folder_selected)
        self.folders_listbox.listbox.config(height=10)
        self.folders_listbox.grid(row=2, column=1, columnspan=2, sticky='NSWE')

        self.imview_buttons = ButtonsFrame(self.folview,
                ['Add...', 'Remove', 'FS'],
                [self.open_directory, self.remove_directory, self.set_fs])
        self.imview_buttons.grid(row=0, column=1) 
        self.fs_button = self.imview_buttons.buttons[2]
        self.set_fs(fs=self.fs)

        # Operations view
        # -------------------------
        self.opview = tk.LabelFrame(self, text='Command center')
        self.opview.grid(row=0, column=2, sticky='NSWE')
        
        self.tabs = Tabs(self.opview,
                ['Style', 'ROI creation', 'Preprocessing', 'Motion analysis'],
                draw_frame = True)
        self.tabs.grid(row=0, column=1, columnspan=2, sticky='NSWE')
        self.tabs.set_page(1) 
       
        self.styleview = self.tabs.tabs[0]
        self.styleview.columnconfigure(2, weight=1)
        
        self.colormap_label = tk.Label(self.styleview, text='Colormap')
        self.colormap_label.grid(row=1, column=1)
        self.colormap_selection = tk.Button(self.styleview, text=self.colors.get_cmap().name,
                command=self.open_colormap_selection)
        self.colormap_selection.grid(row=1, column=2)
        
        tk.Label(self.styleview, text='Line width').grid(row=2, column=1)
        self.patch_lw_slider = tk.Scale(self.styleview, from_=0, to_=10,
                orient=tk.HORIZONTAL)
        self.patch_lw_slider.set(1)
        self.patch_lw_slider.grid(row=2, column=2, sticky='NSWE')
        
        tk.Label(self.styleview, text='Fill strength').grid(row=3, column=1)
        self.patch_fill_slider = tk.Scale(self.styleview, from_=0, to=100,
                orient=tk.HORIZONTAL)
        self.patch_fill_slider.grid(row=3, column=2, sticky='NSWE')
        self.patch_fill_slider.set(40)



        self.roiview = self.tabs.tabs[1]
        self.roiview.columnconfigure(2, weight=1)

        self.roi_drawtypes = {'box': 'box',
                'ellipse': 'ellipse',
                'line': 'line',
                'polygon': 'polygon',
                'arc_from_points': 'polygon',
                'concentric_arcs_from_points': 'polygon',
                'radial_lines_from_points': 'polygon'}

        tk.Label(self.roiview, text='Selection mode').grid(row=1, column=1)
        self.selmode_frame = tk.Frame(self.roiview)
        self.selmode_frame.grid(row=1, column=2)
        
        self.roitype_selection = DropdownList(self.selmode_frame,
                ['box', 'ellipse', 'line', 'polygon', 'arc_from_points',
                    'concentric_arcs_from_points',
                    'radial_lines_from_points'], 
                ['Box', 'Ellipse', 'Line', 'Polygon', 'Arc from points',
                    'Concentric Arcs (++RG)',
                    'Radial lines (++RG)'],
                single_select=True, callback=self.update_roitype_selection)
        self.roitype_selection.grid(row=1, column=2)

        self.drawmode_selection = TickboxFrame(self.selmode_frame,
                ['add', 'remove'], ['Add', 'Remove'],
                single_select=True
                )
        self.drawmode_selection.grid(row=1, column=1)


        tk.Label(self.roiview, text='Block size').grid(row=3, column=1)
        self.blocksize_slider = tk.Scale(self.roiview, from_=16, to=128,
                orient=tk.HORIZONTAL)
        self.blocksize_slider.set(32)
        self.blocksize_slider.grid(row=3, column=2, sticky='NSWE')

        tk.Label(self.roiview, text='Block distance').grid(row=4, column=1)
        self.overlap_slider = tk.Scale(self.roiview, from_=1, to=128,
                orient=tk.HORIZONTAL, resolution=1)
        self.overlap_slider.set(32)
        self.overlap_slider.grid(row=4, column=2, sticky='NSWE')
        
        self.distance_label = tk.Label(self.roiview, text='Line-block distance')
        self.distance_label.grid(row=5, column=1)
        self.distance_slider = tk.Scale(self.roiview, from_=1, to=128,
                orient=tk.HORIZONTAL, resolution=1)
        self.distance_slider.set(32)
        self.distance_slider.grid(row=5, column=2, sticky='NSWE')

        
        self.nroi_label = tk.Label(self.roiview, text='Count')
        self.nroi_label.grid(row=6, column=1)
        self.nroi_label.grid_remove()
        self.nroi_slider = tk.Scale(self.roiview, from_=1, to=128,
                orient=tk.HORIZONTAL, resolution=1,
                command=self.nroi_slider_callback)
        self.nroi_slider.grid(row=6, column=2, sticky='NSWE')
        self.nroi_slider.grid_remove()

        self.radial_len_label = tk.Label(self.roiview, text='Radial line length')
        self.radial_len_label.grid(row=7, column=1)
        self.radial_len_label.grid_remove()
        self.radial_len_slider = tk.Scale(self.roiview, from_=1, to=1024,
                orient=tk.HORIZONTAL, resolution=1)
        self.radial_len_slider.grid(row=7, column=2, sticky='NSWE')
        self.radial_len_slider.grid_remove()





        self.roi_buttons = ButtonsFrame(self.roiview, ['Update', 'Max grid', 'Clear', 'Undo', 'New group'],
                [self.update_grid, self.fill_grid, self.clear_selections, self.undo, self.new_group])

        self.roi_buttons.grid(row=8, column=1, columnspan=2)
        

        self.preview = self.tabs.tabs[2]
        self.preview.columnconfigure(2, weight=1)
        tk.Label(self.preview, text='Gaussian blur').grid(row=2, column=1)
        self.blur_slider = tk.Scale(self.preview, from_=0, to=32,
                orient=tk.HORIZONTAL)
        self.blur_slider.set(0)
        self.blur_slider.grid(row=2, column=2, sticky='NSWE')


        self.parview = self.tabs.tabs[3]
        self.parview.columnconfigure(2, weight=1)


        # Movemeter True/False options; Automatically inspect from Movemeter.__init__
        moveinsp = inspect.getfullargspec(Movemeter.__init__)

        moveargs = []
        movedefaults = []
        for i in range(1, len(moveinsp.args)):
            arg = moveinsp.args[i]
            default = moveinsp.defaults[i-1]
            if isinstance(default, bool) and arg not in ['multiprocess']:
                moveargs.append(arg)
                movedefaults.append(default)
        
        self.movemeter_tickboxes = TickboxFrame(self.parview, moveargs,
                defaults=movedefaults)
        self.movemeter_tickboxes.grid(row=0, column=1, columnspan=2)


        tk.Label(self.parview, text='Maximum movement').grid(row=1, column=1)
        self.maxmovement_slider = tk.Scale(self.parview, from_=1, to=100,
                orient=tk.HORIZONTAL)
        self.maxmovement_slider.set(10)
        self.maxmovement_slider.grid(row=1, column=2, sticky='NSWE')

        tk.Label(self.parview, text='Upscale').grid(row=2, column=1)
        self.upscale_slider = tk.Scale(self.parview, from_=0.1, to=10,
                orient=tk.HORIZONTAL, resolution=0.1)
        self.upscale_slider.set(5)
        self.upscale_slider.grid(row=2, column=2, sticky='NSWE')


        tk.Label(self.parview, text='CPU cores').grid(row=3, column=1)
        self.cores_slider = tk.Scale(self.parview, from_=1, to=os.cpu_count(),
                orient=tk.HORIZONTAL)
        self.cores_slider.set(max(1, int(os.cpu_count()/2)))
        self.cores_slider.grid(row=3, column=2, sticky='NSWE')


        

        self.calculate_button = tk.Button(self.opview, text='Measure movement',
                command=self.measure_movement)
        self.calculate_button.grid(row=1, column=1)

        self.stop_button = tk.Button(self.opview, text='Stop',
                command=self.stop)
        self.stop_button.grid(row=1, column=2)


        self.export_button = tk.Button(self.opview, text='Export results',
                command=self.export_results)
        self.export_button.grid(row=4, column=1)
        
        self.export_name = tk.Entry(self.opview, width=50)
        self.export_name.insert(0, "enter export name")
        self.export_name.grid(row=4, column=2)
        

        # Images view: Image looking and ROI selection
        # -------------------------------------------------
        self.imview = tk.LabelFrame(self, text='Images and ROI')
        self.imview.grid(row=1, column=1, sticky='NSWE')
        
        self.imview.columnconfigure(1, weight=1)
        self.imview.rowconfigure(3, weight=1)

        self.imview_buttons = ButtonsFrame(self.imview,
                ['Exclude image', 'Exclude index'],
                [self.toggle_exclude, lambda: self.toggle_exclude(by_index=True)])
        
        self.imview_buttons.grid(row=1, column=1)


        self.image_slider = tk.Scale(self.imview, from_=0, to=0,
                orient=tk.HORIZONTAL, command=self.change_image)
        
        self.image_slider.grid(row=2, column=1, sticky='NSWE')

        self.images_plotter = CanvasPlotter(self.imview)
        self.images_plotter.grid(row=3, column=1, sticky='NSWE') 
        
        ax = self.images_plotter.ax
        self.excludetext = ax.text(0.5, 0.5, '', transform=ax.transAxes,
                fontsize=24, ha='center', va='center', color='red')



        # Results view: Analysed traces
        # ------------------------------------
        
        self.tabs = Tabs(self, ['Displacement', 'Heatmap'])
        self.tabs.grid(row=1, column=2, sticky='NSWE')
        self.resview = self.tabs.pages[0]
        self.heatview = self.tabs.pages[1]

        #self.resview = tk.LabelFrame(self, text='Results')
        #self.resview.grid(row=1, column=2)
        
        self.resview.rowconfigure(2, weight=1)
        self.resview.columnconfigure(1, weight=1)
        self.heatview.columnconfigure(2, weight=1)
        self.heatview.rowconfigure(2, weight=1)

        self.results_plotter = CanvasPlotter(self.resview)
        self.results_plotter.grid(row=2, column=1, sticky='NSWE')
        
        self.heatmap_plotter = CanvasPlotter(self.heatview)
        self.heatmap_plotter.grid(row=2, column=2, sticky='NSWE') 
        
        self.heatmap_slider = tk.Scale(self.heatview, from_=0, to=0,
            orient=tk.HORIZONTAL, command=self.change_heatmap)
        self.heatmap_slider.grid(row=0, column=1, sticky='NSWE')
        
        self.heatmapcap_slider = tk.Scale(self.heatview, from_=0.1, to=100,
            orient=tk.HORIZONTAL, resolution=0.1, command=self.change_heatmap)
        self.heatmapcap_slider.set(20)
        self.heatmapcap_slider.grid(row=0, column=2, sticky='NSWE') 
        
        self.heatmap_firstcap_slider = tk.Scale(self.heatview, from_=0.1, to=100,
            orient=tk.HORIZONTAL, resolution=0.1, command=self.change_heatmap)
        self.heatmap_firstcap_slider.set(20)
        self.heatmap_firstcap_slider.grid(row=1, column=2, sticky='NSWE') 
       
        
        self.status = tk.Label(self, text='Nothing to do')
        self.status.grid(row=2, column=1, columnspan=2)

        self.columnconfigure(1, weight=1)    
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)


    def stop():
        self.exit=True
        if self.movemeter:
            self.movemeter.stop()

    def set_fs(self, fs=None):

        if fs is None:
            fs = simpledialog.askfloat('Imaging frequency (Hz)', 'How many images were taken per second')

        if fs:
            self.fs = fs
            self.fs_button.configure(text='fs = {} Hz'.format(self.fs))


    def open_settings(self):
        raise NotImplementedError


    def open_directory(self, directory=None):
        
        if directory is None:
            try: 
                with open(os.path.join(MOVEDIR, 'last_directory.txt'), 'r') as fp:
                    previous_directory = fp.read().rstrip('\n')
            except FileNotFoundError:
                previous_directory = os.getcwd()

            print(previous_directory)

            if os.path.exists(previous_directory):
                directory = filedialog.askdirectory(title='Select directory with the images', initialdir=previous_directory)
            else:
                directory = filedialog.askdirectory(title='Select directory with the images')
            
            
        if directory:
            if not os.path.isdir(MOVEDIR):
                os.makedirs(MOVEDIR)
            with open(os.path.join(MOVEDIR, 'last_directory.txt'), 'w') as fp:
                fp.write(directory)
            
            # Check if folder contains any images; If not, append
            # The folders in this folder
            
            if [fn for fn in os.listdir(directory) if fn.endswith('.tif') or fn.endswith('.tiff')] == []:
                directories = [os.path.join(directory, fn) for fn in os.listdir(directory)]
            else:
                directories = [directory]
            
            for directory in directories:
                self.folders.append(directory)
                self.folders_listbox.set_selections(self.folders)
                self.folder_selected(directory)

    
    def remove_directory(self):
        
        self.folders.remove(self.current_folder)
        self.folders_listbox.set_selections(self.folders)


    def folder_selected(self, folder):
        '''
        When the user selects a folder from the self.folders_listbox
        '''
        
        self.current_folder = folder

        print('Selected folder {}'.format(folder))

        self.image_fns = [os.path.join(folder, fn) for fn in os.listdir(folder) if fn.endswith('.tiff') or fn.endswith('.tif')]
        self.image_fns.sort()

        self.images = [None for fn in self.image_fns]
        self.mask_image = None

        self.change_image(slider_value=1)
        N_images = len(self.image_fns)
        self.image_slider.config(from_=1, to=N_images)
       
        self.export_name.delete(0, tk.END)
        self.export_name.insert(0, os.path.basename(folder.rstrip('/')))


    def toggle_exclude(self, by_index=False):
        '''
        by_index  If true, toggle exclude for all images with this index
        '''

        indx = int(self.image_slider.get()) - 1
        if by_index:
            fn = indx
        else:
            fn = self.image_fns[indx]

        if fn not in self.exclude_images:
            self.exclude_images.append(fn)
            self.set_status('Removed image {} from the analysis'.format(fn))
        else:
            self.exclude_images.remove(fn) 
            self.set_status('Added image {} back to the analysis'.format(fn))
        
        self.mask_image = None
        self.change_image(slider_value=self.image_slider.get())
        print(self.exclude_images)
    
    def toggle_controls(self):
        self.show_controls = not(self.show_controls)
        self.change_image()

    def recalculate_old(self, directory=None):
        '''
        Using the current settings, recalculate old data by opening the
        zip file and reading image filenames and ROI limits from there.
        '''

        if directory == None:
            directory = filedialog.askdirectory()
            if not directory:
                return None
        
        if not self._ask_batchname():
            return None
 
        self.exit = False
        for root, dirs, fns in os.walk(directory):
            
            if self.exit:
                break

            movzip = [fn for fn in os.listdir(root) if fn.startswith('movemeter') and fn.endswith('.zip')]
            
            if movzip:
                settings, filenames, selections, rois, movements = self._load_movzip(os.path.join(root, movzip[0]))
                
                self.folder_selected(os.path.dirname(filenames[0]))
                
                x1, y1 = np.min(rois, axis=0)[0:2]
                x2, y2 = np.max(rois, axis=0)[0:2] + rois[0][3]
                self.set_roi(x1,y1,x2,y2)

                self.measure_movement()

                self.export_results(batch_name=self.batch_name)

        self.set_status('Results recalculated :)')


    def replot_heatmap(self, directory=None):
        '''
        Like recalculate old, but relies in the old movement analysis results
        '''
        if directory == None:
            directory = filedialog.askdirectory()
            if not directory:
                return None
        
        if not self._ask_batchname():
            return None
 
        self.exit = False
        for root, dirs, fns in os.walk(directory):
            
            if self.exit:
                break

            movzip = [fn for fn in os.listdir(root) if fn.startswith('movemeter') and fn.endswith('.zip')]
            if movzip:
                settings, filenames, self.selections, self.roi_groups, self.results = self._load_movzip(os.path.join(root, movzip[0])) 
                
                self.folder_selected(os.path.dirname(filenames[0]))
                self.set_settings(settings)

                self.plot_results()
                self.calculate_heatmap()
                self.change_heatmap(1)

                self.export_results(batch_name=self.batch_name)

        self.set_status('Heatmaps replotted :)')

    
    def _ask_batchname(self):
        name = simpledialog.askstring('Batch name', 'Name new folder')
        if name:
            self.batch_name = name
            return True
        else:
            return False


    def batch_process(self, fill_maxgrid=False):
        '''
        fill_maxgrid : bool
            If True, ignore current ROIs and fill a full frame grid
            using the current slider options.
        '''

        if not self._ask_batchname():
            return None
        
        self.exit = False
        for folder in self.folders:
            if self.exit:
                break
            self.folder_selected(folder)
            
            if fill_maxgrid:
                self.fill_grid()
            
            self.measure_movement()
            self.export_results(batch_name=self.batch_name)


    def measure_movement(self):
        if self.image_fns and self.roi_groups:
            print('Started roi measurements')
           
            self.results = []

            cores = int(self.cores_slider.get())
            if cores == 1:
                cores = False
            
            self.movemeter = Movemeter(upscale=float(self.upscale_slider.get()),
                    multiprocess=cores, print_callback=self.set_status, preblur=self.blur_slider.get(),
                    **self.movemeter_tickboxes.states)
           
            for rois in self.roi_groups:
                # Set movemeted data
                images = [self._included_image_fns()]
                self.movemeter.set_data(images, [rois])
                
                self.results.append( self.movemeter.measure_movement(0, max_movement=int(self.maxmovement_slider.get()), optimized=True) )
            
            self.plot_results()

            self.calculate_heatmap()
            self.change_heatmap(1)

            print('Finished roi measurements')
        else:
            print('No rois')
    
    @property
    def image_shape(self):
        slider_value = int(self.image_slider.get())
        image_i = int(slider_value) -1
        if self.images[image_i] is None:
            self.images[image_i] = tifffile.imread(self.image_fns[image_i])
        return self.images[image_i].shape

    
    def open_colormap_selection(self):
        
        top = tk.Toplevel(self)
        top.title('Select colormap')
        sel = ColormapSelector(top, callback=self.apply_colormap,
                startmap=self.colors.get_cmap().name)
        sel.grid(row=0, column=0, sticky='NSWE')
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        top.mainloop()

    def apply_colormap(self, colormap):
        
        if hasattr(colormap, 'colors'):
            self.colors.set_clim(0, len(colormap.colors))
        else:
            self.colors.set_clim(0, 10)

        self.colors.set_cmap(colormap)
        self.colormap_selection.config(text=colormap.name)
        self.update_grid()


    def undo(self):
        '''
        Undo a ROI selection made by the user.
        '''
        if len(self.selections) == 0:
            self.set_status('Nothing to undo')
            return None

        # Index of the roigroup to be undone
        i_roigroup = self.selections[-1][-1]['i_roigroup']

        # Clear the previous selection data
        self.selections = self.selections[:-1]
        
        # Clear the corresponding ROI patches
        N_rois_remove = len(self.roi_patches[-1])
        for patch in self.roi_patches[-1]:
            patch.remove()
        self.roi_patches = self.roi_patches[:-1]
        
        # Clear the actual ROIs
        self.roi_groups[i_roigroup] = self.roi_groups[i_roigroup][:-N_rois_remove]
        
        self.images_plotter.update()
        self.set_status('Undone windows {} in ROI group {}'.format(N_rois_remove, i_roigroup))


    def nroi_slider_callback(self, N=None):
        pass

    def update_roitype_selection(self):
        
        selected = self.roitype_selection.ticked[0] 

        if selected in ['concentric_arcs_from_points', 'radial_lines_from_points']:
            self.nroi_label.grid()
            self.nroi_slider.grid()

            if selected == 'radial_lines_from_points':
                self.radial_len_label.grid()
                self.radial_len_slider.grid()

        else:
            self.nroi_label.grid_remove()
            self.nroi_slider.grid_remove()

            self.radial_len_label.grid_remove()
            self.radial_len_slider.grid_remove()

        self.change_image()

    def clear_selections(self):
        self.selections = []
        self.update_grid()

        self.roi_groups = []
        self.current_roi_group = 0

    def update_grid(self, *args):

        # Updating the image also needed now to update the selector
        # type drawn while selecting (box or line)
        self.change_image()
        
        # Clear any previous patches
        for group in self.roi_patches:
            for patch in group:
                patch.remove()
        self.roi_patches = []

        self.roi_groups = []
        
        if self.selections:
            for selection in self.selections:
                self.set_roi(*selection, user_made=False)
        else:
            self.images_plotter.update()



    def fill_grid(self): 
        self.set_roi(0,0,*reversed(self.image_shape))
   

    def new_group(self):
        self.current_roi_group += 1

    def set_roi(self, x1=None,y1=None,x2=None,y2=None, params=None, user_made=True,
            recursion_data=None):
        

        if params is None:
            params = {}
            params['roitype'] = [s for s, b in self.roitype_selection.states.items() if b][0]
            params['blocksize'] = 2*[self.blocksize_slider.get()]
            params['distance'] = self.distance_slider.get()
            params['relstep'] = float(self.overlap_slider.get())/params['blocksize'][0]
            params['count'] = self.nroi_slider.get()
            params['rlen'] = self.radial_len_slider.get()
            params['i_roigroup'] = int(self.current_roi_group)
            params['mode'] = self.drawmode_selection.ticked[0]

       
        roitype, block_size, distance, rel_step, i_roigroup, count, mode, rlen = [
                params[key] for key in ['roitype','blocksize','distance','relstep', 'i_roigroup', 'count', 'mode', 'rlen']]

        if user_made:
            self.selections.append( (x1, y1, x2, y2, params) )   
        
        if roitype in ['polygon', 'arc_from_points', 'concentric_arcs_from_points',
                'radial_lines_from_points']:
            vertices = x1

            if roitype == 'polygon':
                rois = []
                for i_vertex in range(len(vertices)-1):
                    pA, pB = vertices[i_vertex:i_vertex+2]
                    rois.extend( grid_along_line(pA, pB, distance, block_size, step=rel_step) )
            elif roitype == 'arc_from_points':
                rois = grid_arc_from_points((0,0,*reversed(self.image_shape)), block_size, step=rel_step, points=vertices)
            elif roitype in ['concentric_arcs_from_points', 'radial_lines_from_points']:
                if recursion_data is None:
                    recursion_data = _workout_circle(vertices)
                
                if int(self.current_roi_group) < count-1:
                    self.current_roi_group += 1
                    cp, R = recursion_data
                    
                    if roitype == 'concentric_arcs_from_points':
                        new_recursion_data = (cp, R-distance)
                    elif roitype == 'radial_lines_from_points':
                        new_recursion_data = (cp, R)

                    self.set_roi(x1=x1,y1=y1,x2=x2,y2=y2,
                            params={**params, **{'i_roigroup': self.current_roi_group}},
                            user_made=False,
                            recursion_data=new_recursion_data)
                    self.current_roi_group -= 1 
                
                if roitype == 'concentric_arcs_from_points':
                    rois = grid_arc_from_points((0,0,*reversed(self.image_shape)), block_size, step=rel_step,
                            circle=recursion_data, lw=distance)
                elif roitype == 'radial_lines_from_points':
                    rois = grid_radial_line_from_points((0,0,*reversed(self.image_shape)), block_size, step=rel_step,
                            circle=recursion_data, line_len=rlen,
                            i_segment=self.current_roi_group, n_segments=count)

            else:
                raise ValueError('unkown roitype {}'.format(roitype))

        else:
            w = x2-x1
            h = y2-y1
       
            if roitype == 'line':
                rois = grid_along_line((x1, y1), (x2, y2), distance, block_size, step=rel_step)
            elif roitype == 'ellipse':
                rois = grid_along_ellipse((x1,y1,w,h), block_size, step=rel_step)
            else:
                rois = gen_grid((x1,y1,w,h), block_size, step=rel_step)
            
        while len(self.roi_groups) <= i_roigroup:
            self.roi_groups.append([])

        if mode == 'add':
            self.roi_groups[i_roigroup].extend(rois)
     
            # Draw ROIs

            if len(rois) < 3000:
                self.set_status('Plotting all ROIs...')
            else:
                self.set_status('Too many ROIs, plotting only 3 000 first...')
            
            fig, ax = self.images_plotter.get_figax()
            
            color = self.colors.to_rgba(i_roigroup%self.colors.get_clim()[1])
            
            patches = [] 
            lw = self.patch_lw_slider.get()
            fill = self.patch_fill_slider.get()/100
            fcolor = (color[0], color[1], color[2], color[3]*fill)
            for roi in rois[:3000]:

                patch = matplotlib.patches.Rectangle((float(roi[0]), float(roi[1])),
                        float(roi[2]), float(roi[3]), fill=True, edgecolor=color, facecolor=fcolor,
                        lw=lw)
                patches.append(patch)
                ax.add_patch(patch)
            
            self.roi_patches.append(patches)

        elif mode == 'remove':
            
            def _overlaps(a, b):
                return not (a[0]+a[2] < b[0] or b[0]+b[2] < a[0] or a[1]+a[3] < b[1] or b[1]+b[3] < a[1])

            for i_rgroup in range(len(self.roi_groups)) :
                
                # Remove ROIs
                remove_indices = []
                for i_old, old_roi in enumerate(self.roi_groups[i_rgroup]):    
                    for new_roi in rois:
                        if _overlaps(old_roi, new_roi):
                            remove_indices.append(i_old)
                            break
                
                print('removing {} in rg {}'.format(remove_indices, i_rgroup))

                for i_rm in remove_indices[::-1]:
                    self.roi_groups[i_rgroup].pop()

                    #self.roi_patches[i_rgroup].pop()
                
            # Remove patches separetly
            # Potential optimization if needed: Not sure if this is faster or
            #    slower than the own _overlaps
            # Anyway quite risky if rois and patches become unsynced
            #    (should be made in one-to-one correspondence)
            new_bboxes = [matplotlib.transforms.Bbox([[x, y],[x+w,y+h]]) for x,y,w,h in rois]
            for patches, selections in zip(self.roi_patches, self.selections):
                
                remove_indices = []
                for i_patch, patch in enumerate(patches):
                    if patch.get_bbox().count_overlaps(new_bboxes):
                        patch.remove()
                        remove_indices.append(i_patch)

                for i_rm in remove_indices[::-1]:
                    patches.pop(i_rm)


        else:
            raise ValueError('unkown mode {}'.format(mode))
        self.images_plotter.update()
        self.set_status('ROIs plotted :)')




    def change_image(self, slider_value=None):
        
        slider_value = int(self.image_slider.get())

        image_i = int(slider_value) -1
        print(slider_value)

        if not 0 <= image_i < len(self.image_fns):
            return None
        
        if self.use_mask_image:
            if self.mask_image is None:
                for i in range(len(self.images)):
                    self.images[i] = tifffile.imread(self.image_fns[i])
                
                self.mask_image = np.inf * np.ones(self.image_shape)
                
                for image in self.images:
                    self.mask_image = np.min([self.mask_image, image], axis=0)


        if self.images[image_i] is None:
            self.images[image_i] = tifffile.imread(self.image_fns[image_i])
        
        
        if image_i in self.exclude_images or self.image_fns[image_i] in self.exclude_images:
            self.excludetext.set_text('EXCLUDED')
        else: 
            self.excludetext.set_text('')


        if self.use_mask_image:
            showimage = self.images[image_i] - self.mask_image
        else:
            showimage = self.images[image_i]

        self.images_plotter.imshow(showimage, roi_callback=self.set_roi,
                cmap='gray', slider=self.show_controls,
                roi_drawtype=self.roi_drawtypes[self.roitype_selection.ticked[0]])


    @staticmethod
    def get_displacements(results):
        return [np.sqrt(np.array(x)**2+np.array(y)**2) for x,y in results]


    @staticmethod
    def get_destructive_displacement_mean(results):
        x = [x for x,y in results]
        y = [y for x,y in results]
        return np.sqrt(np.mean(x, axis=0)**2 + np.mean(y, axis=0)**2)


    def plot_results(self):
        self.results_plotter.ax.clear()

        for i_roi_group, result in enumerate(self.results):
            color = self.colors.to_rgba(i_roi_group%self.colors.get_clim()[1])
            displacements = [np.sqrt(np.array(x)**2+np.array(y)**2) for x,y in result]
            
            #for d in displacements[0:50]:
            #    self.results_plotter.plot(d, ax_clear=False, color=color, lw=0.5)
            
            self.results_plotter.plot(self.get_destructive_displacement_mean(result), ax_clear=False, color=color, lw=2)


    def _included_image_fns(self):
        return [fn for i_fn, fn in enumerate(self.image_fns) if fn not in self.exclude_images and i_fn not in self.exclude_images]
    

    def calculate_heatmap(self):
        '''
        Produce minimum size heatmap.
        '''
        self.heatmap_images = []
        
        # FIXME Heatmap for ROI groups not implemented properly
        # Currently just take the first nonempty ROI group
        i_roigroup = [i for i, rois in enumerate(self.roi_groups) if len(rois) != 0]
        if not i_roigroup:
            return None
        else:
            i_roigroup = i_roigroup[0]
        rois = self.roi_groups[i_roigroup]
        results = self.results[i_roigroup]

        roi_w, roi_h = rois[0][2:]

        roi_max_x = np.max([z[0] for z in rois])
        roi_min_x = np.min([z[0] for z in rois])
        roi_max_y = np.max([z[1] for z in rois])
        roi_min_y = np.min([z[1] for z in rois])
        

        step = int(self.overlap_slider.get())
        
        max_movement = float(self.maxmovement_slider.get())
        N = len(self._included_image_fns())

        for i_frame in range(N):
            image = np.zeros( (int((roi_max_y-roi_min_y)/step)+1, int((roi_max_x-roi_min_x)/step)+1) )
            for ROI, (x,y) in zip(rois, results):
                values = (np.sqrt(np.array(x)**2+np.array(y)**2))
                
                value = values[i_frame]
               
                cx = int((ROI[0]-roi_min_x)/step)
                cy = int((ROI[1]-roi_min_y)/step)
                
                try:
                    image[cy, cx] = value
                except:
                    print(image.shape)
                    print('cx {} cy {}'.format(cx, cy))
                    raise ValueError
            if np.max(image) < 0.01:
                image[0,0] = 1
            self.heatmap_images.append(image)

        self.heatmap_slider.config(from_=1, to=len(self.heatmap_images))
        self.heatmap_slider.set(1) 


    def change_heatmap(self, slider_value=None, only_return_image=False):
        #if slider_value == None:
        slider_value = int(self.heatmap_slider.get())

        i_image = int(slider_value) - 1
        image = np.copy(self.heatmap_images[i_image])
        
        # Total max value cap
        allframemax = np.max(self.heatmap_images, axis=0)
        image[allframemax > float(self.heatmapcap_slider.get())] = 0
        
        # First value max cap
        firstframemax = np.max(self.heatmap_images[0:3], axis=0)
        image[firstframemax > float(self.heatmap_firstcap_slider.get())] = 0
        
        #image = image / float(self.heatmapcap_slider.get())
        image = image / np.max(image)
    
        if only_return_image:
            return image
        else:
            self.heatmap_plotter.imshow(image, normalize=False)
   

    def set_settings(self, settings):
        for key, value in settings.items():
            if key == 'block_size':
                self.blocksize_slider.set(value)
            elif key == 'block_distance':
                self.overlap_slider.set(value)
            elif key == 'maximum_movement':
                self.maxmovement_slider.set(value)
            elif key == 'upscale':
                self.upscale_slider.set(value)
            elif key == 'cpu_cores':
                self.cores_slider.set(value)
            elif key == 'exclude_images':
                self.exclude_images = value
            elif key == 'measurement_parameters':
                self.movemeter_tickboxes.states = value


    def set_status(self, text):
        self.status.config(text=text)
        self.status.update_idletasks()
    

    def apply_movzip(self, fn=None, rois=False):
        '''
        Load parts of a movzip and apply settings from it
        to the current session.
        '''
        if fn is None:
            fn = filedialog.askopenfilename(parent=self, title='Select a movzip',
                    initialdir=MOVEDIR)

        settings, filenames, selections, roi_groups, movements = self._load_movzip(fn)
        
        if rois:
            self.selections = selections
            self.rois_groups = roi_groups
            
            self.update_grid()


    def _save_movzip(self, fn=None, only=None):
        '''
        only : bool, string or list of strings
        '''

        if isinstance(only, str):
            only = [only]

        if fn is None:
            if only:
                title = 'Save '+','.join(only)
            else:
                title = 'Save movzip'
            fn = filedialog.asksaveasfilename(parent=self, title=title,
                    initialdir=MOVEDIR)
            
            if not fn.endswith('.zip'):
                fn = fn+'.zip'

        # Dump GUI settings
        settings = {}
        settings['block_size'] = self.blocksize_slider.get()
        settings['block_distance'] = self.overlap_slider.get()
        settings['maximum_movement'] = self.maxmovement_slider.get()
        settings['upscale'] = self.upscale_slider.get()
        settings['cpu_cores'] = self.cores_slider.get() 
        settings['export_time'] = str(datetime.datetime.now())
        settings['movemeter_version'] = __version__
        settings['exclude_images'] = self.exclude_images
        settings['measurement_parameters'] = self.movemeter_tickboxes.states

        if self.images:
            settings['images_shape'] = self.image_shape
        
        
        movzip = {'metadata': settings,
                'image_filenames': self._included_image_fns(),
                'selections': self.selections,
                'rois': self.roi_groups,
                'movements': self.results}

        self.set_status('Saving movzip...')
        
        with zipfile.ZipFile(fn, 'w') as savezip:
            for pfn, obj in movzip.items():

                if only and pfn not in only:
                    continue

                with savezip.open(pfn+'.json', 'w') as fp:
                    fp.write(json.dumps(obj).encode('utf-8'))
        
        self.set_status('Mozip saved.')
        


    def _load_movzip(self, fn):
        '''
        Returns settings, image_filenames, selections, rois, movements
        '''

        movzip = []

        with zipfile.ZipFile(fn, 'r') as loadzip:
            
            for pfn in ['metadata', 'image_filenames', 'selections', 'rois', 'movements']:
                try:
                    with loadzip.open(pfn+'.json', 'r') as fp:
                        movzip.append( json.loads(fp.read()) )
        
                except KeyError:
                    movzip.append(None)

        return (*movzip,)

    
    def save_roiview(self, only_rois=False):
        savefn = filedialog.asksaveasfilename()
        if savefn:
            fig = self.images_plotter.figure
            
            if only_rois:
                self.images_plotter.imshow_obj.set_visible(False)
            
            fig.savefig(savefn, dpi=600, transparent=only_rois)
            
            if only_rois:
                self.images_plotter.imshow_obj.set_visible(True)



    def export_results(self, batch_name=None):

        savename = self.export_name.get()
        zipsavename = savename

        save_root = MOVEDIR
        if batch_name is not None:
            save_root = os.path.join(save_root, 'batch', batch_name)
        
        save_directory = os.path.join(save_root, savename)
        os.makedirs(save_directory, exist_ok=True)
    
        self._save_movzip(os.path.join(save_directory, 'movemeter_{}.zip'.format(zipsavename)))
        
        means = []

        for i_roigroup, results in enumerate(self.results):
            fn = os.path.join(save_directory, 'movements_{}_rg{}.csv'.format(zipsavename, i_roigroup))
            
            displacements = self.get_displacements(results)
            
            if not displacements:
                continue

            dm_displacement = self.get_destructive_displacement_mean(results)

            with open(fn, 'w') as fp:
                writer = csv.writer(fp, delimiter=',')
                
                writer.writerow(['time (s)', 'mean displacement (pixels)', 'destructive mean displacement (pixels)'] + ['ROI{} displacement (pixels)'.format(k) for k in range(len(displacements))])

                for i in range(len(displacements[0])):
                    row = [displacements[j][i] for j in range(len(displacements))]
                    row.insert(0, dm_displacement[i])
                    row.insert(0, np.mean(row))
                    row.insert(0, i/self.fs)
                    writer.writerow(row)

                if i_roigroup == 0:
                    N = len(dm_displacement)
                    means.append(np.linspace(0, (N-1)/self.fs, N))
                means.append(dm_displacement)

        with open(os.path.join(save_directory, 'summary_desctructive_{}.csv'.format(zipsavename)), 'w') as fp:
            writer = csv.writer(fp,  delimiter=',')

            writer.writerow(['time (s)'] +['roi group {} (pixels)'.format(i) for i in range(len(means)-1)])

            for i in range(len(means[0])):
                row = [m[i] for m in means]
                writer.writerow(row)


        slider_i = int(self.image_slider.get())
        self.image_slider.set(int(len(self._included_image_fns()))/2)
        #change_image(slider_value=int(len(self._included_image_fns())/2))

        # Image of the ROIs
        self.set_status('Saving the image view')
        fig, ax = self.images_plotter.get_figax()
        fig.savefig(os.path.join(save_directory, 'movemeter_imageview.jpg'), dpi=400, pil_kwargs={'optimize': True})
        
        self.image_slider.set(slider_i)
        #change_image(slider_value=int(len(self._included_image_fns())/2))
        
        # Image of the result traces
        self.set_status('Saving the results view')
        fig, ax = self.results_plotter.get_figax()
        fig.savefig(os.path.join(save_directory, 'movemeter_resultsview.jpg'), dpi=400, pil_kwargs={'optimize': True})

        # Image of the result traces
        #fig, ax = self.heatmap_plotter.get_figax()
        #fig.savefig(os.path.join(save_directory, 'heatmap_view.jpg'), dpi=600, optimize=True)
        
        
        def save_heatmaps(heatmaps, image_fns, savedir):
            
            for fn, image in zip(image_fns, heatmaps):
                tifffile.imsave(os.path.join(savedir, 'ht_{}'.format(os.path.basename(fn))), image.astype('float32'))
            
            # Save mean heatmap image with scale bar using matplotlib
            # FIXME Expose option for how many last images to save the mean for
            meanimage = np.mean(heatmaps[-min(5, len(heatmaps)):], axis=0)
            
            if False:
                # This was used to clip heatmap values
                # FIXME Expose option in the GUI
                if 'musca' in save_directory:
                    meanimage = np.clip(meanimage, 0, 50)
                    if np.max(meanimage) < 50:
                        meanimage[0,0] = 50
                else:
                    meanimage = np.clip(meanimage, 0, 6)
                    if np.max(meanimage) < 6:
                        meanimage[0,0] = 6

            fig, ax = plt.subplots()
            imshow = ax.imshow(meanimage)
            ax.set_axis_off()

            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(imshow, cax=cax)
            
            fig.savefig(os.path.join(savedir, 'ht_mean.png'), dpi=800)
            
            plt.show(block=False)
            plt.pause(0.01)
            plt.close(fig)
        
        self.set_status('Saving heatmaps')
        subsavedir = os.path.join(save_directory, 'heatmap_tif')
        os.makedirs(subsavedir, exist_ok=True)
         
        save_heatmaps(self.heatmap_images, self.image_fns, subsavedir)
        
        self.set_status('DONE Saving :)')
          

def main():
    '''
    Initialize tkinter and place the Movemeter GUI
    on the window.
    '''
    root = tk.Tk()
    root.title('Movemeter - Tkinter GUI - {}'.format(__version__))
    gui = MovemeterTkGui(root)
    gui.grid(row=1, column=1, sticky='NSWE')
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)
    root.mainloop()


if __name__ == "__main__":
    main()
