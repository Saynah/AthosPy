import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import correlate

import matplotlib.pyplot as plt

# better to just apply this function to the columns
def fft_df(df):

    fs = 41.7
    len_sig = len(df)
    fft_out = []
    for col in df.columns:
        signal = df[col]

        fft = abs( np.fft.rfft(signal) )
        fft_out.append(fft)
        
        freq = np.fft.rfftfreq(len_sig,
            d=1./fs)

    fft_out = np.array(fft_out).T

    # 2 frequencies w/ the greatest power
    fft_sum = fft_out.sum(axis=1)
    ix = np.argsort(fft_sum)
    f2 = freq[ix[-3:-1]]

    df_out = pd.DataFrame(fft_out, columns=df.columns)

    return df_out, freq, f2


def meanpeaks_df(df, frac):
    #removing outliers
    df = df[(np.abs(stats.zscore(df)) < 3).all(axis=1)]
    return df[df > frac*df.max()].mean().values


def phase_df(df, isplot=False):
    x1 = df.values
    x2 = df.values
    nsamp, ncols = x1.shape
    end = int(nsamp*0.95)

    xcorr = correlate(x1, x2)
    xcorr = xcorr[0:end, 0:ncols]

    if isplot:
        fig, ax = plt.subplots()
        plt.plot(xcorr)

    dt = np.arange(1-nsamp, nsamp)
    return -dt[xcorr.argmax(axis=0)]


def calc_features(df_dict, fnames):

    freq = []
    peaks = []
    phase = []
    for fn in fnames:
        df = df_dict[fn]

        _, _, fc = fft_df(df)
        freq.append(fc[::-1])

        peaks.append( meanpeaks_df(df, 0.5) )

        phase.append( phase_df(df) )

    peak_cols = df.columns.values.tolist()
    phase_cols = ['p_%s' % s for s in peak_cols]
    columns = peak_cols + ['f1', 'f2'] + phase_cols

    arr = np.concatenate((peaks, freq, phase), axis=1)
    df_out = pd.DataFrame(arr, index=fnames, 
        columns=columns)

    return df_out