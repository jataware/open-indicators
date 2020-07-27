# Google Trends

Install requirements with `pip3 install -r requirements.txt`.

To run, execute `python3 trends.py --term=someterm --geo=somegeo --output=some.csv` where `someterm` is the term of interest for obtaining a trend and `somegeo` is the [`ISO 3166-2`](https://en.wikipedia.org/wiki/ISO_3166-2) code for the location of interest. You should provide to the `--output` the filename you wish your trend information to be saved.

For example:

```
python trends.py --term=teff --geo=ET-AA --output=teff.csv
```

Will yield a `.csv` file called `teff.csv` containing Google Trend information for Addis Ababa, Ethiopia:

| time       | teff_value | teff_description                                        | country  | admin_1     |
|------------|------------|---------------------------------------------------------|----------|-------------|
| 2015-07-19 | 15         | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |
| 2015-07-26 | 15         | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |
| 2015-08-02 | 16         | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |
| 2015-08-09 | 0          | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |
| 2015-08-16 | 0          | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |
| 2015-08-23 | 22         | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |
| 2015-08-30 | 15         | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |
| 2015-09-06 | 0          | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |
| 2015-09-13 | 14         | Google Trends for the term teff for the geography ET-AA | Ethiopia | Addis Ababa |


## ISO Country/Admin1 Codes
You can refer to `iso-codes.csv` to identify the ISO code you wish to use. Note that you should just use the two letter country code if you wish to identify a trend for the whole country. You should use the full `ISO 3166-2` code to identify a trend for a specific admin 1 region. Note that for some admin 1 regions no trend information is available for certain terms.