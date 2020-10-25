import pyodbc
import mysql.connector


class ForexDb:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="linux123",
        database="forex"
    )

    cursor = conn.cursor()

    def upload_event(self, df):

        rollback_flag = False
        for i, row in df.iterrows():
            row = row.dropna()
            columns = "`"

            columns += "`,`".join([str(i) for i in row.index.tolist()])
            columns += "`"
            sql = "INSERT INTO events (" + columns + ") VALUES (" + "%s," * (
                    len(row) - 1) + "%s)"
            try:
                self.cursor.execute(sql, tuple(row.fillna('None')))
            except Exception as e:
                rollback_flag = True
                print(e)
        if rollback_flag:
            self.rollback_changes()

    def commit_changes(self):
        self.conn.commit()

    def rollback_changes(self):
        self.conn.rollback()
