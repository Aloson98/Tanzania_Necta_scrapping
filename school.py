from bs4 import BeautifulSoup
import requests
import re
from models import StudentSubjectResults, School
from mongoengine import connect

#initiate Database
connect("necta_results", host="localhost", port=27017)

# Retrieve student results
mohammed_shein = School.objects.get(school_index="S6278")
results = StudentSubjectResults.objects(school=mohammed_shein)




for result in results:
    print(f"School: {result.school.school_name}, Data Index: {result.data_index}")
    print("Subjects and Grades:")

    # Convert the document to a dictionary to inspect all fields
    data_dict = result.to_mongo().to_dict()
    
    # Iterate through the dictionary to print subject and grade fields
    for key, value in data_dict.items():
        # Skip metadata fields
        if key not in ['_id', 'school', 'data_index'] and value:
            # Replace underscores for better readability
            subject = key.replace("_", " ").title()
            print(f"{subject}: {value}")
    print("-" * 50)