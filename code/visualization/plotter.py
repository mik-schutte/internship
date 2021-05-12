'''
    plotter.py

    visualises one of the .csv files in the results folder that
    have been generated by the main.py code.
'''
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from brian2.units.stdunits import mV, ms, mS, uA, nA, namp

def plot_dynamicclamp(inj_dynamic, voltage, hidden_state, dt, window=None):
    '''Plots the injected conductance and voltage trace.

       INPUT
       window = [start:stop] in ms
    '''
    g_exc, g_inh = inj_dynamic

    # Check
    if window:
        start, stop = window
        g_exc = g_exc[start:stop]
        g_inh = g_inh[start:stop]
        voltage = voltage[start:stop]
        hidden_state = hidden_state[start:stop]
        time = np.arange(start, stop)
        dt = 1
    else:
        start = 0
        time = np.arange(start, len(hidden_state))*dt

    # Plot
    fig, axs = plt.subplots(3, figsize=(12,12))
    fig.suptitle('Dynamic Clamp')
    for idx, val in enumerate(hidden_state):
        idx += start
        if val == 1:
            axs[0].axvline(idx*dt, c='lightgray')
            axs[1].axvline(idx*dt, c='lightgray')
            axs[2].axvline(idx*dt, c='lightgray')

    axs[0].plot(time, abs(g_exc), c='red')
    axs[0].set(ylabel='Exc. conductance [mS]')

    axs[1].plot(time, abs(g_inh), c='blue')
    axs[1].set(ylabel='Inh. conductance [mS]')

    axs[2].plot(time, voltage, c='black')
    axs[2].set(ylabel='Voltage [mV]', xlabel='Time [ms]')
    plt.show()
    return


def plot_currentclamp(inj_current, voltage, hidden_state, dt, window=None):
    '''Plots the injected current and voltage trace
    '''
    # Check
    if window:
        start, stop = window
        inj_current = inj_current[start:stop]
        voltage = voltage[start:stop]
        hidden_state = hidden_state[start:stop]
        time = np.arange(start, stop)
        dt = 1
    else:
        start = 0
        time = np.arange(start, len(hidden_state))*dt

    fig, axs = plt.subplots(2, figsize=(12,12))
    fig.suptitle('Current Clamp')
    for idx, val in enumerate(hidden_state):
        idx += start
        if val == 1:
            axs[0].axvline(idx*dt, c='lightgray')
            axs[1].axvline(idx*dt, c='lightgray')
    axs[0].plot(time, inj_current, c='red')
    axs[0].set(ylabel='Input current [uA]')
  
    axs[1].plot(time, voltage, c='black')
    axs[1].set(ylabel='Voltage [mV]', xlabel='Time [ms]')
    plt.show()
    return


def plot_compare(dynamic_statemon, current_statemon, hiddenstate, dt):
    ''' Compares the dynamic voltage trace and current voltage trace.
    '''
    fig, axs = plt.subplots(2, figsize=(12,12))
    fig.suptitle('Comparison between Dynamic and Current Clamp', y=0.95)

    for idx, val in enumerate(hiddenstate):
        if val == 1:
            axs[0].axvline(idx*dt, c='lightgray')
    axs[0].title.set_text('Dynamic Clamp')
    axs[0].plot(dynamic_statemon.t/ms, dynamic_statemon.v[0].T/mV, c='black')
    axs[0].set(ylabel='Voltage [mV]', xlabel='Time [ms]')

    for idx, val in enumerate(hiddenstate):
        if val == 1:
            axs[1].axvline(idx*dt, c='lightgray')
    axs[1].title.set_text('Current Clamp')
    axs[1].plot(current_statemon.t/ms, current_statemon.v[0].T/mV, c='black')
    axs[1].set(ylabel='Voltage [mV]', xlabel='Time [ms]')
    plt.show()
    return


def plot_special(axes, array, mini, maxi, col=None, label=None):
    ''' Creates a line over an histogram to represent a distribution '''
    x = np.linspace(mini, maxi)
    density = stats.gaussian_kde(array)
    axes.plot(x, density(x), color=col, label=label)
    return


