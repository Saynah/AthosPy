import os
import pandas as pd
import fnmatch
import difflib
import shutil

# athospy packages
import visualization as viz
import calcs
import fileops as fop


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
            labels, names = fop.parse_folder_name(fname)
            folder_labels.append(labels)

    df = _to_dataframe(folder_labels, names)
    df['Path'] = paths
    df['Person_id'] = _name_to_id(df.First_Last)
    return _select_parsed(df, write_dst)


def label_csvfiles_by_folder(basepath, df_folders, write_dst):
    '''Return dataframe for all csv files under basepath, with a column for folder ids
    Write a record of what was done to disk.
    '''
    # create table for all csv-files
    subdir__ix = zip(df_folders.Path, df_folders.index)
    df_list = [label_csvfiles(subdir, ix) for subdir, ix in subdir__ix]
    # concatenate data frames for all subdirectoriees
    files = pd.concat(df_list, ignore_index=True)
    return _select_parsed(files, write_dst)


def label_csvfiles(basepath, id=-1):
    '''Return dataframe containing labels parsed from all csv files under basepath (recursively).
    Also append an id to index the top-level folder from which the csv files came
    '''
    file_labels = []
    paths = []
    for root, dirnames, fnames in os.walk(basepath):
        for fn in fnmatch.filter(fnames, '*.csv'):
            paths.append(os.path.join(root, fn))
            labels, names = fop.parse_csv_name(fn)
            file_labels.append(labels)

    df = _to_dataframe(file_labels, names)
    df['Path'] = paths
    df['Folder_id'] = [id] * len(df)       # add index to parent folder
    return df


def join_and_anonymize(df_files, df_folders, write_dst):
    '''Join file and folder tables and remove person names
    '''
    df_joined = pd.merge(df_folders[['Person_id', 'Trial']],
                         df_files[['Exercise', 'Legside', 'Resistance', 'Path', 'Folder_id']],
                         left_index=True, right_on='Folder_id')

    df_joined = _rename_csvfiles(df_joined, write_dst)   # copy and overwrite path

    df_joined.drop('Folder_id', axis=1, inplace=True)  # don't need joining idx anymore
    return df_joined


def get_best_match(item, possible):
    '''Return the best matching string in the possible list.
    Otherwise return the original'''
    cutoff = 0.5
    n_match = 1
    match = difflib.get_close_matches(item, possible, n_match, cutoff)
    if match:
        return match[0]  # upack
    return None


def load_and_plot(df_files, write_dir='', plot_on=True):
    '''Loads and plots the csv files in df_files. Optionally saves pdf.
    Labels are used as the title'''
    for i in df_files.index:
        row = df_files.ix[i]
        df = fop.load_emg(row.Path)
        title = str(row.tolist())
        fig, _ = viz.plot_emg(df, title=title)

        if write_dir:
            try: os.mkdir(write_dir)
            except: pass
            fig.savefig(os.path.join(write_dir, str(i) + '.pdf'))
            if not plot_on:
                viz.plt.close()



def check_quality(df_files):
    '''Compile quality metrics into a dataframe and plot their distrubution
    '''
    d_summ = []
    for path in df_files.Path:
        d_summ.append(calcs.quality(path))

    files_qc = pd.DataFrame(d_summ, index=df_files.index)
    viz.plot_qc(files_qc)

    return files_qc


def exclude(df, files_qc, write_dst='../files_dirty.csv'):
    '''Remove files that don't match the quality criteria.
    '''
    len_old = len(df)

    short = files_qc.Length < 500
    repeats = files_qc.MaxFrac_repeat > 60
    zeros = files_qc.MaxFrac_zero > 30
    noisy = files_qc.Median > 100

    is_bad = short | repeats | zeros | noisy
    df_dirty = df[is_bad]
    df_dirty.to_csv(write_dst)

    df = df[~is_bad]
    print 'excluded %d files of %d' % (len_old - len(df), len_old)

    return df


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
    left = pd.DataFrame({'name': S_name})
    right = pd.DataFrame({'name': name_unq,
                          'id': range(len(name_unq))})
    return pd.merge(left, right)['id']


def _rename_csvfiles(df_files, write_dir):
    '''rename csv files by file index
    '''
    shutil.rmtree(write_dir)
    os.mkdir(write_dir)

    path_new = []
    ix__path = zip(df_files.index, df_files.Path)
    for ix, src in ix__path:
        dst = os.path.join(write_dir, str(ix) + '.csv')
        shutil.copy(src, dst)
        path_new.append(dst)

    print 'Copied %d files and renamed by file_id. See "%s"' % (
        len(df_files), write_dir)

    df_files.Path = path_new
    return df_files

