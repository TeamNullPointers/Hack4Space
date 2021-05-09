from flask import Flask
from flask_restful import Resource, Api
import requests
import requests_cache
import os
import configparser
from pathlib import Path
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)


requests_cache.install_cache('epa_cache', backend='sqlite', expire_after=180000)

parser = configparser.ConfigParser()
parser.read("config.txt")

email = parser.get("config", "email")
apikey = parser.get("config", "apikey")
apiurl = parser.get("config", "apiurl")

TEST_URL = "https://aqs.epa.gov/data/api/list/classes?email=carrilloreb9@gmail.com&key=indigocat58"

# ==============================#
#           CONSTANTS           #
# ==============================#


# URLS
#PARAM_ENDPOINT_URL = f"https://aqs.epa.gov/data/api/list/parametersByClass?email={email}&key={apikey}&pc=ALL"
#COUNTY_ANNUAL_SUMMARY_URL = f"https://aqs.epa.gov/data/api/sampleData/byCounty?email={email}&key={apikey}&param={param}&bdate={bdate}&edate={edate}&state=06"

# CODES

STATE = '06'

# COUNTIES
# 	Humboldt County: 023
# 	Los Angeles: 037
# 	San Francisco: 075
# 	San Diego: 073
# 	Sacramento: 067

COUNTIES = {"HUMBOLDT": "023",
            "LA": "037",
            "SF": "075",
            "SD": "073",
            "SACRAMENTO": "067"}



# Parameters
# ------------
# Code, Value Represented
# "42101","Carbon monoxide"
# "42401","Sulfur dioxide"
# "42602","Nitrogen dioxide (NO2)"
# "44201","Ozone"
# "81102","PM10 Total 0-10um STP"
# "88101","PM2.5 - Local Conditions"
# "88502","Acceptable PM2.5 AQI & Speciation Mass"
# "12403","Sulfate (TSP) STP"
# "43102","Total NMOC (non-methane organic compound)"
# "62101","Outdoor Temperature"
# "63301","Solar radiation"
# "64101","Barometric pressure"
# "65102","Rain/melt precipitation"
# "81102","PM10 Total 0-10um STP"
# "85101","PM10 - LC"
# "86101","PM10-2.5 - Local Conditions"
# "86502","Acceptable PM10-2.5 - Local Conditions"


PARAM_LIST = ["42101", "42401","42602","44201", "62101", "65102", "811202","86101", "86502",
"88101","88502"]

DATE_RANGE = (19990101, 20201231)

# ============================== #
#           ROUTES               #
# ============================== #

@app.route('/', methods=['GET'])
def home():

    return 'The API is up and running'

# Test api is working

@app.route('/test', methods=['GET'])
def test():

    r = requests.get(TEST_URL)
    return r.json()


# @app.route('/param_codes', methods=['GET'])
# def list_params(filter_by=None):
#
#     if filter_by:
#         url = PARAM_ENDPOINT_URL + f"&pc={filter_by}"
#     else:
#         url = PARAM_ENDPOINT_URL + "&pc=ALL"
#
#     r = requests.get(url)
#
#     return r.text


# ===================== #
# HELPER FUNCTIONS ==== #
# ===================== #
def generate_date_args(start_year=None, end_year=None):

    '''
    This just generates the correctly formatted date arg to pass.
    Years start on Jan 1
    :param start_year: YY (e.g. 2001 = 01)
    :param end_year: YY (max 21)
    :return: array of strings
    '''

    # We're actually only pulling to 2020 bc 2021 data isn't guaranteed yet

    if end_year:
        assert(end_year < 2021)
    else:
        end_year = 2021

    if start_year is None:
        start_year = 1999


    diff = range(start_year, end_year)
    all_years = list(diff)

    # EPA enforces limit of year inclusive
    start_year = "20{YY}0101"
    end_year="20{YY}1231"

    all_date_tuples = []
    for YY in all_years:
        date_args = (start_year.format(YY=YY), end_year.format(YY=YY))
        all_date_tuples.append(date_args)

    return all_date_tuples


def make_annual_urls(param):
    '''
    dirty little hack for generating a list of urls for the thread
    pool executor to hit up
    :param param:
    :return: list of strings
    '''

    # Consider throwing in date parameterization
    date_args = generate_date_args()
    base_url="https://aqs.epa.gov/data/api/annualData/byCounty?email=carrilloreb9@gmail.com&key=indigocat58"
    param_snippet=f"&param={param}"

    annual_urls = []

    for c in COUNTIES.values():
        county_filter_snippet = f"&county={c}"
        for a, b in date_args:
            date_snippet=f"&bdate={a}&edate={b}1&state=06"
            full_url= base_url + param_snippet + date_snippet + county_filter_snippet
            annual_urls.append(full_url)

    return make_annual_urls()


def get_annual_summary_CO2(url):

    '''
    get one year C02 annual summary for one county
    :param url:
    :return: json
    '''

    req = urllib.request.urlopen(url)
    fullpath = Path(url)
    fname = fullpath.name
    ext = fullpath.suffix

    if not ext:
        raise RuntimeError("URL does not contain an extension")

    with open(fname, "wb") as handle:
        while True:
            chunk = req.read(1024)
            if not chunk:
                break
            handle.write(chunk)

    msg = f"Finished downloading {fname}"
    return msg


# ==================== #
# BIGBOY ROUTES - fetch all (defined in readme)
# cache these please    #
# ==================== #

@timeit
@app.route('/annual/C02)')
def download_all_C02(carbon_urls=None):

    if carbon_urls is None:
        carbon_urls = make_annual_urls("42101")

    with ThreadPoolExecutor(max_workers=13) as executor:
            return executor.map(get_annual_summary_CO2, carbon_urls, timeout=60)



if __name__ == '__main__':
    app.run(app)
