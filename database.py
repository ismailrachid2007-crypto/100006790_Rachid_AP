import time

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
except Exception:
    InfluxDBClient = None
    Point = None
    WritePrecision = None
    SYNCHRONOUS = None

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "srh-token-123"
INFLUX_ORG = "SRH"
INFLUX_BUCKET = "production_line"


class InfluxWriter:
    """Writes production data to InfluxDB. If InfluxDB is off, the HMI still runs."""

    def __init__(self) -> None:
        self.enabled = False
        self.client = None
        self.write_api = None
        if InfluxDBClient is None:
            return
        try:
            self.client = InfluxDBClient(
                url=INFLUX_URL,
                token=INFLUX_TOKEN,
                org=INFLUX_ORG,
                timeout=1000,
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.enabled = True
        except Exception:
            self.enabled = False

    def write_status(self, state: str, total: int, good: int, defective: int, faulted: int) -> None:
        if not self.enabled or Point is None:
            return
        try:
            point = (
                Point("pencil_line")
                .tag("machine", "Pencil_Line_01")
                .field("state_code", self.state_to_code(state))
                .field("parts_produced", total)
                .field("good_parts", good)
                .field("defective_parts", defective)
                .field("faulted", faulted)
                .time(time.time_ns(), WritePrecision.NS)
            )
            self.write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        except Exception:
            self.enabled = False

    @staticmethod
    def state_to_code(state: str) -> int:
        states = {
            "IDLE": 0,
            "STANDBY": 1,
            "PRODUCTIVE": 2,
            "STOPPED": 3,
            "UNSCHEDULED_DOWNTIME": 4,
        }
        return states.get(state, -1)
