from unittest import TestCase
from selenium import webdriver

from data_download.lib.dataset import get_sundays, ForexFactoryCalendarWeek, get_overlapping_events
import pandas as pd

class TestForexFactoryCalendarWeek(TestCase):
    from os import listdir
    from os.path import isfile, join
    driver = webdriver.Chrome('..\..\data\chromedriver.exe')
    forex_factory = ForexFactoryCalendarWeek(driver, 'oct11.2020')

    def test_get_df_from_day_of_calendar(self):
        assert not self.forex_factory.get_df_from_day_of_calendar().empty

    def test_get_event_id(self):
        assert '111885' == self.forex_factory.add_events_ids()[49]

    def test_get_event_detail(self):
        assert 'Source' in self.forex_factory.get_event_detail('111885').iloc[:, 0].tolist()

    def test_get_sundays(self):
        assert 'oct18.2020' in list(get_sundays(2020))


class Test(TestCase):
    def test_get_overlapping_events(self):
        df = pd.DataFrame([['event_1'], ['event_2'], ['event_2'], ['event_3']], columns=['event_name'])
        events_ids = ['event_0', 'event_2', 'event_2', 'event_2.5', 'event_3', 'event_3']
        events_names = ['event_0', 'event_2', 'event_2','event_2.5', 'event_3', 'event_3']
        new_df = get_overlapping_events(df, events_ids, events_names)
        df = pd.DataFrame([['event_2', 'event_2'], ['event_2', 'event_2'], ['event_3', 'event_3']], columns=['event_id', 'event_name'])
        assert df.equals(new_df)
