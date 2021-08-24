from pytrends.request import TrendReq
import argparse
import pandas as pd
import dateutil.parser as dp
import os
from time import time
import numpy as np

# Example CLI: python3 trends.py --term='election' --country='Ethiopia' --admin1='Addis Ababa' --output=output.csv

# For Docker testing:
print(os.getcwd())

# Read in iso codes to build lookup dicts
iso = pd.read_csv("iso-codes.csv")
iso["country_code"] = iso["iso_code"].apply(lambda x: x.split("-")[0])

# Dict of Country to iso2 code (for country only trend search):
ctry_to_iso_d = dict(zip(iso.countryLabel, iso.country_code))

# Dict of (key=country, key=admin1) value = Country-admin1 iso2 code (for country and admin1 trend search)
admin1_to_iso_d = (
    iso.groupby("countryLabel")
    .apply(lambda x: dict(zip(x["admin1Label"], x["iso_code"])))
    .to_dict()
)


# convert user input to iso code:
def input_to_iso(country, admin1=None):
    if admin1:
        geo = admin1_to_iso_d.get(country, {}).get(admin1, None)
    else:
        geo = ctry_to_iso_d.get(country, None)
    return geo


def iso_to_epoch(iso_time):
    parsed_t = dp.parse(iso_time)
    return parsed_t.strftime("%s")


def no_data(term, country, admin1):
    if country:
        ctry = country
    else:
        ctry = np.nan
    
    if admin1:
        admin1 = admin1
    else:
        admin1 = np.nan
    
    empty_dict = {'timestamp': [round(time()*1000)],
                  'country': [ctry],
                  'admin1': [admin1],
                  'trend_level': [np.nan],
                  'search_term':[f'{term}']
                 }

    return pd.DataFrame(empty_dict)


def get_trend(term, country, admin1):

    geo = input_to_iso(country, admin1)
    # geo can = None if the user enters invalid geo keys
    if geo:
        pytrend = TrendReq(hl="en-US", tz=0, geo=geo)
        pytrend.build_payload(kw_list=[term])
        trend_df = pytrend.interest_over_time()

        if trend_df.empty:
            print(
                f"\nNo trend available for term:'{term}' country:'{country}' admin1:'{admin1}'\n"
            )
            return no_data(term, country, admin1)

        # YES Google trend
        else:
            trend_df = trend_df.reset_index()
            trend_df = trend_df.rename(columns={"date": "time", term: "trend_level"})
            trend_df = trend_df.drop(columns="isPartial")
            trend_df["country"] = country
            trend_df["search_term"] = f"{term}"

            if admin1:
                trend_df["admin1"] = admin1

            else:
                trend_df["admin1"] = np.nan

            # Convert to epoch time
            trend_df["timestamp"] = trend_df.time.apply(lambda x: iso_to_epoch(str(x)))
            trend_df = trend_df.drop(columns="time")

            # reorder/rename columns and keep ISO time for comparison
            cols = list(trend_df)
            cols.insert(0, cols.pop(cols.index("timestamp")))
            trend_df = trend_df.reindex(columns=cols)

            df = pd.DataFrame(
                trend_df,
                columns=[
                    "timestamp",
                    "country",
                    "admin1",
                    "trend_level",
                    "search_term",
                ],
            )

            return df

    # bad user country/admin1 inputs
    else:
        print(f"\nFor country:'{country}' admin1:'{admin1}'")
        print(
            "Invalid input:\n  Reference 'country_admin1.csv' for country/admin1 names.\n  Note: Input parameters with spaces must be in quotes.\n"
        )

        return no_data(term, country, admin1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Obtain Google Trends data")
    parser.add_argument("--term", dest="term", type=str, help="The term of interest.")
    parser.add_argument(
        "--country",
        dest="country",
        type=str,
        default="Ethiopia",
        help='Required: Country of interest: "Ethiopia"',
    )
    parser.add_argument(
        "--admin1",
        dest="admin1",
        type=str,
        default=None,
        help='Optional: admin1/province/woreda of interest: "Addis Ababa"',
    )
    parser.add_argument(
        "--output",
        dest="output",
        type=str,
        default="trend.csv",
        help="The name of the desired output file.",
    )
    args = parser.parse_args()

    term = args.term
    country = args.country
    admin1 = args.admin1
    output = args.output
    trend = get_trend(term, country, admin1)

    if isinstance(trend, pd.DataFrame):
        trend.to_csv(args.output, index=False)
        print(trend)
        print(f'\n"{output}" written to {os.getcwd()}\n')
