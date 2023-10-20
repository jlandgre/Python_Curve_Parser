#Version 10/5/23
import pandas as pd
import numpy as np
import regex as re
import os
#2345678901234567890123456789012345678901234567890123456789012345678901234567890
"""
=========================================================================
TensileParsingRun Class
=========================================================================
"""
class TensileParsingRun:
    def __init__(self, parse_defn, path_folder):
        """
        Initializes a ParsingRun object
        JDL 10/5/23

        Args:
        parse_defn [Dictionary] description of how to parse
        path_folder [String] directory path of folder containing raw data files
        """

        #User inputs
        self.defn = parse_defn 
        self.path_folder = path_folder

        #Current file while looping
        self.file = ''

        #Output DataFrames
        self.df_raw = pd.DataFrame()
        self.df_params = pd.DataFrame()

    def read_files_procedure(self):
        """
        Read all analysis files in specified folder and append data to 
        df_raw and df_params
        JDL 10/6/23
        """
        for filename in os.listdir(self.path_folder):

            #Skip non-csv files
            if not filename.endswith('.csv'): continue

            #Set filename attribute and instance ParseAnalysisFile
            self.file = filename
            parse_file = ParseAnalysisFile(self)
            parse_file.parse_individual_file()
    
    def write_parsed_data(self):
        """
        Write parsed data DataFrames to output file
        JDL 10/6/23
        """
        params_filepath = os.path.join(self.path_folder, 'df_params.xlsx')
        raw_filepath = os.path.join(self.path_folder, 'df_raw.xlsx')
        
        # Write df_params to Excel file
        with pd.ExcelWriter(params_filepath) as writer:
            self.df_params.to_excel(writer, index=False)
        
        # Write df_raw to Excel file
        with pd.ExcelWriter(raw_filepath) as writer:
            self.df_raw.to_excel(writer, index=False)
    
