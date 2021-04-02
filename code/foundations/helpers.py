''' helpers.py
    
    Helps you out :)
''' 
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import numpy as np
from brian2 import *
from models.models import Barrel_PC, Barrel_IN

def scale_to_freq(neuron, input_theory, target, on_off_ratio, clamp_type, duration, hidden_state, dt=0.5, Ni=None):
    ''' Scales the theoretical input to an input that results in target firing frequence 
        by running test simulations. 

        INPUT
        neuron (Class): neuron model as found in models.py
        input_theory (array or tuple): theoretical input that has to be scaled; (g_exc, g_inh) if dynamic
        target (int): target frequency for the simulation
        on_off_ratio (float): how much more does the neuron need to fire during the ON state
        clamp_type (str): 'current' or 'dynamic' 
        duration (int): duration of the simulation in miliseconds
        hidden_state (array): binary array representing the hidden state
        dt (float): time step of the simulation and hiddenstate
        Ni (int): index of the neuron to be simulated

        OUTPUT
        inj_input (brian2.TimedArray): the input that results in the target firing frequency
    '''
    # Checks
    try:
        if neuron.stored == False:
            neuron.store()
    except:
        raise TypeError('Please insert a neuron class')
    if clamp_type != 'current' and clamp_type != 'dynamic':
        raise ValueError('ClampType must be \'current\' or \'dynamic\'')

    freq_diff_list = []
    scale_list =[1, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25]
    for idx, scale in enumerate(scale_list):
        neuron.restore()

        # Scale and run
        inj = scale_input_theory(input_theory, clamp_type, 0, scale, dt)
        M, S = neuron.run(inj, duration*ms, Ni)

        # Compare against frequency target
        freq = S.num_spikes/(duration/1000)
        freq_diff = abs(freq - target)
        freq_diff_list.append(freq_diff)

        # Compare against on_frequency target
        spiketrain = make_spiketrain(S, hidden_state, dt)
        on_freq = get_on_freq(spiketrain, hidden_state, dt)

        # Check if prior scale wasn't a better fit
        if idx != 0 and freq_diff_list[idx-1] < freq_diff:
            # Check for ON/OFF ratio
            if on_freq != 0 and freq != 0 and on_freq/freq < on_off_ratio:
                print('FAILED: ratio not met')
                neuron.restore()
                return False

            neuron.restore()
            return scale_input_theory(input_theory, clamp_type, 0, scale_list[idx-1], dt)

    # Check for ON/OFF ratio
    if on_freq/freq < on_off_ratio:
        print('FAILED: ratio not met')   
        neuron.restore()
        return False

    neuron.restore()
    return scale_input_theory(input_theory, clamp_type, 0, scale_list[-1], dt)
    
def scale_input_theory(input_theory, clamp_type, baseline, scale, dt):
    ''' Scales the theoretical current or dynamic input with a scale factor. 
        
        INPUT
        input_theory (array or tuple): array of theoretical current or (g_exc, g_inh)
        clamp_type (str): 'current' or 'dynamic'
        scale (float): scaling factor
        dt (float): time step of the simulation

        OUTPUT
        inj_input (brian2.TimedArray): the scaled input
    '''
    if clamp_type == 'current':
        scaled_input = (baseline + input_theory * scale)*uamp
        inject_input = TimedArray(scaled_input, dt=dt*ms)

    elif clamp_type == 'dynamic':
        # Check for correct inpuy
        try: 
            g_exc, g_inh = dynamic_theory
        except: 
            ValueError('For scaling of dynamic theory insert (g_exc, g_inh).')
        g_exc = baseline + g_exc*mS * scale
        g_inh = g_inh*mS * scale
        g_exc = TimedArray(g_exc, dt=dt*ms)
        g_inh = TimedArray(g_inh, dt=dt*ms)
        inject_input = (g_exc, g_inh)

    return inject_input

def make_spiketrain(S, hiddenstate, dt):
    ''' Generates a binary array that spans the whole simulation and 
        is 1 when a spike is fired.
    '''
    spiketrain = np.zeros((1, hiddenstate.shape[0]))
    spikeidx = np.array(S.t/ms/dt, dtype=int)
    spiketrain[:, spikeidx] = 1
    return spiketrain

def get_spike_intervals(S):
    ''' Determine the interval between spikes in milliseconds. 
    '''
    # Check
    if not isinstance(S, StateMonitor):
        TypeError('No SpikeMonitor provided')
        
    intervals = []
    for i in range(len(S.t)-1):
        intervals.append(abs(S.t[i+1] - S.t[i])/ms)
    return intervals

def get_on_index(hidden_state):
    ''' Get the indexis where the hidden state is ON.
    '''
    # Index where hidden state is ON
    on_idx = []
    for idx, val in enumerate(hidden_state):
        if val == 1:
            on_idx.append(idx)
    return on_idx

def get_on_spikes(spiketrain, hidden_state):
    ''' Get the index where spikes are fired during ON-state.
    '''
    # ON index
    on_idx = get_on_index(hidden_state)

    # Spike index
    spike_idx = np.where(spiketrain==1)[1]

    # Spikes when hidden state is ON
    on_spikes = []
    for idx in spike_idx:
        if idx in on_idx:
            on_spikes.append(idx)
    return on_spikes

def get_on_freq(spiketrain, hidden_state, dt):
    ''' Get firing frequency during on state in Hertz (Hz).
    '''
    on_spike_count = len(get_on_spikes(spiketrain, hidden_state))
    on_duration = len(get_on_index(hidden_state))*dt*ms
    return (on_spike_count/on_duration)/Hz