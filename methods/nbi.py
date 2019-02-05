from pymongo import MongoClient
import pandas as pd
import csv



def connectToNBI(collection_name,string):
    """
       Connects to NBI mongodb instance and returns a collection 
    """

    Client = MongoClient(string)
    db = Client.nbi
    collection = db[collection_name]
    return collection


def getSurveyRecords(states, years, fields, collection_name):
    """ returns survey records of provided states, years from the collection.
        returns a dataframe
    """
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


#collection = connectToNBI("bridges","mongodb://research:superSMART1%3A%3A@ist177a-mongo.ist.unomaha.edu/admin")
