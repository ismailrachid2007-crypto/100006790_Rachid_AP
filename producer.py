"""Optional telemetry producer.
Run this only when Docker, InfluxDB and Grafana are running.
It sends sample values so the Grafana dashboard is not empty during testing.
"""
import random
import time
from database import InfluxWriter

writer = InfluxWriter()
total = good = defective = 0

while True:
    total += 1
    if random.random() < 0.12:
        defective += 1
        state = "UNSCHEDULED_DOWNTIME"
        faulted = 1
    else:
        good += 1
        state = "PRODUCTIVE"
        faulted = 0
    writer.write_status(state=state, total=total, good=good, defective=defective, faulted=faulted)
    print(f"sent: total={total}, good={good}, defective={defective}, state={state}")
    time.sleep(2)
