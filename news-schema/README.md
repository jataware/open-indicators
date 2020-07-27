# News Schema

The news-schema script transforms the .json file from the News Article Search into a schema-compliant .csv file in preparation for registration to a datamart.

#### Run script:

1. run `cd your/local/folder/open-indicators/news-schema/`
2. Copy your `user_search.yaml` (from the webapp UI) to `your/local/folder/open-indicators/news-schema/news/`
3. Copy your `results.json` (from the News Article Search) to `your/local/folder/open-indicators/news-schema/news/`
4. You must add metadata to the yaml file.  Cut and paste the snippet below into your yaml file, update the values, and save.

        admin:
          adminX: <ENTER THE LOWER ADMIN LEVEL>
          adminY: <ENTER THE HIGHER ADMIN LEVEL>
          country: <ENTER THE COUNTRY>

    Example:
    
        admin:
          adminX: admin_1
          adminY: admin_3
          country: United States

5. run `python3 news-csv.py --news=news/results.json --yaml=news/user_search.yaml --output=news/results.csv --type=False`
6. Your file for registration will be in the ../news folder. 
```
