#Version 10/5/23
#python -m pytest test_curve_parse.py -v -s
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import sys, os
import pandas as pd
import numpy as np
import pytest
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.dirname(current_dir) +  os.sep + 'libs' 
if not libs_dir in sys.path: sys.path.append(libs_dir)
from curve_parse import TensileParsingRun
from curve_parse import ParseAnalysisFile

IsPrint = False

@pytest.fixture()
def parse_defn():
    defn = {}
    defn['run_id'] = ('_AnalysisName', 1, 0, 1) #Flag, col, row offset, col offset
    defn['analysis_id'] = ('_AnalysisName', 1, 0, 1)

    defn['params_start'] = ('BeginSample', 1, 1) #Flag, col, row offset
    defn['params_end'] = ('BeginData', 1, -1)

    defn['params_col_names'] = 1 #Column with param names
    defn['params_col_offset'] = 1 #params_col_names to param vals offset

    defn['raw_start'] = ('BeginData', 1, 3) #Flag, col, row offset
    defn['raw_end'] = ('EndData', 1, -1) #Flag, col, row offset
    defn['raw_var_names'] = (1, -2) #colStart, rowOffset from raw_start row
    return defn

@pytest.fixture()
def parse_run(parse_defn):
    return TensileParsingRun(parse_defn, current_dir + os.sep)

@pytest.fixture()
def parse_file(parse_run):
    parse_run.file = 'Run101620-1_Material X_val.csv'
    return ParseAnalysisFile(parse_run)

"""
=========================================================================
TensileParsingRun Class
=========================================================================
"""
def test_read_files_procedure(parse_run):
    """
    Read all analysis files in specified folder and append data to 
    df_raw and df_params
    JDL 10/6/23
    """
    parse_run.read_files_procedure()

    assert parse_run.df_params.shape == (4, 8)
    assert parse_run.df_raw.shape == (19, 6)

def test_write_parsed_data(parse_run):
    """
    Read all analysis files in specified folder and append data to 
    df_raw and df_params
    JDL 10/6/23
    """
    parse_run.read_files_procedure()
    parse_run.write_parsed_data()

    print('\n\n')
    print(parse_run.df_params)
    print('\n\n')
    print(parse_run.df_raw)
    print('\n\n')

"""
=========================================================================
ParseAnalysisFile Class
=========================================================================
"""
def test_ParseAnalysisFile_InstanceClass(parse_file):
    assert isinstance(parse_file, ParseAnalysisFile)
    assert isinstance(parse_file.run.df_params, pd.DataFrame)
    assert isinstance(parse_file.run.df_raw, pd.DataFrame)
    assert parse_file.run.file == 'Run101620-1_Material X_val.csv'

def test_ParseAnalysisFile_parse_file_raw_data(parse_file):
    """
    Procedure to parse raw data from file and append to df_raw
    JDL 10/5/23
    """
    pass

def test_ParseAnalysisFile_parse_file_params_data(parse_file):
    """
    Procedure to parse params data from file and append to df_params
    JDL 10/5/23
    """
    pass

def test_ParseAnalysisFile_open_file(parse_file):
    """
    Open the analysis file to be parsed
    JDL 10/5/23
    """
    parse_file.open_file()
    assert isinstance(parse_file.df_file, pd.DataFrame)
    assert parse_file.df_file.shape == (42, 3)

def test_ParseAnalysisFile_read_run_id(parse_file):
    """
    Read the RunID from the analysis file
    JDL 10/5/23
    """
    parse_file.open_file()
    parse_file.read_run_id()

    sExpected = ' "Run101620-1_Material X_Analysis 94623.mss"'
    assert parse_file.run_id == sExpected

def test_ParseAnalysisFile_string_cleanup(parse_file):
    """
    Remove leading and trailing spaces and double quotes from string
    JDL 10/5/23
    """
    s = ' "Run101620-1_Material X_Analysis 94623.mss"'
    s_clean = parse_file.id_string_cleanup(s)

    sExpected = 'Run101620-1_Material X_Analysis 94623.mss'
    assert s_clean == sExpected

