'''
Default dynamic parameters and ParameterEditor for letting the user
modify them in the program.
'''
import os
import time
import ast
import json

from gonioimsoft.directories import PUPILDIR


DEFAULT_DYNAMIC_PARAMETERS = {'isi': 10.0, 'repeats': 1, 'pre_stim': 0.000,
        'stim': 0.200, 'post_stim': 0.00, 'frame_length' : 0.010,
        'ir_imaging': 5, 'ir_waiting': 0, 'ir_livefeed': 1,
        'flash_on': 8, 'flash_off': 0,
        'ir_channel': "Dev1/ao1", 'flash_channel': "Dev1/ao0",
        'suffix': '', 'trigger_channel': "/Dev1/PFI0",
        'trigger_out_channel': "Dev2/ao0",
        'biosyst_stimulus': '',
        'biosyst_channel': 2,
        'avgint_adaptation': 0,
        'flash_type': 'square',
        'save_stack': False}

DYNAMIC_PARAMETERS_TYPES = {'seconds': ['isi', 'pre_stim', 'stim', 'post_stim', 'frame_length', 'avgint_adaptation'],
        'voltage': ['ir_imaging', 'ir_waiting', 'ir_livefeed', 'flash_on', 'flash_off'],
        'channel': ['ir_channel', 'flash_channel', 'trigger_channel', 'trigger_out_channel'],
        'integer': ['repeats', 'biosyst_channel'],
        'string': ['suffix', 'biosyst_stimulus', 'flash_type'],
        'boolean': ['save_stack']}


DYNAMIC_PARAMETERS_HELP = {'isi': 'Inter stimulus intervali[s]',
        'repeats': 'How many times the protocol is repeated',
        'pre_stim': 'How long to image before the pulse [s]',
        'stim': 'Stimulus (step pulse) length [s]',
        'post_stim': 'How long to image after the pulse [s]',
        'frame_length': 'Exposure time / inter-frame interval',
        'ir_imaging': 'IR brightness during image acqusition',
        'ir_waiting': 'IR brightness when waiting ISI',
        'ir_livefeed': 'IR brightness while updating the live image',
        'flash_on': 'Flash brightness during stim',
        'flash_off':' Flash brightness during image acqustition',
        'ir_channel': 'NI channel for IR',
        'flash_channel': 'NI channel for Flash',
        'trigger_channel': 'Trigger recieve/in channel',
        'trigger_out_channel': 'Trigger send/out channel',
        'suffix': 'Tag added to the saved folders',
        'biosyst_stimulus': 'Override the square pulse by a biosyst stimulus',
        'biosyst_channel': 'Channel of the biosyst simulus',
        'avgint_adaptation': 'Time to show stimulus mean value before imaging [s]',
        'flash_type': '"square" or sinelogsweep',
        'save_stack': 'If true, save stack instead separate images'}


def getRightType(parameter_name, string_value):
    '''
    Convert user inputted string to correct parameter value based on
    DYNAMIC_PARAMETER_TYPES

    TODO    - channel checking, check that the channel is proper NI channel
    '''
    if parameter_name in DYNAMIC_PARAMETERS_TYPES['integer']:
        return int(string_value)

   
    if parameter_name in DYNAMIC_PARAMETERS_TYPES['seconds']:
        if string_value.startswith('[') and string_value.endswith(']'):
            seconds = ast.literal_eval(string_value)

            for s in seconds:
                if s < 0:
                    raise ValueError('Here time is required to be strictly positive.')
        else:
            seconds = float(string_value)
            if seconds < 0:
                raise ValueError('Here time is required to be strictly positive.')
        return seconds

    if parameter_name in  DYNAMIC_PARAMETERS_TYPES['voltage']:
        if string_value.startswith('[') and string_value.endswith(']'):
            voltages = ast.literal_eval(string_value)
            for voltage in voltages:
                if not -10<=voltage<=10:
                    raise ValueError('Voltage value range -10 to 10 V exceeded.')
            return voltages
        else:
            voltage = float(string_value)
            if not -10<=voltage<=10:
                raise ValueError('Voltage value range -10 to 10 V exceeded.')
            return voltage

    if parameter_name in  DYNAMIC_PARAMETERS_TYPES['channel']:
        if type(string_value) == type(''):
            if string_value.startswith('[') and string_value.endswith([']']):
                return ast.literal_eval(string_value)
            else:
                return string_value
    
    if parameter_name in DYNAMIC_PARAMETERS_TYPES['string']:
        return str(string_value)

    if parameter_name in DYNAMIC_PARAMETERS_TYPES['boolean']:
        if string_value.lower() == 'true':
            return True
        elif string_value.lower() == 'false':
            return False
        else:
            raise ValueError('Boolean falue has to be either "True" or "False"')

    raise NotImplementedError('Add {} correctly to DYNAMIC_PARAMETER_TYPES in dynamic_parameters.py')



def load_parameters(fn):
    '''
    Loading imaging parameters, saved as a json file.
    '''
    with open(fn, 'r') as fp:
        data = json.load(fp)
    return data


