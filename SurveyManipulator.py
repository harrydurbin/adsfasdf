'''
CREATION INFO:
Harry Durbin
Enveritas Coding Test
Junior Data Engineer
May 12, 2017

DESCRIPTION:
The purpose of this code is to feed this python module a filename that points to original CSV and print new CSV in the same path
as original CSV. The code manipulates data to provide basic information about each survey adding the following columns to the
raw csv:
+ Survey length [minutes]
+ Survey amount 10% of shortest surveys [true/false]
+ Farmer's performance on "No Banned Pesticides" criterion ["NA", "F", "P"]
    - Farmer uses no chemicals ["NA" for not applicable]
    - Farmer uses banned chemicals (herbicides, fertilizers, insecticides) ["F" for fail]
        --> banned chemicals are: ['endosulfan', 'gramaxon', 'paraquat', 'preglone', 'parathion', 'terbufos', 'thiodan', 'vidate']
        --> fuzzywuzzy is used to correct spelling of chemicals listed by hand in the 'other_' columns
    - Farmer uses chemicals but doesn't use banned chemicals ["P" for pass]

INSTRUCTIONS:
1) copy this SurveyManipulator.py files into your local python packages folder
    --> typ: 'python -m site --user-site' if path unknown
2) review/edit the fixed variables below if wanting to check alternative parameters
3) import this module into your python script with 'import SurveyManipulator'
4) to create new csv file and dataframe with additional features, for the argument, enter the path
    and file name of the csv:
    -->e.g. df_new = SurveyManipulator.survey_manipulator('PATH_TO_CSV_FILE/CSV_FILE_NAME.csv')

'''
import pandas as pd # panda dataframes
import math # math functions
from fuzzywuzzy import process # fuzzy string matchinb
import re # real expressions
import os

pd.set_option("display.max_columns", 30)

# set variables / lists
duration_quantile = 0.10 # the top percentage of surveys that have shorter duration than this quantile


fuzzy_score_cut_off = 80 # percent of string matching required to correct spelling


bannedpesticides = ['endosulfan', 'gramaxon', 'paraquat', 'preglone', # this is the list of banned Pesticides
                  'parathion', 'terbufos', 'thiodan', 'vidate']


chem_choices = ['endosulfan', 'gramaxon', 'paraquat', 'preglone', # this is the list of all possible chemicals, including banned
            'parathion', 'terbufos', 'thiodan', 'vidate']


class survey_manipulator(object):

    def __init__(self,path):
        self.path = path
        self.fpath , self.fn = self.getFilePath()
        self.df = self.loadData()
        self.df = self.addDurationColumn()
        self.df = self.addShortDurationColumn()
        self.df = self.addBannedPesticideComplianceColumn()
        self.createNewCSV()
        global duration_quantile
        global fuzzy_score_cut_off
        global bannedpesticides
        global chem_choices

    def getFilePath(self):
        self.fpath, self.fn = os.path.split(self.path)
        print self.fpath
        print self.fn
        return self.fpath , self.fn

    def loadData(self):
        # load raw survey data
        self.df = pd.read_csv(self.fpath+'/'+self.fn)
        print 'Loading csv data...'
        return self.df

    def getUniqueChemicals(self, chemical_list):
        compiled_list = []
        for chem in chemical_list:
            try:
                math.isnan(chem)
                continue
            except:
                if chem != 'other':
                    compiled_list.append(chem)
        if compiled_list == []: compiled_list == ['NaN']
        return list(set(compiled_list))

    def splitHandwrittenChemicals(self, chemical_list):
        split_chemical_list = []
        for chem in chemical_list:
            split_chemical_list.append(re.findall(r"[\w']+", chem))
        return split_chemical_list

    def flattenList(self, l):
        flattened_list = list(set([item for sublist in l for item in sublist]))
        return flattened_list

    def correctSpelling(self, chemical_list):
        corrected_chemical_list = []
        for chem in chemical_list:
            corrected_chem, score = process.extractOne(chem, chem_choices)
            if score > fuzzy_score_cut_off:
                corrected_chemical_list.append(corrected_chem)
            else:
                corrected_chemical_list.append(chem)
        return corrected_chemical_list

    def checkBanned(self, chem_list):
        nobannedpesticides=[]
        compliance = ''
        if chem_list != []:
            for chem in chem_list:
                if chem in bannedpesticides:
                    nobannedpesticides.append('F')
                    compliance = 'F'
                    break
                else:
                    nobannedpesticides.append('P')
                    compliance = 'P'
                    continue
        else:
            compliance = 'NA'
        return compliance

    def addDurationColumn(self):
        # add new column for duration time
        self.df['ended_time'] = pd.to_datetime(self.df['ended_time'])
        self.df['started_time'] = pd.to_datetime(self.df['started_time'])
        self.df['durationminutes'] = (self.df['ended_time'] - self.df['started_time']).astype('timedelta64[m]')
        print 'Adding a column for survey duration...'
        return self.df

    def addShortDurationColumn(self):
        # add new column for short duration
        self.df['durationquantile']=""
        self.df.loc[self.df['durationminutes'] <= self.df['durationminutes'].quantile(duration_quantile), 'durationquantile'] = 'True'
        self.df.loc[self.df['durationminutes'] > self.df['durationminutes'].quantile(duration_quantile), 'durationquantile'] = 'False'
        print 'Adding a column to indicate if it was a short survey...'
        return self.df

    def addBannedPesticideComplianceColumn(self):
        #  add column for 'no banned pesticides' criterion
        chem_columns = ['herbicides','fertilizers','other_insecticides','other_herbicides',
                        'other_fertilizers','other_insecticides']

        self.df['chem_list'] = self.df[chem_columns].values.tolist()
        self.df['chem_list1'] = self.df['chem_list'].apply(lambda x: self.getUniqueChemicals(x))
        self.df['chem_list2'] = self.df['chem_list1'].apply(lambda x: self.splitHandwrittenChemicals(x))
        self.df['chem_list3'] = self.df['chem_list2'].apply(lambda x: self.flattenList(x))
        self.df['chem_list4'] = self.df['chem_list3'].apply(lambda x: self.correctSpelling(x))
        self.df['nobannedpesticides']=self.df['chem_list4'].apply(lambda x: self.checkBanned(x))

        self.df.drop(['chem_list','chem_list1','chem_list2','chem_list3','chem_list4'],axis=1,inplace=True)
        self.df[['herbicides','fertilizers','insecticides','other_herbicides',
            'other_fertilizers','other_insecticides','nobannedpesticides']]
        print 'Adding a column to indicate if farmer complies with "No Banned Pesticides" criteria"...'
        return self.df

    def createNewCSV(self):
        self.df.to_csv(self.fpath+'/'+self.fn.split('.csv')[0]+'_new.csv')
        print 'Writing a new csv file...'
        return

if __name__ == "__main__":
    SurveyManipulator()