class ParseAnalysisFile:
    def __init__(self, run):
        """
        Initializes a ParseAnalysisFile object to parse a single file
        JDL 10/5/23

        Args:
        run [ParsingRun] reference to parent ParsingRun object (for
                         access to defn, df_params and df_raw)
        """

        #User inputs
        self.run = run

        #Internal attributes
        self.df_file = None
        self.run_id = ''
        self.analysis_id = ''
        self.lst_idx_param_start = []
        self.lst_idx_param_end = []
        self.lst_idx_raw_start = []
        self.lst_idx_raw_end = []
        self.lst_varnames = []
        self.run = run

    """
    =========================================================================
    Overall and sub-procedures for parsing a single file
    =========================================================================
    """
    def parse_individual_file(self):
        """
        Overall procedure to parse a single file
        JDL 10/6/23
        """
        self.open_and_read_ids()
        self.parse_file_params_data()
        self.parse_file_raw_data()

    def open_and_read_ids(self):
        """
        Sub-procedure to open the analysis file and read RunID and 
        AnalysisID metadata strings
        JDL 10/6/23
        """
        self.open_file()
        self.read_run_id()
        self.parse_run_id_string()
        self.read_analysis_id()
        self.parse_analysis_id_string()

    def parse_file_params_data(self):
        """
        Sub-procedure to parse the params data from the analysis file
        JDL 10/5/23
        """
        #Populate idx lists that locate params data for samples
        self.set_param_idx_lists()

        #Read the raw data for all samples
        self.read_params()

    def parse_file_raw_data(self):
        """
        Sub-procedure to parse the raw data from the analysis file
        JDL 10/6/23
        """
        #Populate idx lists that locate raw data for samples
        self.set_raw_idx_lists()

        #Read the raw data variable names based on the first sample
        self.read_raw_var_names()

        #Read the raw data for all samples
        self.read_raw_data()

    def open_file(self):
        """
        Open the analysis file to be parsed
        JDL 10/5/23
        """
        pathfile = self.run.path_folder + self.run.file
        self.df_file = pd.read_csv(pathfile, header=None)

    def read_run_id(self):
        """
        Read the RunID from the analysis file
        JDL 10/5/23
        """
        flag = self.run.defn['run_id'][0]
        idx_col_flag = self.run.defn['run_id'][1] - 1
        idx_col_val = idx_col_flag + self.run.defn['run_id'][3]
        
        fil = self.df_file[idx_col_flag] == flag
        self.run_id = self.df_file.loc[fil, idx_col_val].values[0]

    def parse_run_id_string(self):
        """
        Extract the RunID string from the raw cell value
        JDL 10/5/23
        """
        #Clean up the string by removing leading/trailing spaces and quotes
        self.run_id = self.id_string_cleanup(self.run_id)

        #set run_id to first part of string (before first underscore)
        lst = self.run_id.split('_')
        self.run_id = lst[0]

    def id_string_cleanup(self, id_string):
        """
        Strip leading/trailing spaces and quotes from an ID string
        JDL 10/5/23
        """
        # Define regular expression patterns
        leading_space_pattern = r'^\s+'
        trailing_space_pattern = r'\s+$'
        quote_pattern = r'^"|"$'
        
        # Use regular expression to strip leading/trailing spaces and quotes
        id_string = re.sub(leading_space_pattern, '', id_string)
        id_string = re.sub(trailing_space_pattern, '', id_string)
        id_string = re.sub(quote_pattern, '', id_string)
        return id_string
    
    def read_analysis_id(self):
        """
        Read the AnalysisID from the analysis file
        JDL 10/5/23
        """
        flag = self.run.defn['analysis_id'][0]
        idx_col_flag = self.run.defn['analysis_id'][1] - 1
        idx_col_val = idx_col_flag + self.run.defn['analysis_id'][3]
        
        fil = self.df_file[idx_col_flag] == flag
        self.analysis_id = self.df_file.loc[fil, idx_col_val].values[0]

    def parse_analysis_id_string(self):
        """
        Extract the AnalysisID string from the raw cell value
        JDL 10/5/23
        """
        #Clean up the string by removing leading/trailing spaces and quotes
        self.analysis_id = self.id_string_cleanup(self.analysis_id)

        #set run_id to first part of string (before first underscore)
        lst = self.analysis_id.split('_')
        self.analysis_id = lst[2].split('.')[0]

    def set_param_idx_lists(self):
        """
        Populate lists of parameter block start and end indices within 
        df_file
        JDL 10/5/23
        """
        self.lst_idx_param_start = self.set_param_idx_list('params_start')
        self.lst_idx_param_end = self.set_param_idx_list('params_end')

    def set_param_idx_list(self, defn_key):
        """
        Get a list of start and end indices of rows with the specified
        flag string and apply offset
        (helper function to set_param_idx_lists and set_raw_idx_lists)
        JDL 10/5/23
        """
        #Get the flag string, column index and row offset from defn dict tuple
        tup = self.run.defn[defn_key]
        flag, idx_col_flag, row_offset = tup[0], tup[1] - 1, tup[2]

        #Get list of indices of rows with the flag string and apply offset
        fil = self.df_file[idx_col_flag] == flag
        lst = self.df_file[fil].index.tolist()
        lst = [x + row_offset for x in lst]
        return lst

    def set_raw_idx_lists(self):
        """
        Populate lists of raw data block start and end indices within 
        df_file
        JDL 10/6/23
        """
        self.lst_idx_raw_start = self.set_param_idx_list('raw_start')
        self.lst_idx_raw_end = self.set_param_idx_list('raw_end')

    def read_raw_var_names(self):
        """
        Read the raw data variable names from the first sample in
        df_file
        JDL 10/6/23
        """
        row_offset = self.run.defn['raw_var_names'][1]
        idx_names = self.lst_idx_raw_start[0] + row_offset
                
        for val in self.df_file.loc[idx_names]:

            #Stop reading when NaN (blank cell) is encountered
            if (type(val) == float):
                if np.isnan(val): break
            
            #Strip leading and trailing spaces from string
            elif (type(val) == str):
                val = val.strip()
            self.lst_varnames.append(val)

    def read_params(self):
        """
        Iterate over file's samples and append param data to df_params
        JDL 10/6/23
        """
        #Set column indices for param names and values from defn dict tuple
        idx_col_names = self.run.defn['params_col_names'] - 1
        idx_col_vals = idx_col_names + self.run.defn['params_col_offset']

        #Iterate over samples and read params
        indices = zip(self.lst_idx_param_start, self.lst_idx_param_end)
        for i, (idx_start, idx_end) in enumerate(indices):
            sample_id = i + 1
            self.append_param_block(sample_id, idx_col_names, idx_col_vals, idx_start, idx_end)
    
    def append_param_block(self, sample_id, idx_col_names, idx_col_vals, idx_start, idx_end):
        """
        Append an individual sample's data to df_params
        JDL 10/6/23
        """
        #Read param names
        names = self.df_file.loc[idx_start:idx_end, idx_col_names].tolist()

        #Read values and convert to numeric if possible
        vals = self.df_file.loc[idx_start:idx_end, idx_col_vals].tolist()
        vals = convert_to_numeric(vals)

        #Append params row to df_params
        df_temp = pd.DataFrame([vals], columns=names)
        
        #Populate ID columns
        df_temp['SampleID'] = sample_id
        df_temp['RunID'] = self.run_id
        df_temp['AnalysisID'] = self.analysis_id

        #Reorder the columns
        cols = ['RunID', 'AnalysisID', 'SampleID'] + names
        df_temp = df_temp[cols]

        #Concat sample's params data block to df_raw
        self.run.df_params = pd.concat([self.run.df_params, df_temp], ignore_index=True)

    def read_raw_data(self):
        """
        Iterate over file's samples and append raw data to df_raw
        JDL 10/6/23
        """
        #Set column indices for param names and values from defn dict tuple
        idx_col_start = self.run.defn['raw_var_names'][0] - 1
        idx_col_end = idx_col_start + len(self.lst_varnames) - 1

        #Iterate over samples and read params
        indices = zip(self.lst_idx_raw_start, self.lst_idx_raw_end)
        for i, (idx_start, idx_end) in enumerate(indices):
            sample_id = i + 1
            self.append_raw_block(sample_id, idx_col_start, idx_col_end, idx_start, idx_end)

    def append_raw_block(self, sample_id, idx_col_start, idx_col_end, idx_start, idx_end):
        """
        Append an individual sample's raw data to df_raw
        JDL 10/6/23
        """
        #Read values and convert to numeric if possible
        df_temp = self.df_file.loc[idx_start:idx_end, idx_col_start:idx_col_end]
        df_temp = df_temp.apply(convert_to_numeric)
        df_temp.columns = self.lst_varnames

        #Populate ID columns
        df_temp['SampleID'] = sample_id
        df_temp['RunID'] = self.run_id
        df_temp['AnalysisID'] = self.analysis_id

        #Reset the index
        df_temp.reset_index(drop=True, inplace=True)
        df_temp.index.name = 'idx'
        df_temp.reset_index(drop=False, inplace=True)

        #Reorder the columns
        cols = ['RunID', 'AnalysisID', 'SampleID', 'idx'] + self.lst_varnames
        df_temp = df_temp[cols]

        #Concat sample's raw data block to df_raw
        self.run.df_raw = pd.concat([self.run.df_raw, df_temp], ignore_index=True)

"""
=========================================================================
Utility functions - move to util.py
=========================================================================
"""
def convert_to_numeric(lst):
    new_lst = []
    
    # Loop through input list and convert each value to numeric if possible
    for value in lst:
        try:
            new_value = float(value)
            new_lst.append(new_value)
        except ValueError:
            new_lst.append(value)

    # Return new list with converted values
    return new_lst
