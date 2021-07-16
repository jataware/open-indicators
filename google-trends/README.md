# Google Trends

Install requirements with `pip3 install -r requirements.txt`.

To run, execute `python3 trends.py --term=someterm --country=somecountry --admin1=someadmin1 --output=some.csv` where:

<b>Required arguments:</b>
  - `--term=someterm` is the term of interest for obtaining a trend.
  - `--country=somecountry` is the country of interest.
  
<b>Optional arguments:</b>  
  - `--admin1=someadmin1` is the state or provincial level of interest; without a `state` Google Trends returns country-level results
  - `--output=some.csv` is your desired output filename, defaults to `trend.csv`

Note: Any argument with a space requires quotes (such as `'Addis Ababa'` in the example below)

<b>Example:</b>

```
python trends.py --term=teff --country=Ethiopia --admin1='Addis Ababa' --output=teff.csv
```

Will yield a `.csv` file called `teff.csv` containing Google Trend information for Addis Ababa, Ethiopia:


| timestamp   | country   |admin1          | feature     | value | search_term |
|-------------|-----------|----------------|-------------|-------|-------------|
| 1451203200  | Ethiopia  | Addis Ababa    | trend level | 1     | teff        | 
| 1451808000  | Ethiopia  | Addis Ababa    | trend level | 4     | teff        | 
| 1452412800  | Ethiopia  | Addis Ababa    | trend level | 4     | teff        | 
| 1453017600  | Ethiopia  | Addis Ababa    | trend level | 8     | teff        | 

Where:

  - `timestamp`: Date of Google Trends data in epoch time; time of day is T08:00:00Z for all rows.
  - `country`: Country that Google Trends searched over for your `term` 
  - `admin1`: admin1/State/province/woreda that Google Trends searched over for your `term`; `None` if no admin1 entered
  - `feature`: Identifies the trend value.
  - `value`: a normalized score on how 'popular' your `term` is for your chosen geopolitical area versus other searches at a particular time
  - `search_term`: the keyword or phrase searched for




## ISO Country/State Names
You can refer to `iso-codes.csv` to identify the country and state format you wish to use; the country/state must match the `iso-codes.csv` to include spelling, form, and capitalization. For instance: if you are interested in trend data for Amhara in Ethiopia, you must enter `--admin1='Amhara Region'`. If you wish to only get country-level trend data, do not include a `--admin1=` argument. Again, any argument you provide that has whitespace (such as `Addis Ababa` must be in quotes. Note that for some state-level searches, no trend information is available for certain terms.

## Docker Container

To run Google Trends in a Docker container:

1. Build a local image in your working directory with `docker build -t trends .`
2. Run the trends.py script with your desired arguments: 
    `docker run -v ${PWD}:/output --rm trends --term=cafe --country=Italy --admin1=Campania --output=/output/cafe.csv`
