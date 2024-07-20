import os
import datetime
import json


# function to get a new result folder
def getNewResultDirectory(root_output_dir : str = "", main_name="BackTest Result"):
    current_datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    new_dir = root_output_dir + "/" + main_name + " - " + current_datetime_str

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    return new_dir


def is_jsonable(x):
        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False

def get_serialized_parameters_from_list(object_list):
    list_data = []
    for strategy in object_list:
        obj_data = {}
        properties = vars(strategy)
        for prop in properties:
            if (is_jsonable(properties[prop])):
                obj_data[prop] = properties[prop]
        
        list_data.append(obj_data)
            
    return list_data
    

def save_dictionary_as_json(dictionary, file_name):
    with open(file_name, "w") as outfile: 
        json.dump(dictionary, outfile)