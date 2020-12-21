# Google Trends

Install requirements with `pip3 install -r requirements.txt`.

To run, execute `python3 trends.py --term=someterm --country=somecountry --state=somestate --output=some.csv` where:

<b>Required arguments:</b>
  - `--term=someterm` is the term of interest for obtaining a trend.
  - `--country=somecountry` is the country of interest.
  
<b>Optional arguments:</b>  
  - `--state=somestate` is the state or provincial level of interest; without a `state` Google Trends returns country-level results
  - `--output=some.csv` is your desired output filename, defaults to `trend.csv`

Note: Any argument with a space requires quotes (such as `'Addis Ababa'` in the example below)

<b>Example:</b>

```
python trends.py --term=teff --country=Ethiopia --state='Addis Ababa' --output=teff.csv
```

Will yield a `.csv` file called `teff.csv` containing Google Trend information for Addis Ababa, Ethiopia:

| timestamp   | iso_time    | value | description                      | country  | state       | iso2 |
|-------------|-------------|-------|----------------------------------|----------|-------------|------|
| 1451203200  | 2015-12-27  | 0     | Google Trends for teff for ET-AA | Ethiopia | Addis Ababa | ET   |
| 1451808000  | 2016-01-03  | 20    | Google Trends for teff for ET-AA | Ethiopia | Addis Ababa | ET   |
| 1452412800  | 2016-01-10  | 57    | Google Trends for teff for ET-AA | Ethiopia | Addis Ababa | ET   |
| 1453017600  | 2016-01-17  | 20    | Google Trends for teff for ET-AA | Ethiopia | Addis Ababa | ET   |

Where:

  - `timestamp`: Google Trends date-time in epoch time
  - `iso_time`: ISO-8601 date (YYYY-MM-DD)
  - `value`: a normalized score on how 'popular' your `term` is for your chosen geopolitical area versus other searches at a particular time
  - `description`: Tags data with `term` and iso2 code for country-state (if state included)
  - `state`: State/province/woreda for Google Trends `term`; `None` if no state entered
  - `iso2`: Country-level iso 2 abbreviation


## ISO Country/State Names
You can refer to `iso-codes.csv` to identify the country and state format you wish to use; the country/state must match the `iso-codes.csv` to include spelling, form, and capitalization. For instance: if you are interested in trend data for Amhara in Ethiopia, you must enter `--state='Amhara Region'`. If you wish to only get country-level trend data, do not include a `--state=` argument. Again, any argument you provide that has whitespace (such as `Addis Ababa` must be in quotes. Note that for some state-level searches, no trend information is available for certain terms.

## Docker Container

To run Google Trends in a Docker container:

1. Build a local image in your working directory with `docker build -t trends .`
2. Run the trends.py script with your desired arguments: 
    `docker run --rm trends --term=cafe --country=Italy --state=Campania --output=cafe.csv`
