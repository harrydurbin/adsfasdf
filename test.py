import surveymanipulator

# assume a this relative path and filename, but can change
sm = surveymanipulator.SurveyManipulator('data/data_sample.csv')

# dataframe of manipulated data
df_new = sm.df
