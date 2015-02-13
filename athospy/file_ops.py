import os               # directory walking
import pandas as pd     # data table/series manipulation 
import re               # regular expressions
import difflib          # soft string matching
import json
import fnmatch          # 

# DEPRECATED. Use fileops

EXER_LIST = 'config/exercise-list_short.txt'
PERS_LIST = 'config/person-list'

# exer_map = _load_json(EXER_LIST)
# pers_map = _load_json(PERS_LIST)

f = open(EXER_LIST)
exercise_set = set()
for line in f:
    exercise_set.add( line.rstrip() )
f.close()


# helper functions

# TODO get person and exercise mappings from json file. 
#   need to think about this more
# # load config files for person and exercise matching
# def _load_json(json_file):
#     with open(EXER_LIST) as json_file:
#         return json.load(json_file)




def load_emg_df(csv_path):
    '''Load EMG data from the specified CSV file as a pandas data frame
    '''
    _, ext = os.path.splitext(csv_path)
    assert ext == '.csv', 'extension must be .csv, not "%s"' % ext
    
    df = pd.read_csv(csv_path, header=0)
    df = df.loc[:,['LGM', 'LBF', 'LVL', 'LVM', 'RGM', 'RBF', 'RVL', 'RVM']]
    # reorder columns for left/right: glut, ham, lat/med: quad

    return df


def parse_csv_name(csv_name):
    """Extract labels from csv file name. Empty "" if parsing error"""
    # could also extract the person name (first item)
    # however, the naming convention (first_last or last_first) is not consistent

#     pers_exer = re.findall(r"([a-zA-Z ]+)(?:_| _)([a-zA-Z]+).{0,7}\.csv", fn)
    exer = re.findall(r"[a-zA-Z ]+(?:_| _)([a-zA-Z]+).{0,7}\.csv",
        csv_name)
    if exer:
        return exer[0]
    else:
        return "" 


def parse_person(sub_dir):
    first_last = re.findall(r"([a-zA-Z]*)_(?:[a-zA-Z]*_)?([a-zA-Z]*)_Calib",
        sdir)
    if first_last: return first_last[0][0] + ' ' + first_last[0][1]
    else: return []


def map_exercise(ex_name):
    """Match exercise name to one in the list and map it properly"""

    match = difflib.get_close_matches(ex_name, possible, 1, cutoff)
    if match: return match[0] # upack
    else: return []


def label_csvs_in_dir(data_dir):
    """Crawl data directory and label csv files.
    Write file names and labels to a data frame.
    Also write ignored files"""

    # could also check for READMEs at each level

    for root, dirs, fnames in os.path.walk(data_dir):
        for fname in fnmatch.filter(fnames, '*.csv'):
            labels = parse_csv_name(fnames)
            if labels:
                e = get_best_match(exer, exercise_set, cutoff)
                if e:
                    personExerDict[p][e].append(csvPath)
                    count += 1
                else:
                    ignoredFiles.append(csvPath)
#                         print 'ignored file: ', csvPath
                    count_ign += 1
            else:
                ignoredFiles.append(csvPath)
#                     print 'ignored file: ', csvPath
                count_ign += 1


def csv_summary(file_path):
    df = load_emg_df(file_path) # load only EMG data
    
    len_df = len(df)
    
    summary = {
        "Length" : len_df,
        "Max" : df[df<15000].unstack().max(),
        "Median" : df.unstack().median(),
        "n_spikes" : (df>65000).sum().sum(),
        "MaxFrac_zero" : max((df==0).sum().divide(len_df) * 100),
        "MaxFrac_repeat" : max(((df!=0) & (df.diff()==0)).sum().divide(len_df) * 100)
    }
    return summary