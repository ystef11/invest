#!/usr/bin/python3
# coding=utf8
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
        self.cursor.callproc('get_idea', [p,])
        return self.cursor.fetchall()

    def get_idea_agent(self):
        self.cursor.callproc('get_idea_agent')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    db = DB()
    print(db.get_idea())
    print(db.get_idea_agent())
    db.close()