from flask import Flask
import asyncio
from flask.ext.aiohttp import async
from flask_restful import Resource, Api
import requests
import requests_cache
import os
import configparser

app = Flask(__name__)
aio = AioHTTP(app)


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


# ==================== #
# BIGBOY ROUTES - fetch all (defined in readme)
# cache these please    #
# ==================== #

@app.route('/annual/C02', methods=['GET'])
@async
def get_annual_summaries_CO2():
    response = yield from aiohttp.request(
        'GET',

    )

    param = "42101"
    humboldt = COUNTIES["HUMBOLDT"]

    url=f"https://aqs.epa.gov/data/api/sampleData/byCounty?email={email}&key={apikey}&param={param}" \
        f"&bdate={bdate}&edate={edate}&state=06&county={humboldt}"




# =========++++
# HELPER FUNCTIONS ====

def get_url_county_x_param(county, param, date_arg):
    '''
    Get the url string uniue to a combo of county and date arg string
    :param county: county code
    :param date_arg: formatted str
    :return: full url string for api GET request
    '''

    base_url = ""

    url = base_url + date_arg + f"&state=06&county={county}"

    return url

def __generate_date_args(param, start_year=None, end_year=None):

    '''
    This just generates the correctly formatted date arg to pass.
    Years start on Jan 1
    :param start_year: YY (e.g. 2001 = 01)
    :param end_year: YY (max 21)
    :return: array of strings
    '''

    if end_year:
        assert(end_year < 2021)
    else:
        end_year = 2021

    if start_year is None:
        start_year = 2001


    diff = range(start_year, end_year)
    all_years = list(diff)

    date_formatting_pattern: f"'010120{YY}'"
    args = []
    for y in all_years:
        new_arg = date_formatting_pattern(YY=y)
        args.append(new_arg)


    full_args = []
    for a in args:
        add_to_arg = f"&param={param}&bdate={start_year}&edate={a}&state=06"
        full_arg = BASE + add_to_arg
        full_args.append(full_arg)

    return full_args


def pull_annual(all_requests_gen):
    '''

    :param all_requests_gen:
    :return: array of objects (JSON response data)
    '''

    all_request_responses = []
    for a in all_requests_gen:
        response_body = get_annual_summary(a)
        all_request_responses.append(response_body)

    return all_request_responses


def _generate_all_annual_requests_less_county(p_list = None,
                                     bdate = None,
                                     edate = None):

    '''

    :param p_list:
    :param bdate:
    :param edate:
    :return: list of strings
    '''
    if p_list:
        ps = p_list

    else:
        ps = PARAM_LIST

    if bdate:
        b = bdate

    else:
        b = "19990101"

    if edate:
        e = edate
    else:
        e = "20210101"


    # I am sincerely sorry for the heinous amount of for loops in this software but hey, hack, right?


    almost_full_urls = []
    for p in ps:
        url_slice = f"&param={p}&bdate={b}&edate={e}"
        full_url_less_county = BASE + url_slice
        almost_full_urls.append(full_url_less_county)

    return almost_full_urls


def _generate_all_annual_requests(a_list):

    request_endpoints = []
    for a in a_list:
        for c in COUNTY_LIST:
            url = a + f"&county={c}"
            request_endpoints.append(url)

    return request_endpoints





# WRAPPER TO GET ALL ANNUAL REPORTS - USE SPARINGLY

# @TODO: when I get back from break - implement async io logic stuff to do all annual gets at once(threaded)
# relies on client session apparently

@app.route('/do_annual')
def get_annual_summary(request_endpoints):

    response = requests.get(request_endpoints)

    return response.json()



# # Pull all annual reports from the counties in our county list
# # pass specific param
# @app.route('annual_all/<int:param code>')
# def pull_county_annuals(p):
#
#     responses = []
#     for c in COUNTY_LIST:
#         county=c
#         param=p
#         r = requests.get(COUNTY_ANNUAL_SUMMARY_URL+f"&county={county}")


if __name__ == '__main__':
    aio.run(app)
