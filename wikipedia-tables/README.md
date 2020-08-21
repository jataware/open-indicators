# Wikipedia Table Search

## Overview
This jupyter notebook:

   1. Gathers and builds a list of Ethiopian-related wikipedia URLs. The data pull is two-pronged:

       - Through the [wikidata query service](https://query.wikidata.org/) and leveraging the [qwikidata module ](https://qwikidata.readthedocs.io/en/stable/readme.html)

       - Via scraping the [wikipedia search](https://en.wikipedia.org/w/index.php?title=Special:Search&limit=20&offset=0&profile=default) with Beautiful Soup

   2. Searches the urls for tables using beautiful soup. Tables are limited to `wikidata`- and `infobox`-type tables.

   3. Provides a keyword search of the text presented <i>in</i> the tables.


