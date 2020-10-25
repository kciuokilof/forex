import calendar
import random
import time

import pandas as pd
import requests
from lxml import html
from lxml.etree import tostring
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import date, timedelta

from data_download.lib.web_elments import repeat_on_failure


def get_sundays(year):
    d = date(year, 1, 1)  # January 1st
    d += timedelta(days=6 - d.weekday())  # First Sunday
    while d.year == year:
        d_str = calendar.month_name[d.month].lower()[:3] + str(d.day) + '.' + str(d.year)
        yield d_str
        d += timedelta(days=7)


def get_overlapping_events(df, events_ids, events_names):
    new_df = pd.DataFrame()
    start_idx = 0
    for _, row in df.iterrows():
        df_event_name = row['event_name']
        for idx, event_name in enumerate(events_names[start_idx:]):
            if df_event_name == event_name:
                row['event_id'] = events_ids[idx+ start_idx]
                new_df = new_df.append(row)
                start_idx = idx
                break
    return new_df.reset_index(drop=True)


class ForexFactoryCalendarWeek:
    url = 'https://www.forexfactory.com/'
    calendar_url = 'https://www.forexfactory.com/calendar'

    def __init__(self, driver, week):
        self.calendar_url = self.calendar_url + '?week=' + week
        self.page = requests.get(self.calendar_url)
        self.page_root = html.fromstring(self.page.text)
        self.driver = driver
        self.driver.get(self.calendar_url)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'ui-outer')))

    def get_df_from_day_of_calendar(self) -> pd.DataFrame:
        table_web_element = self.driver.find_element_by_xpath('//table[@class="calendar__table"][1]').get_attribute('outerHTML')
        df = pd.read_html(table_web_element)[0]
        final_df = df[~(df.iloc[:, 4].str.fullmatch('Graph') | df.iloc[:, 4].str.startswith('Actual') | df.iloc[:,
                                                                                                        4].str.fullmatch(
            'No Data Series Details') | df.iloc[:, 4].isna())]
        final_df = final_df[~(final_df.iloc[:, 1] == final_df.iloc[:, -1])]
        final_df.iloc[:, [0, 1]] = final_df.iloc[:, [0, 1]].fillna(method='ffill')
        return final_df.reset_index(drop=True)

    def add_events_ids(self, df):
        events_len = len(df)
        # events_ids_xpath = '//tr[contains(@class,"calendar__row calendar__expand")]'
        events_ids_xpath = '//tr[contains(@class,"calendar__row calendar_row calendar__row")]'
        events_names_xpath = events_ids_xpath + '//span[@class="calendar__event-title"]'
        events_ids = [el.get_attribute('data-eventid').strip() for el in
                      self.driver.find_elements_by_xpath(events_ids_xpath)]
        events_names = [el.text.strip() for el in
                        self.driver.find_elements_by_xpath(events_names_xpath)]
        events_ids = [events_ids[idx] for idx, event_name in enumerate(events_names) if event_name != '']
        events_names = [event_name for idx, event_name in enumerate(events_names) if event_name != '']
        if len(events_ids) == events_len and df['event_name'].to_list() == events_names:
            df['event_id'] = events_ids
            return df
        new_df = get_overlapping_events(df, events_ids, events_names)
        print(f'len(new_df):    { len(new_df)};  len(df):    {len(df)};  len(events_ids):    {len(events_ids)}')
        return new_df

    def get_event_detail(self, event_id) -> pd.Series:
        element = self.driver.find_element_by_xpath(f'//tr[@data-eventid="{event_id}"]//a[@title="Open Detail"]')
        time.sleep(random.uniform(0, 3))
        self.driver.execute_script("arguments[0].click();", element)
        detail_button = repeat_on_failure(self.driver.find_element_by_xpath,
                                          f'//tr[@data-eventid="{event_id}" and contains(@class, "calendar__details")]//table[2]')
        tbl = detail_button.get_attribute('outerHTML')
        df_list = pd.read_html(tbl)
        assert len(df_list) == 1, f'Wrong elements detail tables number  for event "{event_id}" ' \
                                  f'on the one page"{self.calendar_url}"'
        df_list[0].columns = ['detail_name', 'detail_value']
        df_list[0]['detail_name'] = ['detail_' + x.replace(' ', '') for x in df_list[0]['detail_name']]
        event_details = df_list[0].set_index('detail_name')['detail_value']
        return event_details

    def add_events_impact(self, df):
        df['Impact'] = df.apply(lambda row: self.get_single_event_impact(row.event_id), axis=1)
        return df

    def get_single_event_impact(self, event_id):
        xpath = f'//tr[@data-eventid={event_id}]//td[contains(@class, "calendar__impact")]//span'
        return self.driver.find_element_by_xpath(xpath).get_attribute('class')

