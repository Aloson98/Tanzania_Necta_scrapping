from bs4 import BeautifulSoup
import requests
import re
from models import School
from mongoengine import connect
import json

#initiate Database
connect("necta_results", host="localhost", port=27017)

# Retrieve student results
mohammed_shein = School.objects.get(school_index="S6278")
jsonData = json.loads(mohammed_shein.to_json())


print(jsonData)