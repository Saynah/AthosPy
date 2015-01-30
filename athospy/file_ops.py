import os
import pandas as pd

def load_emg_df(file_path):
    file_path = os.path.join(os.getcwd(), file_path)
    _, ext = os.path.splitext(file_path)
    if ext:
        assert ext == '.csv', "extension must be .csv, not %s" % ext

    df = pd.read_csv(file_path, header=0)
    df = df.loc[:,['LGM', 'LBF', 'LVL', 'LVM', 'RGM', 'RBF', 'RVL', 'RVM']]
    return df


def csv_summary(file_path):
    df = load_emg_df(file_path) # load only EMG data
    
    len_df = len(df)
    
    summary = {
        "Length" : len_df,
        "Median" : df.unstack().median(),
        "Max" : df[df<15000].unstack().max(),
        "MaxFrac_zero" : max((df==0).sum().divide(len_df) * 100),
        "MaxFrac_repeat" : max(((df!=0) & (df.diff()==0)).sum().divide(len_df) * 100)
    }
    return summary
