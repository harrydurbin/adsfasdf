
## CREATION INFO:
Harry Durbin
Enveritas Coding Test
Junior Data Engineer
May 12, 2017

## DESCRIPTION:
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

## INSTRUCTIONS:
1) make sure required modules are installed:
    --> 'pip install -r requirements.txt'
2) copy this file into your local python packages folder (Python 2).
    --> if path unknown: 'python -m site --user-site' 
3) review/edit set variables.
4) see test.py for example for how to use this module to create new csv and dataframe.
