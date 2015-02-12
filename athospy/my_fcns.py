import os
import re
import pandas as pd
import fnmatch
import difflib
import shutil


def label_folders(basepath, write_dst):
    '''Return dataframe containing labels parsed from sub-folders directly under basepath.
    Write a record of what was done to disk.
    '''
    folder_labels = []
    paths = []
    for fname in os.listdir(basepath):
        path = os.path.join(basepath, fname)
        if os.path.isdir(path) and fname[0] != '.':
            paths.append(path)
            labels, names = parse_folder_name(fname)
            folder_labels.append(labels)

    df = _to_dataframe(folder_labels, names)
    df['Path'] = paths
    df['Person_id'] = _name_to_id(df.First_Last)
    return _select_parsed(df, write_dst)


def label_all_csvfiles(basepath, folders, write_dst):
    '''Return dataframe for all csv files under basepath, with a column for folder ids
    Write a record of what was done to disk.
    '''
    # create table for all csv-files
    subdir__ix = zip(folders.Path, folders.index)
    df_list = [label_csvfiles(subdir, ix) for subdir, ix in subdir__ix]
    # concatenate data frames for all subdirectoriees
    files = pd.concat(df_list, ignore_index=True)
    return _select_parsed(files, write_dst)


def label_csvfiles(basepath, id):
    '''Return dataframe containing labels parsed from all csv files under basepath (recursively).
    Also append an id to index the top-level folder from which the csv files came
    '''
    file_labels = []
    paths = []
    for root, dirnames, fnames in os.walk(basepath):
        for fn in fnmatch.filter(fnames, '*.csv'):
            paths.append(os.path.join(root, fn))
            labels, names = parse_csv_name(fn)
            file_labels.append(labels)

    df = _to_dataframe(file_labels, names)
    df['Path'] = paths
    df['Folder_id'] = [id] * len(df)       # add index to parent folder
    return df


def rename_csvfiles(write_dst, df_files):
    '''rename csv files by file index
    '''
    shutil.rmtree(write_dst)
    os.mkdir(write_dst)

    ix__path = zip(df_files.index, df_files.Path)
    for ix, src in ix__path:
        fn_new = str(ix) + '.csv'
        dst = os.path.join(write_dst, fn_new)
        shutil.copy(src, dst)


def get_best_match(item, possible):
    '''Return the best matching string in the possible list.
    Otherwise return the original'''
    cutoff = 0.5
    n_match = 1
    match = difflib.get_close_matches(item, possible, n_match, cutoff)
    if match:
        return match[0]  # upack
    return None


# Move to file_ops.py ?
###############################################

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


# Helper functions
###################################################

def _to_dataframe(labels, names):
    if len(labels) == 0:
        return []
    else:
        return pd.DataFrame(labels, columns=names)


def _select_parsed(df, write_dst):
    '''Save record of all items in DataFrame.
    Return only items that were successfully parsed.
    '''
    df.to_csv(write_dst)
    parsed = df[df.iloc[:, 1].notnull()]
    print 'Parsed %d of %d items. See record at "%s"' % (
        len(parsed), len(df), write_dst)
    return parsed


def _name_to_id(S_name):
    '''replace names in series with numberical identifiers
    '''
    name_unq = S_name.unique()
    left = pd.DataFrame({'name':S_name})
    right = pd.DataFrame({'name': name_unq,
                          'id': range(len(name_unq))})
    return pd.merge(left,right)['id']