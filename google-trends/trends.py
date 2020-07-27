from pytrends.request import TrendReq
import argparse
import pandas as pd

iso = pd.read_csv('iso-codes.csv')
iso['country_code'] = iso['iso_code'].apply(lambda x: x.split('-')[0])

def get_geo(geo):
    if len(geo) == 2:
        country = iso[iso['country_code']==geo].iloc[0].countryLabel
        admin1 = None
    else:
        country = iso[iso['iso_code']==geo].iloc[0].countryLabel
        admin1 = iso[iso['iso_code']==geo].iloc[0].admin1Label
    return country, admin1

def get_trend(term, geo):
    pytrend = TrendReq(hl='en-US', tz=360, geo=geo)
    pytrend.build_payload(kw_list=[term])
    trend_df = pytrend.interest_over_time()
    if trend_df.shape[0] == 0:
        print(f"No trend available for term '{term}' and geo {geo}")
        return None
    else:
        trend_df = trend_df.reset_index()
        trend_df = trend_df.rename(columns={'date': 'time', term: f'{term}_value'})
        trend_df = trend_df.drop(columns='isPartial')
        trend_df[term + '_description'] = f'Google Trends for the term {term} for the geography {geo}'
        country, admin1 = get_geo(geo)
        trend_df['country'] = country
        if admin1:
            trend_df['admin_1'] = admin1
        return trend_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Obtain Google Trends data')
    parser.add_argument('--term', dest ='term', type=str, help='The term of interest.')
    parser.add_argument('--geo', dest ='geo', type=str, default='ET', help='The geography of interest in https://en.wikipedia.org/wiki/ISO_3166-2 format')
    parser.add_argument('--output', dest ='output', type=str, default='trend.csv', help='The name of the desired output file.')
    args = parser.parse_args()
    term = args.term
    geo = args.geo

    trend = get_trend(term, geo)
    trend.to_csv(args.output, index=False)