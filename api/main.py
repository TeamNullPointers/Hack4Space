from flask import Flask
import requests_cache
import configparser
from pathlib import Path
import requests
import uuid
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# requests_cache.install_cache('epa_cache', backend='sqlite', expire_after=180)

parser = configparser.ConfigParser()
parser.read("config.txt")
#
# email = parser.get("Default", "Email")
# apikey = parser.get("Default", "Apikey")
# apiurl = parser.get("Default", "Apiurl")

# I know it's heinous to have these in the script, troubleshooting
email="carrilloreb9@gmail.com"
apikey="indigocat58"

TEST_URL = "https://aqs.epa.gov/data/api/list/classes?email=carrilloreb9@gmail.com&key=indigocat58"


# ==============================#
#           CONSTANTS           #
# ==============================#

# CODES

STATE = '06'

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


PARAM_LIST = ["42101", "42401","42602","44201", "62101",
              "65102", "811202","86101", "86502",
              "88101","88502"]

DATE_RANGE = (19990101, 20201231)


# ======================== #
# ===HELPER FUNCTIONS ==== #
# ======================== #


# date-range related
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
        assert (end_year < 2021)
    else:
        end_year = 2021

    if start_year is None:
        start_year = 1999

    diff = range(start_year, end_year)
    all_years = list(diff)

    # EPA enforces limit of year inclusive
    start_year = "{YY}0101"
    end_year = "{YY}1231"

    all_date_tuples = []
    for YY in all_years:
        date_args = (start_year.format(YY=YY), end_year.format(YY=YY))
        all_date_tuples.append(date_args)

    return all_date_tuples


def make_urls(param=None, report_type=None):
    """
    dirty little hack for generating a list of urls for the thread
    pool executor to hit up
    :param param:
    :param report_type: str describing which report endpoint to hit, e.g Sample Data
    :return: list of strings
    """
    date_args = generate_date_args()

    if report_type is None:
        report_type = "annualData"

    # Defaulting to carbon emissions because that's the most common
    if param is None:
        param = "42101"

    base_url = "https://aqs.epa.gov/data/api/{report_type}" \
               "/byState?email=carrilloreb9@gmail.com&key=indigocat58".format(report_type=report_type)
    param_snippet = "&param={param}".format(param=param)

    all_urls = []

    for a, b in date_args:
        date_snippet = "&bdate={a}&edate={b}&state=06".format(a=a, b=b)
        full_url = base_url + param_snippet + date_snippet
        all_urls.append(full_url)

    return all_urls


def download_file(url, file_name):
    try:
        data = requests.get(url)
        with open(file_name, mode='wb') as localfile:
            localfile.write(data.content)

    except:

        return data


def runner(urls):
    threads = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        for url in urls:
            file_name = uuid.uuid1()
            threads.append(executor.submit(download_file, url, file_name))
        for task in as_completed(threads):
            print(task.result())


def pull_all(urls):
    print("attempting to pull files")
    runner(urls)


# ============================== #
#           ROUTES               #
# ============================== #


@app.route('/', methods=['GET'])
def home():

    return "<h1 style='color:blue'>We got ourselves an API!</h1>"

# Test api is working


@app.route('/test', methods=['GET'])
def test():

    r = requests.get(TEST_URL)
    return r.json()


@app.route('/annual', methods=['GET'])
def download_all_annual(param, urls=None):

    if urls is None:
        urls = make_urls(param, "annualData")

    pull_all(urls)


@app.route('/sample', methods=['GET'])
def download_all_sample(param, urls=None):

    if urls is None:
        urls = make_urls(param, "sampleData")

    pull_all(urls)


if __name__ == '__main__':
    app.run(host='0.0.0.0')


