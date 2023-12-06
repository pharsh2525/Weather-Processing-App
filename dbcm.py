"""
 Name: Harshkumar Patel & Brenan Hermann
 Date: 16 November 2023
 Project: Weather Processing App
"""

import sqlite3
import logging


class DBCM:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type or exc_val or exc_tb:
                logging.error(f"Database error: {exc_val}")
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
