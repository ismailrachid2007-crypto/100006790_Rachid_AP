from typing import Dict, Optional
from database import InfluxWriter
from models import Pencil
from stations import (
    EraserHolderStation,
    EraserInstallStation,
    GraphiteInsertStation,
    QualityPackagingStation,
    WoodenBodyStation,
)


class ProductionLine:
    """Back-end orchestrator for the pencil production line."""

    def __init__(self) -> None:
        self.running = False
        self.faulted = False
        self.machine_state = "IDLE"
        self.product_id = 0
        self.total_parts = 0
        self.good_parts = 0
        self.defective_parts = 0
        self.last_error = "None"
        self.last_pencil: Optional[Pencil] = None
        self.database = InfluxWriter()
        self.stations = [
            GraphiteInsertStation(),
            WoodenBodyStation(),
            EraserHolderStation(),
            EraserInstallStation(),
            QualityPackagingStation(),
        ]

    def start(self) -> None:
        self.running = True
        self.faulted = False
        self.machine_state = "PRODUCTIVE"
        self.last_error = "None"
        self.write_telemetry()

    def stop(self) -> None:
        self.running = False
        self.machine_state = "STANDBY"
        self.write_telemetry()

    def reset(self) -> None:
        self.running = False
        self.faulted = False
        self.machine_state = "IDLE"
        self.product_id = 0
        self.total_parts = 0
        self.good_parts = 0
        self.defective_parts = 0
        self.last_error = "None"
        self.last_pencil = None
        self.write_telemetry()

    def produce_one_part(self) -> Pencil:
        self.product_id += 1
        pencil = Pencil(self.product_id)
        self.machine_state = "PRODUCTIVE"

        for station in self.stations:
            if pencil.defective:
                break
            station.process(pencil)

        self.total_parts += 1
        if pencil.defective:
            self.defective_parts += 1
            self.faulted = True
            self.running = False
            self.machine_state = "UNSCHEDULED_DOWNTIME"
            self.last_error = pencil.defect_reason
        else:
            self.good_parts += 1
            self.faulted = False
            self.last_error = "None"
            self.machine_state = "PRODUCTIVE" if self.running else "STANDBY"

        self.last_pencil = pencil
        self.write_telemetry()
        return pencil

    def write_telemetry(self) -> None:
        self.database.write_status(
            state=self.machine_state,
            total=self.total_parts,
            good=self.good_parts,
            defective=self.defective_parts,
            faulted=int(self.faulted),
        )

    def get_status(self) -> Dict[str, str]:
        return {
            "Machine State": self.machine_state,
            "Total Parts": str(self.total_parts),
            "Good Parts": str(self.good_parts),
            "Defective Parts": str(self.defective_parts),
            "Faulted": "YES" if self.faulted else "NO",
            "Last Error": self.last_error,
        }
