from flask import Flask
import requests
import requests_cache
import configparser
import time
from pathlib import Path
import urllib.request
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# requests_cache.install_cache('epa_cache', backend='sqlite', expire_after=180)

# parser = configparser.ConfigParser()
# parser.read("config.txt")
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

def get_one_annual_summary(url):
    '''
    get one year C02 annual summary for one county
    :param url:
    :param year:
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

    msg = "Finished downloading {fname}".fname(fname=fname)
    return msg


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
        param = 42101

    base_url = "https://aqs.epa.gov/data/api/{report_type}" \
               "byCounty?email=carrilloreb9@gmail.com&key=indigocat58".format(report_type=report_type)
    param_snippet = "&param={param}".format(param=param)

    all_urls = []

    for c in COUNTIES.values():
        county_filter_snippet = "&county={c}".format(c=c)
        for a, b in date_args:
            date_snippet = "&bdate={a}&edate={b}&state=06".format(a=a, b=b)
            full_url = base_url + param_snippet + date_snippet + county_filter_snippet
            all_urls.append(full_url)

    return all_urls


# MULTI-THREADING LOGIC

session = None


def set_global_session():
    global session
    if not session:
        session = requests.Session()


def download_url(url):
    with session.get(url) as response:
        name = multiprocessing.current_process().name
        print(f"{name}:Read {len(response.content)} from {url}")


def download_all_urls(urls):
    with multiprocessing.Pool(initializer=set_global_session) as pool:
        pool.map(download_url, urls)


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
        urls = make_urls(param, "annual")

    download_all_urls(urls)


if __name__ == '__main__':
    urls = make_urls()
    start_time = time.time()
    download_all_annual(urls)
    duration = time.time() - start_time
    print(f"Called {len(urls)} api endpoints in {duration} seconds")
    app.run(host='0.0.0.0')