def plot_clampcell_MI(MI_data):
    ''' Plot the results of the clamp comparison simulation0
    '''
    # Load Data
    MI_PC_current = [run['MI'] for run in MI_data['PC_current']]
    MI_PC_dynamic = [run['MI'] for run in MI_data['PC_dynamic']]
    MI_IN_current = [run['MI'] for run in MI_data['IN_current']]
    MI_IN_dynamic = [run['MI'] for run in MI_data['IN_dynamic']]

    ## Statistical data
    PC_N = len(MI_PC_current)
    IN_N = len(MI_IN_current)
    current_means = [np.nanmean(MI_PC_current), np.nanmean(MI_IN_current)]
    current_sem = [np.nanstd(MI_PC_current)/PC_N, np.nanstd(MI_IN_current)/IN_N]
    dynamic_means = [np.nanmean(MI_PC_dynamic), np.nanmean(MI_IN_dynamic)]
    dynamic_sem = [np.nanstd(MI_PC_dynamic)/PC_N, np.nanstd(MI_IN_dynamic)/IN_N]

    # Plot
    sns.set_context('talk')
    fig, ax = plt.subplots(figsize=(12, 8))
    x = np.arange(2)
    bar_width = 0.25

    ## Make bars
    b1 = ax.bar(x, height=current_means, label='Current Clamp', yerr=current_sem, capsize=4,
    color= ['red','blue'], width=bar_width, edgecolor='black')
    b2 = ax.bar(x + bar_width, height=dynamic_means, label='Dynamic Clamp', yerr=dynamic_sem, capsize=4,
    color= ['lightcoral', 'royalblue'], width=bar_width, edgecolor='black')

    ## Fix x-axis
    ax.set_xticks(x + bar_width/2)
    ax.set_xticklabels(['Pyramidal Cell', 'Interneuron'])

    # Add legend
    plt.legend()

    # Axis styling
    ax.set_ylabel('Mutual Information')
    ax.set_title('Mutual Information in different clamps')
    plt.show()


def plot_regime_compare(pathorlist):    
    ''' Plots the injected current and membrane potential 
        of different hidden state regimes.

        pathorlist : path to the regime_compare folder or [slow, fast, slow_high, fast_low]
    '''
    # Check input
    if isinstance(pathorlist, str):
        regimes = ['slow.npy', 'fast.npy', 'slow_high.npy', 'fast_low.npy']
        slow = np.load('results/saved/regime_compare/'+regimes[0], allow_pickle=True).item()
        fast = np.load('results/saved/regime_compare/'+regimes[1], allow_pickle=True).item()
        slow_high = np.load('results/saved/regime_compare/'+regimes[2], allow_pickle=True).item()
        fast_low = np.load('results/saved/regime_compare/'+regimes[3], allow_pickle=True).item()

    elif isinstance(pathorlist, list) or isinstance(pathorlist, np.array):
        slow, fast, slow_high, fast_low = pathorlist
    
    else: 
        raise AssertionError('Input should be a path to the saved .npy files or [PC_results, IN_results].')

    # Plot
    fig, axs = plt.subplots(ncols=2, figsize=(10, 10))
    plot_special(axs[0], slow['input'], col='blue', label='Slow')
    plot_special(axs[0], fast['input'], col='red', label='Fast')
    plot_special(axs[0], slow_high['input'], col='green', label='Slow High')
    plot_special(axs[0], fast_low['input'], col='purple', label='Fast Low')
    axs[0].set(xlabel='Input Current [nA]')
    axs[0].title.set_text('Input Current distribution')

    plot_special(axs[1], slow['potential'], col='blue', label='Slow')
    plot_special(axs[1], fast['potential'], col='red', label='Fast')
    plot_special(axs[1], slow_high['potential'], col='green', label='Slow High')
    plot_special(axs[1], fast_low['potential'], col='purple', label='Fast Low')
    axs[1].set(xlabel='Membrane Potential [mV]')
    axs[1].title.set_text('Membrane Potential distribution')
    plt.legend()
    plt.show()


def plot_dt_compare(pathorlist):
    ''' Plot the results of the dt_compare simulation.
        
        pathorlist : path to the dt_compare results folder or [PC_results, IN_results]
    '''
    # Check input
    if isinstance(pathorlist, str):
        PC_results_I = np.load(pathorlist + 'PC_results.npy', allow_pickle=True).item()['I']
        PC_results_Vm = np.load(pathorlist + 'PC_results.npy', allow_pickle=True).item()['Vm']
        IN_results_I = np.load(pathorlist + 'IN_results.npy', allow_pickle=True).item()['I']
        IN_results_Vm = np.load(pathorlist + 'IN_results.npy', allow_pickle=True).item()['Vm']

    elif isinstance(pathorlist, list) or isinstance(pathorlist, np.array):
        PC_results, IN_results = pathorlist
        PC_results_I = PC_results['I']
        PC_results_Vm = PC_results['Vm']
        IN_results_I = IN_results['I']
        IN_results_Vm = IN_results['Vm']
    
    else: 
        raise AssertionError('Input should be a path to the saved .npy files or [PC_results, IN_results].')

    # Get sampling rates
    sampling_array = PC_results_I.keys()

    # Plot the figure
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))
    for sampling_rate in sampling_array:
        plot_special(axs[0, 0], PC_results_I[sampling_rate], -500, 500, label=sampling_rate)
        plot_special(axs[0, 1], PC_results_Vm[sampling_rate], -100, -50, label=sampling_rate)
        plot_special(axs[1, 0], IN_results_I[sampling_rate], -500, 500, label=sampling_rate)
        plot_special(axs[1, 1], IN_results_Vm[sampling_rate], -100, -50, label=sampling_rate)
    axs[0, 0].set(xlabel='Input Current [uA]')
    axs[0, 0].title.set_text('Pyramidal Cells')
    axs[0, 1].set(xlabel='Membrane Potential [mV]')
    axs[0, 1].title.set_text('Pyramidal Cells')
    axs[1, 0].set(xlabel='Input Current [uA]')
    axs[1, 0].title.set_text('Interneurons')
    axs[1, 1].set(xlabel='Membrane Potential [mV]')
    axs[1, 1].title.set_text('Interneurons')
    plt.legend()
    plt.show()


