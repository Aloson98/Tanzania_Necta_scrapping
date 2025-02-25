import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mongoengine import connect
import sys
import json

sys.path.append('..')
from models import *

#connect to the database
connect('necta_database_2', host='localhost', port=27017)

necta_result = pd.read_pickle("necta_results_pickle")
print(necta_result.head(10))