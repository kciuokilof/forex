from datetime import datetime
from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.webdriver import Proxy
from selenium.webdriver.common.proxy import ProxyType

from data_download.lib.dataset import get_sundays, ForexFactoryCalendarWeek
from selenium.webdriver.chrome.options import Options

from data_download.lib.db import ForexDb
from data_download.lib.decorators import timing
import multiprocessing as mp

from data_download.lib.webdriver import get_user_agent_driver


def add_datetime_for_db_insert(df, year):
    df['datetime'] = df.apply(
        lambda row: datetime.strptime(str('SunOct 6 ' + str(year) + ' ' + row[1]).strip(),
                                      '%a%b %d %Y %I:%M%p').strftime("%Y-%m-%d %H:%M:%S")
        if not any(x in row[1] for x in ['Day', 'Data', 'Tentative']) else datetime.strptime(str('SunOct 6 ' + str(year)).strip(), '%a%b %d %Y').strftime(
            "%Y-%m-%d %H:%M:%S"),
        axis=1)
    df = df.drop(columns=[df.columns[0], df.columns[1]])
    return df


def adjust_column_names_to_db_schema(upload_df):
    columns = [column[0] if type(column) == tuple else column for column in upload_df.columns]
    columns = ['event_name' if x == 'Unnamed: 4_level_0' else x for x in columns]
    upload_df.columns = columns
    return upload_df


@timing
def upload_week(driver, year, week, db):
    forex_factory = ForexFactoryCalendarWeek(driver, week)
    df = forex_factory.get_df_from_day_of_calendar()
    df = add_datetime_for_db_insert(df, year)
    df = adjust_column_names_to_db_schema(df)
    df = forex_factory.add_events_ids(df)
    df = forex_factory.add_events_impact(df)
    upload_df = pd.DataFrame()
    for name, row in df.iterrows():
        event_details = forex_factory.get_event_detail(row['event_id'])
        concat_series = pd.concat([event_details, row])
        upload_df = upload_df.append(concat_series, ignore_index=True)

        upload_df = adjust_column_names_to_db_schema(upload_df)
        upload_df = upload_df.drop(columns=['Graph', 'Detail'])
    # try:
    #     db.upload_event(upload_df)
    # except Exception as e:
    #     db.rollback_changes()
    #     print(e)
    # db.commit_changes()
    # print(f'uploaded: {len(upload_df)} rows')
    upload_df.to_csv(str(year)+str(week))


def upload_year(year):
    db = ForexDb()

    # Below is tested line

    weeks = get_sundays(year)
    driver = get_user_agent_driver()
    for week in list(weeks):
        print(week)
        upload_week(driver, year, week, db)


if __name__ == '__main__':
    upload_year(2019)
    # with mp.Pool(2) as p:
    #     # upload_year
    #     p.map(upload_year, [2019, 2018, 2017, 2016, 2015, 2014])

