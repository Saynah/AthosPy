from __future__ import division

import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import correlate
import matplotlib.pyplot as plt
import fileops as fop

# better to just apply this function to the columns


def fft_df(df):

    fs = 41.7
    len_sig = len(df)
    fft_out = []
    for col in df.columns:
        signal = df[col]

        fft = abs(np.fft.rfft(signal))
        fft_out.append(fft)

        freq = np.fft.rfftfreq(len_sig,
                               d=1. / fs)

    fft_out = np.array(fft_out).T

    # 2 frequencies w/ the greatest power
    fft_sum = fft_out.sum(axis=1)
    ix = np.argsort(fft_sum)
    f2 = freq[ix[-3:-1]]

    df_out = pd.DataFrame(fft_out, columns=df.columns)

    return df_out, freq, f2


def meanpeaks_df(df, frac):
    # removing outliers
    df = df[(np.abs(stats.zscore(df)) < 3).all(axis=1)]
    return df[df > frac * df.max()].mean().values


def phase_df(df, isplot=False):
    x1 = df.values
    x2 = df.values
    nsamp, ncols = x1.shape
    end = int(nsamp * 0.95)

    xcorr = correlate(x1, x2)
    xcorr = xcorr[0:end, 0:ncols]

    if isplot:
        fig, ax = plt.subplots()
        plt.plot(xcorr)

    dt = np.arange(1 - nsamp, nsamp)
    return -dt[xcorr.argmax(axis=0)]


def calc_features(data_dict, keys, standardize=False):
    print 'Deprecated. Use top_fcns.get_features()'
    freq = []
    peaks = []
    phase = []
    for key in keys:
        df = data_dict[key]

        _, _, fc = fft_df(df)
        freq.append(fc[::-1])

        peaks.append(meanpeaks_df(df, 0.5))

        phase.append(phase_df(df))

    peak_cols = df.columns.values.tolist()
    phase_cols = ['p_%s' % s for s in peak_cols]
    columns = peak_cols + ['f1', 'f2'] + phase_cols

    arr = np.concatenate((peaks, freq, phase), axis=1)
    feat = pd.DataFrame(arr, index=keys, columns=columns)

    if standardize:
        feat = (feat - feat.mean()) / feat.std()

    return feat


def quality(csv_path):
    '''Calculate basic quality metrics for csv file.
    * number of rows - to find files that are too short or long enough to sample multiple times
    * max value across all channels (below 15,000) - magnitude of the signal
    * median value across all channels - find files with signals that are too low
    * number of spikes to 65535 - files where sensor was freaking out
    * max fraction of zero values across channels - possibly dead sensors?
    * max fraction of consecutive non-zero values - files with temporal binning issues
    '''
    df = fop.load_emg(csv_path)
    len_df = len(df)

    quality = {
        "Length": len_df,
        "Max": df[df < 15000].unstack().max(),
        "Median": df.unstack().median(),
        "N_spikes": (df > 65000).sum().sum(),
        "MaxFrac_zero": max((df == 0).sum().divide(len_df) * 100),
        # "MaxFrac_repeat": max(((df != 0) & (df.diff() == 0)).sum().divide(len_df) * 100)
        "MaxFrac_repeat": max(((df > 100) & (df.diff() == 0)).sum().divide(len_df) * 100)
    }
    return quality
