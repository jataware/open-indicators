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

      - `--type=False` a dummy feauture `article_value` is created to support the qualifier assignments of: url, title, and text data. For datasets with many features this reduces redunancy of data and can significantly reduce the size of the file.

      - `--type=True` Each feature in the dataset is assigned the url, title, and text as a qualifier. This allows for direct assignment of the qualifiers to a feature, but is also redundant and can lead to exceptioanlly large .csv files. <i>Not recommended</i> for datasets with more than a few features.
      
6. Your file for registration will be in the ../news folder.
