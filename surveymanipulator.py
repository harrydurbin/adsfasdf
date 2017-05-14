import pandas as pd # panda dataframes
from fuzzywuzzy import process # fuzzy string matching
import re # real expressions
import os
import numpy as np

class SurveyManipulator(object):

    ## fixed set variables
    DURATION_QUANTILE = 0.10 # the quartile of surveys that have short duration
    FUZZY_SCORE_CUT_OFF= 80 # percent of string matching required to correct spelling
    # this is the list of banned Pesticides:
    BANNED_PESTICIDES = ['endosulfan', 'gramaxon', 'paraquat', 'preglone',
                            'parathion', 'terbufos', 'thiodan', 'vidate']
    # list of the column names that contain a list of chemicals
    CHEM_COLUMNS = ['herbicides','fertilizers','insecticides',
                    'other_herbicides','other_fertilizers','other_insecticides']

    def __init__(self, path):
        self.path = path
        self.execute()

    def get_filepath(self):
        self.fpath, self.fn = os.path.split(self.path)
        print '=============================================================================='
        print 'Loading csv data...'
        return self.fpath , self.fn

    def load_data(self):
        df = pd.read_csv(self.fpath+'/'+self.fn)
        return df

    @staticmethod
    def get_unique_chemicals(chemical_list):
        # compile chemicals from 6 cols to single list
        compiled_list = []
        for chem in chemical_list:
            if chem != 'other':
                compiled_list.append(chem)
        return set(compiled_list)

    @staticmethod
    def split_handwritten_chemicals(chemical_list):
        # split chemical names apart bzsed on various deliminators
        re.findall(r"[\w']+", chemical_list)
        return chemical_list

    @staticmethod
    def flatten_list(l):
        flattened_list = list(set([item for sublist in l for item in sublist]))
        return flattened_list

    @staticmethod
    def correct_spelling(chemical_list):
        # fixes spelling errors of chemical names
        corrected_chemical_list = []
        for chem in chemical_list:
            corrected_chem, score = process.extractOne(chem, SurveyManipulator.BANNED_PESTICIDES)
            if score > SurveyManipulator.FUZZY_SCORE_CUT_OFF:
                corrected_chemical_list.append(corrected_chem)
            else:
                corrected_chemical_list.append(chem)
        return corrected_chemical_list

    @staticmethod
    def format_column(df,col):
        df[col] = df[col].astype(str)
        if str(col)[:6]=='other_':
            df[col] = df[col].apply(lambda x: re.findall(r"[\w']+", x))
            df[col] = df[col].apply(lambda x: SurveyManipulator.correct_spelling(x))
        else:
            df[col] = df[col].apply(lambda x: x.split())
        return df[col]

    @staticmethod
    def add_NaNs(df,col):
        df[col] = df[col].apply(lambda x: np.nan if x == ['nan'] else x)
        return df[col]

    @staticmethod
    def check_banned(chem_list):
        # check each chemical to see if it is banned
        compliance = ''
        if chem_list!={'nan'}:
            for chem in chem_list:
                if chem in SurveyManipulator.BANNED_PESTICIDES:
                    compliance = 'F'
                    return compliance
                else:
                    compliance = 'P'
        else:
            compliance = 'NA'
        return compliance

    def add_duration_column(self):
        # add new column for duration time
        self.df['ended_time'] = pd.to_datetime(self.df['ended_time'])
        self.df['started_time'] = pd.to_datetime(self.df['started_time'])
        self.df['durationminutes'] = (self.df['ended_time'] - self.df['started_time']).astype('timedelta64[m]')
        print 'Adding a column for survey duration...'
        return

    def add_short_duration_column(self):
        # add new column for short duration
        self.df['durationquantile']=""
        self.df.loc[self.df['durationminutes'] <= self.df['durationminutes'].quantile(self.DURATION_QUANTILE), 'durationquantile'] = 'True'
        self.df.loc[self.df['durationminutes'] > self.df['durationminutes'].quantile(self.DURATION_QUANTILE), 'durationquantile'] = 'False'
        print 'Adding a column to indicate if it was a short survey...'
        return

    def add_banned_pesticide_compliance_column(self):
        #  add column for 'no banned pesticides' criterion

        for colname in self.CHEM_COLUMNS:
            self.df[colname] = self.format_column(self.df, colname)

        self.df['chem_list'] = self.df[self.CHEM_COLUMNS].values.tolist()
        self.df['chem_list'] = self.df['chem_list'].apply(lambda x: self.flatten_list(x))
        self.df['chem_list'] = self.df['chem_list'].apply(lambda x: self.get_unique_chemicals(x))
        self.df['nobannedpesticides']=self.df['chem_list'].apply(lambda x: self.check_banned(x))
        self.df.drop('chem_list', axis = 1, inplace=True)

        for colname in self.CHEM_COLUMNS:
            self.add_NaNs(self.df,colname)

        print 'Adding a column to indicate if farmer complies with "No Banned Pesticides"...'
        return

    def create_new_csv(self):
        self.df.to_csv(self.fpath+'/'+self.fn.split('.csv')[0]+'_new.csv')
        print 'Writing a new csv file...'
        print '=============================================================================='
        return

    def execute(self):
        self.fpath, self.fn = self.get_filepath()
        self.df = self.load_data()
        self.add_duration_column()
        self.add_short_duration_column()
        self.add_banned_pesticide_compliance_column()
        self.create_new_csv()
        return
