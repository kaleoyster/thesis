from pymongo import MongoClient
import pandas as pd
import csv



def connectToNBI(collection_name,connection_string):
    """
    
       description: connects to NBI mongodb instance and returns a collection 
       input type: collection_name - [string], connection_string - [string]
       return type: collection - [string]
       
    """

    Client = MongoClient(connection_string)
    db = Client.nbi
    collection = db[collection_name]
    return collection


def getSurveyRecords(states, years, fields, db, connection_string):
    """  
       
        description: returns survey records of provided states, years from the collection.
        input type:  states - [list], year - [list], db - [string], connection_string - [string]
        return type: survey_records - [dataframe] 
 
    """
    collection = connectToNBI(db,connection_string)
    masterdec = []
    for yr in years:
        for state in states:
            pipeline = [{"$match":{"$and":[{"year":yr},{"stateCode":state}]}},
                        {"$project":fields}]
            dec = collection.aggregate(pipeline)
            for i in list(dec):
                masterdec.append(i)
    survey_records = pd.DataFrame(masterdec)
    return survey_records


def filterSurveyData(survey_records):
    """ 
    decription: filters missing and 'NA' values from condition rating: deck, substructure, and superstructure. And, discrards structure type = 19 and type of wearing surface = '6'
    
    return type:
    :dataframe: filtred survey records, length of survey records before filteration and after filteration 
    :list: before_filtr : before_filter - length of the survey records 
    :list: after_filtr  : after_filter - length of the survey records
    
    """   
    
    before_filtr = len(survey_records) ## Length of survey record before filtering

    
    ## Filtring Criteria for  deck, substructure and superstructure
    survey_records = survey_records.loc[~survey_records['deck'].isin(['N','NA'])]
    survey_records = survey_records.loc[~survey_records['substructure'].isin(['N','NA'])]
    survey_records = survey_records.loc[~survey_records['superstructure'].isin(['N','NA'])]
    
    ## discards survey records of Structure type - 19  and Type of Wearing Surface - 6
    survey_records = survey_records.loc[~survey_records['Structure Type'].isin([19])]
    survey_records = survey_records.loc[~survey_records['Type of Wearing Surface'].isin(['6'])]
  

    after_filtr = len(survey_records) ## Length of survey record before filtering
    
    return survey_records, before_filtr, after_filtr


def same_elements(elements):
    """
     description: Checks if all the elements of the list are equal
     
     return type:
     :Boolean: returns True if the all the elements of the list are equal 
     
    """
    if not elements:
        return True
    return [elements[0]*len(elements) == elements]


def createTimeseries(survey_records):
    """Create time series data from the loose records"""
    survey_timeseries = [[key]+[col for col in value] for key, value in {k:[g['Age'].tolist(),g['ADT Type'].tolist(),g['superstructure'].tolist(),g['Avg. Daily Precipitation (mm)'].tolist(), g['stateCode'].tolist(), g['averageDailyTraffic'].tolist(),g["owner"].tolist()] for k, g in survey_records.groupby('structureNumber')}.items()]
    # for key, value in {k:[g['Age'].tolist(),g['ADT Type'].tolist(),g['Category'],g['superstructure'].tolist()] for k, g in survey_records.groupby('structureNumber')}.items():
    return survey_timeseries
    

## 2nd in sequence
def createProfile(data):
    """ this function creates a profile to split records ## Renamed backward difference"""
    counter = 0
    profile = [True]
    while counter+1 < len(data):
        if data[counter] < data[counter+1]:
            profile.append(True)
        else:
            profile.append(False)
            profile.append(True)
        counter = counter + 1
    return profile

###
def createBackwardProfile(data):
    """ this function creates a profile to split records ## Renamed backward difference"""
    counter = 0
    profile = [True]
    while counter+1 < len(data):
        if data[counter+1] - data[counter] < 26 :
            profile.append(True)
        else:
            profile.append(False)
            profile.append(True)
        counter = counter + 1
    return profile



def utilitySplitBridgeRecords(data, profile):
    """ The ultility function to split records by intervention
     Takes a 1xn list returns 2xn list"""
    """Modify here"""
    counter = 0
    main_list = []
    temp_list = []
    for bval in profile:
        if bval == True:
            temp_list.append(data[counter])
            counter  = counter + 1 
        else:
            main_list.append(temp_list)
            temp_list = []        
    main_list.append(temp_list)
    return main_list


def splitSurveyRecords(survey_timeseries):
    """
    description: return split records of bridge to account intervention like Rebuilt, Reconstruction, and Rehabilitation
    input - type:
        :list: survey_timeseries
    output - type:
        :list: temp
    """
    temp = []
    for i in survey_timeseries:
        profile = createProfile((i[1]))
        #print("Create Profile:",i[1])
        temp_list = []
        temp_list.append(i[0])
        for row in i[1:]:
            split_records = utilitySplitBridgeRecords(row, profile)
            temp_list.append(split_records)
        temp.append(temp_list)
        
    return temp


## combine function:
def combinedStructureNumberWithRecords(structure_numbers_split_records, s):
    """
    Combine function of split structure numbers with the rest of the records
    
    description:
                
    input-type:
        :list: structure_number
        :list: s

    return-type:
    
        :list: combined_records
    """
    combined_records = []
    for h,j in zip(structure_numbers_split_records, s):
        combined_records.append([h]+j[1:])
    return combined_records

def splitStructureNumbers(s):
    """
    decription:
        Split the the structure numbers of the depending s?
        
    input - type:
        :list:
    return - type:
        :list: 
  
    """
    structure_numbers_split_records = []
    for i in s:
        len_K = len(i[1])
        structureNumber = i[0]
        structureNumbers = []
        for k in range(len_K):
            stNumber=(str(structureNumber)+'_'+str(k+1))
            structureNumbers.append(stNumber)
        structure_numbers_split_records.append(structureNumbers)
    return structure_numbers_split_records


def createIndividualRecords(survey_records):
    """ 
    description: create split records from individual records
    input - type:
         :list: survey_records
         
    output - type:
         :list: split_by_intervention_survey_ records
    """
    split_by_intervention_survey_records = []
    length_i = len(survey_records[0])
    for i in survey_records:
        length = len(i[1])
        for j in range(length):
            split_temp1 = []
            for k in range(0,length_i):
                split_temp1.append(i[k][j])
            split_by_intervention_survey_records.append(split_temp1)
    return split_by_intervention_survey_records










#collection = connectToNBI("bridges","mongodb://research:superSMART1%3A%3A@ist177a-mongo.ist.unomaha.edu/admin")
