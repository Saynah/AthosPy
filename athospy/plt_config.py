import pandas as pd
import matplotlib.pyplot as plt

def mpl_plt():
	import matplotlib as mpl

	plt.style.use('ggplot')
	
    # mpl.rc('figure', figsize=[16, 9])
	mpl.rc('figure', figsize=[16, 4])
	mpl.rc('xtick', labelsize=12) 
	mpl.rc('ytick', labelsize=12)
	mpl.rc('font', size=12)

	return mpl, plt

def line_df(df, title='', x=None):
    df_emgR = df.loc[:, ['RGM','RBF','RVM','RVL']]
    df_emgL = df.loc[:, ['LGM','LBF','LVM','LVL']]
    
    fig, ax = plt.subplots(2, 1, sharex=True)
    df_emgR.plot(ax=ax[0], x=x).legend(loc='center left', bbox_to_anchor=(1, 0.5))
    df_emgL.plot(ax=ax[1], x=x).legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax[0].set_ylabel('Right EMG')
    ax[1].set_ylabel('Left EMG')
    
    plt.suptitle(title)
    
    return fig, ax