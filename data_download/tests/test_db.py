from unittest import TestCase
import pandas as pd

from data_download.lib.db import ForexDb


class TestDb(TestCase):
    from os import listdir
    from os.path import isfile, join
    db = ForexDb()

    def test_upload_event(self):
        test_event = pd.DataFrame([['test_name']], columns=['event_name'])
        self.db.upload_event(test_event)
        self.db.rollback_changes()