def plot_scaling_compare(pathorlist):
    ''' Plots the injected current, membrane potential and frequency
        of different dynamic scaling scales.

        pathorlist : path to the scaling_compare results folder or [current_dict, dynamic_dict]
    '''
    # Check input
    if isinstance(pathorlist, str):
        current_dict = np.load(pathorlist + 'current_dict.npy', allow_pickle=True).item()
        dynamic_dict = np.load(pathorlist + 'dynamic_dict.npy', allow_pickle=True).item()

    elif isinstance(pathorlist, list) or isinstance(pathorlist, np.array):
        current_dict, dynamic_dict = pathorlist
    
    else: 
        raise AssertionError('Input should be a path to the saved .npy files or [PC_results, IN_results].')

    scale_array = dynamic_dict['PC']['I'].keys()
    N = len(scale_array)
    x = np.arange(N+1)

    fig, axs = plt.subplots(ncols=3, figsize=(15,8))

    # I 
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in current_dict['PC']['I'].values()], color='red', s=125, marker='^', ax=axs[0])
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in dynamic_dict['PC']['I'].values()], color='lightcoral', s=100, marker='d', ax=axs[0])
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in current_dict['IN']['I'].values()], color='blue', s=100, marker='p', ax=axs[0])
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in dynamic_dict['IN']['I'].values()], color='royalblue', s=90, marker='o', ax=axs[0])
    # Vm
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in current_dict['PC']['Vm'].values()], color='red', s=100, marker='^', ax=axs[1])
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in dynamic_dict['PC']['Vm'].values()], color='lightcoral', s=100, marker='d', ax=axs[1])
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in current_dict['IN']['Vm'].values()], color='blue', s=100, marker='p', ax=axs[1])
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in dynamic_dict['IN']['Vm'].values()], color='royalblue', s=90, marker='o', ax=axs[1])
    # F
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in current_dict['PC']['f'].values()], color='red', s=100, marker='^', ax=axs[2], label='Current, PC')
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in dynamic_dict['PC']['f'].values()], color='lightcoral', s=100, marker='d', ax=axs[2], label='Dynamic, PC')
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in current_dict['IN']['f'].values()], color='blue', s=100, marker='p', ax=axs[2], label='Current, IN')
    sns.scatterplot(x=scale_array, y=[np.mean(i) for i in dynamic_dict['IN']['f'].values()], color='royalblue', s=90, marker='o', ax=axs[2], label='Dynamic, IN')

    plt.legend()
    axs[0].set(ylabel='Input Current[uA]')
    axs[0].title.set_text('Injected current')
    axs[1].set(ylabel='Membrane potential [mV]', xlabel='scale')
    axs[1].title.set_text('Membrane potential')
    axs[2].set(ylabel='Frequency [Hz]',  xlabel='scale')
    axs[2].title.set_text('Firing frequency')

    fig.suptitle('Scaling effect')
    plt.legend(['Current, PC', 'Dynamic, PC', 'Current, IN', 'Dynamic, IN'])
    axs[2].axhline(y=1.4233, c='red')
    axs[2].axhline(y=6.6397, c='blue')
    plt.show()


def plot_ISI_compare(pathordict):
    '''docstring
    '''
    # Check input
    if isinstance(pathordict, str):
        ISI = np.load(pathordict, allow_pickle=True).item()

    elif isinstance(pathordict, dict):
        ISI = pathordict
    
    else: 
        raise AssertionError('Input should be a path to the saved .npy file or {current_PC, dynamic_PC, current_IN, dynamic_IN}.')
    
    # Plot
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10,10))
    sns.histplot(ISI['current_PC'], ax=axs[0,0], kde=True, bins=50, color='red')
    sns.histplot(ISI['dynamic_PC'], ax=axs[0,1], kde=True, bins=50, color='red')
    sns.histplot(ISI['current_IN'], ax=axs[1,0], kde=True, bins=50, color='blue')
    sns.histplot(ISI['dynamic_IN'], ax=axs[1,1], kde=True, bins=50, color='blue')

    axs[0, 0].set_yscale('log')
    axs[0, 0].title.set_text('current PC')
    axs[0, 1].title.set_text('dynamic PC')
    axs[1, 0].title.set_text('current IN')
    axs[1, 1].title.set_text('dynamic IN')
    axs[0, 0].set_ylabel('')
    axs[0, 1].set_ylabel('')
    axs[1, 0].set_ylabel('')
    axs[1, 1].set_ylabel('')
    fig.text(0.5, 0.04, 'ISI (ms)', ha='center')
    fig.text(0.04, 0.5, 'Frequency', va='center', rotation='vertical')
    plt.show()
