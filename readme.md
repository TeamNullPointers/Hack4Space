# Team Null Pointers
# Rebeca Carrillo, Crystal Contreras, Josh Crosby

For IBM Hack4Space hackathon

Air Data - flask application that pulls air quality data from the Environmental Protection Agency's AQS API and saves it locally.


# API Quick Start 
 1. clone repository and cd into it
 
in your terminal, do
```
source api/py3/bin/activate
export FLASK_APP=api/gunicorn_myapp.py
python3 gunicorn_myapp.py
python3 main.py

```
navigate to `http://localhost:5000/` in your browser

# Routes (all GET methods at this point)
* / 	index
* /test
* /annual
* /sample


## TODO: 
	- add swagger documentation
	- templates



Our problem space: *Air quality degradation over time".*
Things to make more specific:
    - what time frame?
    - what defines "good" and "worse" air quality?
    - where are our datasets coming from?



DATA FROM: EPA AQS API

 ## Case study: California 1999-2020

  #### right now we're focusing on california for reasons. (list reasons here). We can expand later if we need to
  	- Los Angeles
  	- San Francisco
  	- San Diego
  	- Sacramento
  	- Humboldt Country (Eureka, Arcata)



--- 
## About parameters:
```
The parameters in AQS are identified by codes that are specific to the AQS system itself. That is, we do not use Chemical Abstract Service or any other standard naming conventions. AQS parameter codes are 5-digit numeric codes. AQS also has parameter names that are domain specific and may or may not correlate to other taxonomies.

AQS also defines parameter classifications. These are groups of parameters that have been collected for ease of extraction from the database. Examples of parameter classifications are Criteria (parameters for which National Ambient Air Quality standards have been defined), Meteorological, Core HAPs (Core Hazardous Air Pollutants), etc. A parameter may belong to any number of classifications. Classifications are not defined by regulation or policy and may change at any time.
```


## PARAMETERS BEING PULLED:

```
Code,value_represented
"42101","Carbon monoxide"
"42401","Sulfur dioxide"
"42602","Nitrogen dioxide (NO2)"
"44201","Ozone"
"81102","PM10 Total 0-10um STP"
"88101","PM2.5 - Local Conditions"
"88502","Acceptable PM2.5 AQI & Speciation Mass"
"12403","Sulfate (TSP) STP"
"43102","Total NMOC (non-methane organic compound)"
"62101","Outdoor Temperature"
"63301","Solar radiation"
"64101","Barometric pressure"
"65102","Rain/melt precipitation"
"81102","PM10 Total 0-10um STP"
"85101","PM10 - LC"
"86101","PM10-2.5 - Local Conditions"
"86502","Acceptable PM10-2.5 - Local Conditions"
```

From the site documentation:
```
3.1.2. The significance of 1999
1999 marked the beginning of required PM2.5 (particulate matter of 2.5 microns in aerodynamic diameter or less) and PM2.5 speciated monitoring (62 FR 38652). PM10 and TSP data is available in prior years, but 1999 is the first year with national FRM and non-FRM PM2.5 monitoring. This is reflected in the large jump in the number of monitors in 1999.
```

---