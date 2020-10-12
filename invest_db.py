
import pymysql
from pymysql.cursors import DictCursor

class DB:
    def __init__(self, connect_timeout=15):
        self.conn = pymysql.connect(
                    host='5.3.6.108',
                    user='invest',
                    password='invest',
                    db='invest_db',
                    charset='utf8mb4',
                    cursorclass=DictCursor
                )
        self.cursor = self.conn.cursor()

    def get_idea(self, agent_id=None):
        if agent_id is None:
            p = 0
        else:
            p = agent_id
        self.cursor.callproc('invest_db.get_idea', [p, ])
        print("Printing laptop details")
        for result in self.cursor.stored_results():
            print(result.fetchall())

