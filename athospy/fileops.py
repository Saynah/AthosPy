import re
import os
import pandas as pd

def load_emg(csv_path):
    '''Load EMG data from the specified CSV file as a pandas data frame
    '''
    _, ext = os.path.splitext(csv_path)
    assert ext == '.csv', 'extension must be .csv, not "%s"' % ext
    
    df = pd.read_csv(csv_path, header=0)
    df = df.loc[:,['LGM', 'LBF', 'LVL', 'LVM', 'RGM', 'RBF', 'RVL', 'RVM']]
    # reorder columns for left/right: glut, ham, lat/med: quad

    return df


def parse_folder_name(folder_name):
    '''extract name of person and trial/fitness/push numbers from folder name'''
    # names = ['First', 'Last', 'Trial', 'Fitness', 'Push']
    # labels = re.findall(r"^([a-zA-Z]*)_(?:[a-zA-Z]*_)?([a-zA-Z]*)[_ ]Calib.*[_ ]Trial(\d*)[_ ]Fitness(\d*)[_ ]Push(\d*)$",
    #                     folder_name)
    names = ['First_Last', 'Trial', 'Fitness', 'Push']
    labels = re.findall(r"^([a-zA-Z]*_(?:[a-zA-Z]*_)?[a-zA-Z]*)[_ ]Calib.*[_ ]Trial(\d*)[_ ]Fitness(\d*)[_ ]Push(\d*)$",
                        folder_name)
    if labels:
        return list(labels[0]), names
    return [None] * len(names), names


def parse_csv_name(csv_name):
    '''extract person name, excercise name, leg side, number, and suffix labels'''
    names = ['LastFirst', 'Exercise', 'Legside', 'Resistance', 'Sufffix']

    # try requiring the tag for leg-side
    labels = re.findall(r"^([a-zA-Z ]+)(?:_| _)([A-Za-z]+)_?([LR])(\d*)(.{0,4})\.csv$",
                        csv_name)
    if labels:
        return list(labels[0]), names

    # try with optional tag for leg-side and permit a longer allowed suffix
    labels = re.findall(r"^([a-zA-Z ]+)(?:_| _)([A-Za-z]+)_?([LR])?(\d*)(.{0,8})\.csv$",
                        csv_name)
    if labels:
        return list(labels[0]), names
    return [None] * len(names), names


def sample_data(files, n_sec):
    '''Create dictionary of sampled data, with file ids as keys.
    '''
    # TODO: allow input of single series instead of dataframe?
    n_samp = int(41.7 * n_sec)

    data_dict = {}
    ix__path = zip(files.index, files.Path)
    for ix, csv_path in ix__path:
        df = load_emg(csv_path)

        i_mid = len(df) // 2
        i_start = i_mid - n_samp // 2
        i_end = i_mid + n_samp // 2

        data_dict[ix] = df.iloc[i_start:i_end]
    
    return data_dict
