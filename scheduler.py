import schedule
import time
from scanner import scan

# Intraday scan (every 5 minutes)
schedule.every(5).minutes.do(scan, interval="5m")

# Daily scan (after market close)
schedule.every().day.at("16:10").do(scan, interval="1d")

print("📡 Scanner running...")

while True:
    schedule.run_pending()
    time.sleep(1)

