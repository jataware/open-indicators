# News Article Search
This repository houses files to run a focused, user-defined search of on-line news articles. Created by Jataware, this research effort extracts open-source data to provide timely and relevant information to modelers and data scientists.

News data collection relies on the [Bing News Search API](https://azure.microsoft.com/en-us/services/cognitive-services/bing-news-search-api/). For testing purposes, we recommend establishing a trial account with this API. Your API settings should be set based on the instructions in the [Configuration section](#configuration) of this document.


**Disclaimer**: any datasets contained in this repository have not been vetted by human experts. They should be taken as representative of events that occurred on the ground, but should not be considered authoritative sources or ground truth.

## Contents
1. [Overview](#overview)
2. [Extraction options](#extraction-options)
3. [NLP](#nlp)
4. [Building Your Search](#building-your-search)
5. [WebApp Instructions](#webapp-instructions)
6. [Geography](#geography)
7. [Python Requirements](#python-requirements)
8. [Configuration](#configuration)
9. [Execution](#execution)

## Overview
News Article Search scours news-related websites searching for user-defined events (concepts) and associated terms of interest for that event (target variables). The program returns a `.json` tagged with user-defined data extractions from the articles' text. Extraction techniques include regular expression matching and natural language processing. Below is an overview:  

![Image of sentence](https://github.com/jataware/open-indicators/blob/master/news-article-search/images/diagram.png)
  
  - Concept Variable(s): The main topical event for which the user is searching. The user MUST define a primary concept and MAY add alternative concepts. For example, the primary concept could be "COVID" with alternates "COVID-19" and "SARS-COV-2".
  	
  - Target Variable(s): Within the scope of the concept, the program searches for the target variable(s) as the parameter(s) of interest. For example, continuing with the "COVID" concept, a user may be interested in "tests" and "ventilators" as primary target variables. Just like with the concept variable, the user MAY add alternates for each target variable; i.e. "tests" can be expanded to include "test kits" and "test-kits" as alternates. A minimum of one primary target variable is required.
	
- Query expander: The program generates query combinations that are expanded with a fixed concept, individually-grouped target variable sets, which are then appended to each geopolitical admin-level in the user-selected csv file. 

![Image of queries](https://github.com/jataware/open-indicators/blob/master/news-article-search/images/queries.png)
	
- Open News index: focused search of news websites with expanded queries. At a minumum the text, title, date, and url of the news article are returned.  Additional data provided depends on the user's search preferences.
	
- Information extraction: regular expression matching and natural language processing techniques are applied to the data returned from the news index.

### Extraction Options
Below illustrates the options available to the user while extracting data from news articles. For a given search either one or both methods can be utilized.

![Image of NLP-REGEX](https://github.com/jataware/open-indicators/blob/master/news-article-search/images/nllpregex.png)

  - REGEX: regular expresssion matching with two options; see `User Interface` for more detail. Extracts either frequency counts for a given target variable or quantitative data associated with the target.
  - NLP: natural langauge processing. See `NLP` for more detail.

- Data Delivery: query results returned to user using desired search techniques as a `.json` file for follow-on analysis.

### NLP
  - Leverages University of Arizona’s Odinson project. For detailed information on UofA's project see: [https://github.com/lum-ai/odinson](https://github.com/lum-ai/odinson)
  - User chooses verb-object pairings. Verbs and object words are [stemmed](https://en.wikipedia.org/wiki/Stemming): i.e. testing → test or mandated → mandate
  - Odinson returns sentences that includes the verb-object pairing. The sentences not only alert the user of an item of interest in the article, but also maintains the context of the search.
  - Below is an example of how our NLP extractor parses a sentence into various part of speech.  Notice that the NOUN (businesses) is a direct object (DOBJ) of the verb (reopen).  Using Odinson, sentence structures matching your verb-object pairings are extracted and returned.

<p align="center">
<img src="https://github.com/jataware/open-indicators/blob/master/news-article-search/images/sentenceCircle.png" alt="drawing" width="900"/>
</p>


### Building Your Search

To build the yaml file with all required search parameters, a webapp can be deployed locally or accessed remotely with credentials.

Local deployment:

  1. Clone the open-indicators repository to /your/local/folder.
  2. run `cd /your/local/folder/open-indicators/news-article-search/`
  3. run `pip install -r requirements.txt`
  4. run `python3 webapp/app.py`
  5. Open web browser, go to: `localhost:5000`
  6. Follow WebApp instructions below.
	
Remote connection:	

  1. Contact Jataware for credentials.
  2. Open web browser, go to: `https://news-search.worldmodelers.com/`
  3. Enter credentials.
  4. Follow WebApp instructions below.
		
### WebApp Instructions:

#### Start:

 <p align="center"><img src="https://github.com/jataware/open-indicators/blob/master/news-article-search/images/start.png" alt="drawing" width="700"/></p>

Click the `Build your search` button to start. There is a link back to this repository (GitHub Repo) for reference and at any time the build can be started anew by clicking `Refresh your search`


#### Filename and Concept Definition:

 <p align="center"><img src="https://github.com/jataware/open-indicators/blob/master/news-article-search/images/FILE.png" alt="drawing" width="400"/></p>
	
  -  Enter your desired filename; this will be the name of the file that is downloaded to your computer.
  
  -  Enter your desired concept(s). There must be at least one, but there is no max limit. Enter one term per row and press `enter` to add more concepts. Do NOT add a space after your term.
	
#### Exact Match (REGEX matching): Exact Search section allows you to add target variables that will be extracted via the regular expression techniques discussed above.

  <p align="center">
  <img src="https://github.com/jataware/open-indicators/blob/master/news-article-search/images/EXACT.png" alt="drawing" width="400"/>
  </p>	
	
  - Enter a descriptive column label that describes your target variables; this label will 'hold' the regular expression results and you will access this label for post-processing analysis.
  
  - `Count`: returns the count, or number of times, a target variable appears in an article. For example: target variable = 'masks'; text = "Mask Shortage: Governor requests 10,000 masks'; return = 2.  
	
  - `Quantity`: returns the quantitative characterization of the target variable. For example: target variable = 'masks'; text = "Mask Shortage: Governor requests 10,000 masks'; return = '10,000 masks'.
	
  - Title of Article Filter: Options include `True` or `False`. This functionality allows the user to choose whether or not to require the geography keyword to be in the title of the article.  As an example: for a geography csv with cities and states, the user can return news article data based on whether or not the city name is in the title of the news article. `True` only returns articles that include the city name in the title; `False` ignores this filter and returns all relevant news articles. 
	
  - `+ Exact Match`: Select this button to add more target variables. There is no max limit. Repeat the steps above.

#### Semantic Match (NLP): Semantic Search section allows you to add verb-object pairings that will be extracted via the NLP technique discussed above.

  <p align="center">
  <img src="https://github.com/jataware/open-indicators/blob/master/news-article-search/images/NLP.png" alt="drawing" width="400"/>
  </p>	
	
  - Enter a descriptive column label that describes your target variables; this label will 'hold' the regular expression results and you will access this label for post-processing analysis
	
  - Title of Article Filter: Options include `True` or `False`. This functionality allows the user to choose whether or not to require the geography keyword to be in the title of the article.  As an example: for a geography csv with cities and states, the user can return news article data based on whether or not the city name is in the title of the news article. `True` only returns articles that include the city name in the title; `False` ignores this filter and returns all relevant news articles.
  
  - `verb`: enter your action words / verbs that you are interested in; multiple verbs can be entered. Do not add a space after your verb. Selected verbs should be related to your search topic.
	
  - `object`: enter your nouns / objects that you are interested in; multiple objects can be entered. Do not add a space after your object. Selected objects should be related to your search topic.
	
  - verb-object example: If you are interested in policy changes related to schools opening during the COVID pandemic, options include:
  	- verbs: open, reopen, resume
	- objects: school, class, campus
	
  - `+ Semantic Match`: Select this button to add more verb-object pairings. There is no max limit. Repeat the steps above.

### Geography
The user can choose what admin level to search, such as "country", "city,state" or "state/province, country". For example, the user may wish to search for each **concept** and **target variables** by country (e.g. "COVID-19" AND "Albania" AND "TESTS" OR "TEST-KITS"). The repository includes several csv files in the `geo` folder. Any sorting (such as by population) needs to be pre-processed by the user. For user-provided csv files, the files must be collapsed to two columns, such as `city` and `state`. Any of the pre-formatted csv files can be used as model for pre-processing your file. Should the user want to sort the geography data, it must be pre-sorted prior to starting a run.

### Python Requirements
This program is built with Python 3.7; non-standard package requirements can be found in the `requirements.txt` file included in the repository.

### Configuration

Note that you must update the `subscription_key` in `config.ini` with your Bing News Search API key.

```
[BING PARAMETERS]
# keep textFormat and "searchurl" as is.
# https://docs.microsoft.com/en-us/rest/api/cognitiveservices-bingsearch/bing-news-api-v7-reference
searchurl = https://api.cognitive.microsoft.com/bing/v7.0/news/search
textFormat = HTML
subscription_key = {API KEY}
count = 10
category = Politics
mkt = en-us
safeSearch = Moderate

[LOGGER]
# CRITICAL <- ERROR <- WARNING <- INFO <- DEBUG
logger_level = INFO
```

Config Options:
  - [BING PARAMETERS]	
  	- `HTML` and `searchurl` are required and static for proper output, do not delete.
	- Obtain a subscription key at: https://docs.microsoft.com/en-us/azure/api-management/api-management-subscriptions
	- Parameter information and customizing options are at: 
	https://docs.microsoft.com/en-us/rest/api/cognitiveservices-bingsearch/bing-news-api-v7-reference  

  - [LOGGER]	
  	- Provides ability to choose level of logging for terminal returns during a run.
	- Standard options include: CRITICAL <- ERROR <- WARNING <- INFO <- DEBUG
		- For general-purpose, recommend setting logger to "INFO"
		
## Execution

### Main Script
  - main.py
  - The script does not require user manipulation to run the desired news articles search. User-specific search options and search variable selections are made in the `config.ini` and the project definition `.yaml` files as discussed above.

  The `main.py` script takes three arguments:
  1. `-r`: the location you wish to store the result `json` file
  2. `-geo`: the geo-political levels you wish to use for your execution (.csv file).
  3. `-defs`: the YAML execution definition file you wish to use

### Running the script
1. Clone the open-indicators repository to your local machine (example:`your/local/folder/`)
2. Open a Terminal window and navigate to your folder (`cd your/local/folder/open-indicators/news-article-search`)
3. Type `$ ls` and confirm all required files are listed in your workding directory.
4. Move your geo-political .csv file to: `your/local/folder/open-indicators/news-article-search/geo`
5. Run the script, for example:
	
	`$ python3 src/main.py -r=results.json -geo=geo/us_city_state.csv -defs=user_search.yaml`
	
	and generically:
	
	`$ python3 src/script.py (-r= filename for results) (-geo = geo/ geography csv) (-defs = user's keyword searches)`
	
5. The `results.json` file is written to the `results/` folder, a sub-folder of the working directory.



