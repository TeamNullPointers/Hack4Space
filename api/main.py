from flask import Flask,request,jsonify,
from flask_restful import Resource, Api
import requests
import requests_cache
import os
import configparser

app = Flask(__name__)

requests_cache.install_cache('epa_cache', backend='sqlite', expire_after=180)

parser = configparser.ConfigParser()
parser.read("config.txt")

email = parser.get("config", "email")
apikey = parser.get("config", "apikey")
base = parser.get("config", "apiurl")

# ==============================#
#           CONSTANTS           #
# ==============================#


# URLS
PARAM_ENDPOINT_URL = f"https://aqs.epa.gov/data/api/list/parametersByClass?email={email}&key={apikey}"
COUNTY_ANNUAL_SUMMARY_URL = f"https://aqs.epa.gov/data/api/sampleData/byCounty?email={email}&key={apikey}&param={param}&bdate={bdate}&edate={edate}&state=06&county={county}"

# CODES

STATE = '06'

# COUNTIES
# 	Humboldt County: 023
# 	Los Angeles: 037
# 	San Francisco: 075
# 	San Diego: 073
# 	Sacramento: 067

COUNTY_LIST = ['023','037','075','073','067']
# Parameters
# {
# "code": "11101",
# "value_represented": "Suspended particulate (TSP)"
# },
# {
#       "code": "11114",
#       "value_represented": "Windblown particulate"
#     },
# { "code": "11203",
# "value_represented": "Light scatter"
# },
# {
# "code": "11204",
# "value_represented": "Smoke"
# },
# {
#       "code": "42101",
#       "value_represented": "Carbon monoxide"
#     },
# {
#     "code": "25101",
#     "value_represented": "Dustfall Combustible (SP)"
# },
#
# {
#     "code": "31101",
#     "value_represented": "Respirable part"
# },
# {
#     "code": "42401",
#     "value_represented": "Sulfur dioxide"
# },
# {
#     "code": "65305",
#     "value_represented": "Radioactivity rainfall"
# },
# {
#     "code": "68110",
#     "value_represented": "Relative Humidity"
# },
# {
#     "code": "66101",
#     "value_represented": "Cloud cover"
# },

PARAM_LIST = ["11101", "11114","11203",
              "11204", "42101", "25101",
              "31101", "42401", "65305",
              "68110", "66101"]


# ============================== #
#           ROUTES               #
# ============================== #


@app.route('/', methods=['GET'])
def home():
    return 'The API is up and running'


@app.route('/param_codes', methods=['GET'])
def list_params(filter_by=None):

    if filter_by:
        url = PARAM_ENDPOINT_URL + f"&pc={filter_by}"
    else:
        url = PARAM_ENDPOINT_URL + "&pc=ALL"

    r = requests.get(url)

    return r.text




@app.route('/annual/<int:county>')
def show_annual_summary_by_county(county):


    response = requests.get()