import csv
from datetime import datetime
import os

class LoggerOpenSeach:
    def __init__(self, logfile="query_log.csv"):
        self.logfile = logfile
        if not os.path.exists(self.logfile):
            with open(self.logfile, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["query", "response_time", "date"])

    def saveLog(self, query, time):
        with open(self.logfile, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([query, time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