def test_ParseAnalysisFile_parse_run_id_string(parse_file):
    """
    Extract the RunID string from the raw cell value
    JDL 10/5/23
    """
    parse_file.open_file()
    parse_file.read_run_id()
    parse_file.parse_run_id_string()
    sExpected = 'Run101620-1'
    assert parse_file.run_id == sExpected

def test_ParseAnalysisFile_read_analysis_id(parse_file):
    """
    Read the AnalysisID from the analysis file
    JDL 10/5/23
    """
    parse_file.open_file()
    parse_file.read_analysis_id()

    sExpected = ' "Run101620-1_Material X_Analysis 94623.mss"'
    assert parse_file.analysis_id == sExpected

def test_ParseAnalysisFile_parse_analysis_id_string(parse_file):
    """
    Extract the AnalysisID string from the raw cell value
    JDL 10/5/23
    """
    parse_file.open_file()
    parse_file.read_analysis_id()
    parse_file.parse_analysis_id_string()
    sExpected = 'Analysis 94623'
    assert parse_file.analysis_id == sExpected

def test_ParseAnalysisFile_set_param_idx_lists(parse_file):
    """
    Populate lists of parameter block start and end indices within 
    df_file
    JDL 10/5/23
    """
    parse_file.open_file()
    parse_file.read_run_id()
    parse_file.set_param_idx_lists()
    assert parse_file.lst_idx_param_start == [10, 26]
    assert parse_file.lst_idx_param_end == [14, 30]

def test_ParseAnalysisFile_set_raw_idx_lists(parse_file):
    """
    Populate lists of raw data block start and end indices within 
    df_file
    JDL 10/6/23
    """
    parse_file.open_file()
    parse_file.set_raw_idx_lists()
    assert parse_file.lst_idx_raw_start == [18, 34]
    assert parse_file.lst_idx_raw_end == [22, 38]

def test_ParseAnalysisFile_read_raw_var_names(parse_file):
    """
    Read the raw data variable names from the first sample in
    df_file
    JDL 10/6/23
    """
    parse_file.open_file()
    parse_file.set_raw_idx_lists()
    parse_file.read_raw_var_names()
    assert parse_file.lst_varnames == ['_Load', 'SlackExt']

def test_ParseAnalysisFile_read_params(parse_file):
    """
    Iterate over file's samples and append param data to df_params
    JDL 10/6/23
    """
    parse_file.open_and_read_ids()
    parse_file.set_param_idx_lists()
    parse_file.read_params()

    cols_expected = ['RunID', 'AnalysisID', 'SampleID',\
                     'AverageLoad','AvgNPeaks','PeakLoad','PeelEnd','PeelStart']
    row_0 = [0.91, 2.23, 2.58, 402, 38]
    row_1 = [0.97, 2.48, 2.53, 402, 38]

    assert parse_file.run.df_params.shape == (2, 8)    
    assert parse_file.run.df_params.columns.tolist() == cols_expected

    assert (parse_file.run.df_params['RunID'] == 'Run101620-1').all()
    assert (parse_file.run.df_params['AnalysisID'] == 'Analysis 94623').all()
    assert parse_file.run.df_params.loc[0, 'SampleID'] == 1
    assert parse_file.run.df_params.loc[1, 'SampleID'] == 2

    assert parse_file.run.df_params.iloc[0, 3:].tolist() == row_0
    assert parse_file.run.df_params.iloc[1, 3:].tolist() == row_1