def save_parameters(fn, parameters):
    '''
    Loading imaging parameters, saved as a json file.
    '''
    with open(fn, 'w') as fp:
        json.dump(parameters, fp)



class ParameterEditor:
    '''
    Dictionary editor on command line with ability to load and save presets.
    '''
    def __init__(self, dynamic_parameters, locked_parameters={}):
        '''
        dynamic_parameters      Dictionary of the dynamic imaging parameters.
        '''
        self.dynamic_parameters = dynamic_parameters
        self.parameter_names = sorted(self.dynamic_parameters.keys())

        self.presets_savedir = os.path.join(PUPILDIR, 'presets')
        self.presets = self.load_presets(self.presets_savedir)

        self.locked_parameters = locked_parameters

    
    def load_presets(self, directory):
        
        presets = {}
        
        if os.path.isdir(directory):
            files = [os.path.join(directory, fn) for fn in os.listdir(directory)]
        else:
            files = []

        for afile in files:
            try:
                preset = load_parameters(afile)
            except:
                print("Couldn't load preset {}".format(afile))
                continue
            
            # If older files lack some parameters, use default parameters
            for key in self.parameter_names:
                if not key in preset:
                    preset[key] = DEFAULT_DYNAMIC_PARAMETERS[key]
                    
            presets[os.path.basename(afile)] = preset

        return presets


    def print_preset(self, preset):
        '''
        Prints the current parameters and the help strings.
        '''
                 
        parameter_names = sorted(self.dynamic_parameters.keys())

        print()
        
        print('{:<20} {:<40} {}'.format('PARAMETER NAME', 'VALUE', 'DESCRIPTION'))
        for parameter in parameter_names:
            if parameter in self.locked_parameters:
                lck = ' (LOCKED to {})'.format(self.locked_parameters[parameter])
            else:
                lck = ''
            print('{:<20} {:<40} {}'.format(parameter, str(preset[parameter])+lck,
                DYNAMIC_PARAMETERS_HELP[parameter]))
        print()


    def getModified(self):
        '''
        Ask user to edit the parameters until happy and then return
        the parameters.
        '''
        
        while True:
            print('MODIFYING IMAGING PARAMETERS')
            self.print_preset(self.dynamic_parameters)
            parameter = input('Parameter name or (list/save/load) (Enter to continue) >> ')
            
            # If breaking free
            if parameter == '':
                break
            

            self.presets = self.load_presets(self.presets_savedir)

            
            # If saving preset
            if parameter.lower() == 'save':
                name = input('Save current parameters under preset name (if empty == suffix) >> ')
                if name == '' and self.dynamic_parameters['suffix'] != '':
                    name = self.dynamic_parameters['suffix']
                
                if os.path.isdir(PUPILDIR):
                    os.makedirs(self.presets_savedir, exist_ok=True)
                    save_parameters(os.path.join(self.presets_savedir, name), self.dynamic_parameters)
                else:
                    print('Saving the preset failed, {} does not exist'.format(PUPILDIR))

                continue        

            if parameter.lower() == 'list':
                if self.presets is {}:
                    print('There are no existing presets!')
                else:
                    print('These are the existing presets:')
                    for preset in self.presets.keys():
                        print('  '+preset)
                    print('')
                continue

            if parameter.lower() == 'load':
                # If parameter is actually a preset
                
                while True:
                    
                    preset_names = sorted(self.presets.keys())

                    for i, name in enumerate(preset_names):
                        print('{}) {}'.format(i+1, name))
                    
                    sel = input('>> ')

                    try:
                        to_load = preset_names[int(sel)-1]
                        break
                    except:
                        print('Invalid preset.')

                parameter = to_load

            if parameter in self.presets.keys():
                self.print_preset(self.presets[parameter])
                
                confirm = input('Load this (y/n)>> ').lower()
                if confirm and confirm[0] == 'y':
                    self.dynamic_parameters = self.presets[parameter]
                else:
                    print('Answer not yes, loading of the preset cancelled')
                continue
            
    

            try:
                self.dynamic_parameters[parameter]
            except KeyError:
                print('Invalid input, not a parameter name')
                time.sleep(1)
                continue

            while True:

                value = input('Value for {} >> '.format(parameter))
                
                if value == '':
                    break

                try:
                    value = getRightType(parameter, value)
                except ValueError as e:
                    print(str(e))
                    print('Could not convert the value to right type. Try againg or Enter to skip.')
                    continue

                self.dynamic_parameters[parameter] = value
                break

        return {**self.dynamic_parameters, **self.locked_parameters}


def getModifiedParameters(**kwargs):
    '''
    Take in the DEFAULT parameters in the beginning of this code file
    and let the user modify them using text based ParameterEditor
    '''
    editor = ParameterEditor(DEFAULT_DYNAMIC_PARAMETERS, **kwargs)
    return editor.getModified()



if __name__ == "__main__":
    print(getModifiedParameters())


