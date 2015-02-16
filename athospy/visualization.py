import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def set_styles():
    '''Sets matplotlib and pyplot plotting styles
    '''
    # not sure why this doesnt work if called outside of the function
    plt.style.use('ggplot')	
    mpl.rc('figure', figsize=[16, 4])
    mpl.rc('xtick', labelsize=12) 
    mpl.rc('ytick', labelsize=12)
    mpl.rc('font', size=12)
    mpl.rc('axes', titlesize=13)


def plot_emg(df, title=''):
    '''plot EMG data sampled at 41.7 Hz
    '''
    df_emgR = df.loc[:, ['RGM','RBF','RVM','RVL']]
    df_emgL = df.loc[:, ['LGM','LBF','LVM','LVL']]
    
    fs = 41.7
    N = len(df)
    t = np.linspace(0, N/fs, N)

    fig, ax = plt.subplots(2, 1, sharex=True)
    df_emgR.plot(ax=ax[0], x=t).legend(loc='center left', bbox_to_anchor=(1, 0.5))
    df_emgL.plot(ax=ax[1], x=t).legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax[0].set_ylabel('Right EMG')
    ax[1].set_ylabel('Left EMG')
    ax[1].set_xlabel('time [sec]')
    
    plt.suptitle(title)
    
    return fig, ax


def plot_qc(df_qc, figsize=(16, 6)):
    '''Plot distribution of quality metrics across files.
    '''
    y = np.random.randn(len(df_qc))
    fig, ax = plt.subplots(df_qc.shape[1], figsize=figsize)
    for i, axi in enumerate(ax):
        axi.scatter(df_qc.iloc[:,i], y)

        axi.set_title(df_qc.columns[i])
        axi.set_yticks([])
        axi.get_xaxis().set_tick_params(direction='in')
        fig.tight_layout(pad=0.4)

    return fig, ax


def plot_confusion(mat, classes):
    '''Plot confusion matrix, with class labels.
    '''
    figsize = mpl.rcParams['figure.figsize']
    mpl.rc('figure', figsize=(8, 8))

    fig, ax = plt.subplots()
    cax = plt.pcolor(mat, cmap=plt.cm.Blues)

    mpl.rc('figure', figsize=figsize)

    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(mat.shape[0])+0.5, minor=False)
    ax.set_yticks(np.arange(mat.shape[1])+0.5, minor=False)

    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    ax.set_xticklabels(classes, fontsize=14);
    ax.set_yticklabels(classes);
    
    plt.xticks(rotation=70)
    
    ax.yaxis.set_label_position("right")
    ax.set_ylabel('true')
    ax.set_xlabel('predicted')
    
    ax.set_aspect(1)
    
    fig.colorbar(cax, label='fraction classified')
    cax.set_clim(vmin=0,vmax=1)
    