def test_ParseAnalysisFile_append_param_block(parse_file):
    """
    Append an individual sample's data to df_params
    JDL 10/6/23
    """
    parse_file.open_and_read_ids()

    parse_file.set_param_idx_lists()
    idx_col_names, idx_col_vals = 0, 1
    idx_start = parse_file.lst_idx_param_start[0]
    idx_end = parse_file.lst_idx_param_end[0]
    sample_id = 1
    parse_file.append_param_block(sample_id, idx_col_names, \
                                  idx_col_vals, idx_start, idx_end)

    cols_expected = ['RunID', 'AnalysisID', 'SampleID',\
                     'AverageLoad','AvgNPeaks','PeakLoad','PeelEnd','PeelStart']
    vals_expected = ['Run101620-1', 'Analysis 94623', 1, 0.91, 2.23, 2.58, 402, 38]
    assert parse_file.run.df_params.columns.tolist() == cols_expected
    assert parse_file.run.df_params.loc[0].tolist() == vals_expected

    assert (parse_file.run.df_params['RunID'] == 'Run101620-1').all()
    assert (parse_file.run.df_params['AnalysisID'] == 'Analysis 94623').all()
    assert (parse_file.run.df_params['SampleID'] == 1).all()


def test_ParseAnalysisFile_read_raw_data(parse_file):
    """
    Iterate over file's samples and append raw data to df_raw
    JDL 10/6/23
    """
    #Open the file and read RunID and AnalysisID
    parse_file.open_and_read_ids()

    #Populate idx lists that locate raw data for samples
    parse_file.set_raw_idx_lists()

    #Read the raw data variable names based on the first sample
    parse_file.read_raw_var_names()

    #Read the raw data for all samples
    parse_file.read_raw_data()

    assert parse_file.run.df_raw.shape == (10, 6)
    assert (parse_file.run.df_raw['RunID'] == 'Run101620-1').all()
    assert (parse_file.run.df_raw['AnalysisID'] == 'Analysis 94623').all()
    assert (parse_file.run.df_raw.loc[0:4,'SampleID'] == 1).all()
    assert (parse_file.run.df_raw.loc[5:9,'SampleID'] == 2).all()
    assert parse_file.run.df_raw['idx'].tolist() == [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
    col_Load = [0, 0.08, 0.8, 0.4, 0.2, 0, 0.01, 0.05, 0.5, 0.4]
    col_Extension = [0, 0.124, 0.189, 0.264, 0.352, 0.001, 0.091, 0.149, 0.218, 0.298]
    assert parse_file.run.df_raw['_Load'].tolist() == col_Load
    assert parse_file.run.df_raw['SlackExt'].tolist() == col_Extension


def test_ParseAnalysisFile_append_raw_block(parse_file):
    """
    Append an individual sample's raw data to df_raw
    JDL 10/6/23
    """
    #Open the file and read RunID and AnalysisID
    parse_file.open_and_read_ids()

    #Populate idx lists that locate raw data for samples
    parse_file.set_raw_idx_lists()

    #Read the raw data variable names based on the first sample
    parse_file.read_raw_var_names()

    idx_col_start, idx_col_end = 0, 1
    idx_start = parse_file.lst_idx_raw_start[0]
    idx_end = parse_file.lst_idx_raw_end[0]
    parse_file.append_raw_block(1, idx_col_start, idx_col_end, idx_start, idx_end)

    cols_expected = ['RunID','AnalysisID','SampleID','idx','_Load','SlackExt']
    assert parse_file.run.df_raw.columns.tolist() == cols_expected

    assert (parse_file.run.df_raw['RunID'] == 'Run101620-1').all()
    assert (parse_file.run.df_raw['AnalysisID'] == 'Analysis 94623').all()
    assert (parse_file.run.df_raw['SampleID'] == 1).all()

    col_Load = [0, 0.08, 0.8, 0.4, 0.2]
    col_Extension = [0, 0.124, 0.189, 0.264, 0.352]
    assert parse_file.run.df_raw['_Load'].tolist() == col_Load
    assert parse_file.run.df_raw['SlackExt'].tolist() == col_Extension


"""
=========================================================================
Utility functions for Print()
=========================================================================
"""

def PrintDF(df, text=''):
    print('\n', text, '\n')
    print(df)
    print('\n\n')

def PrintVars(vars, text):
    print('\n\n')
    if isinstance(vars, list):
        for v, s in zip(vars, text):
            print(f"{s}: {v}")
    else:
        print(f"{text}: {vars}")
    print('\n\n')


