def mpl_plt():
	import matplotlib as mpl
	import matplotlib.pyplot as plt

	plt.style.use('ggplot')
	
	mpl.rc('figure', figsize=[16, 9])
	mpl.rc('xtick', labelsize=12) 
	mpl.rc('ytick', labelsize=12)
	mpl.rc('font', size=12)

	return mpl, plt