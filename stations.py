import random
from abc import ABC, abstractmethod
from models import Pencil


class Station(ABC):
    """Abstract base class: every station must implement process()."""
    name: str

    @abstractmethod
    def process(self, pencil: Pencil) -> Pencil:
        pass


class GraphiteInsertStation(Station):
    name = "Graphite Core Insert"

    def process(self, pencil: Pencil) -> Pencil:
        pencil.stage_log.append("Station 1: graphite core inserted")
        if random.random() < 0.06:
            pencil.mark_defective("Graphite core missing or broken")
        else:
            pencil.graphite_core = True
        return pencil


class WoodenBodyStation(Station):
    name = "Wooden Body Assembly"

    def process(self, pencil: Pencil) -> Pencil:
        pencil.stage_log.append("Station 2: wooden body assembled")
        if random.random() < 0.05:
            pencil.mark_defective("Wooden body cracked")
        else:
            pencil.wooden_body = True
        return pencil


class EraserHolderStation(Station):
    name = "Eraser Holder Install"

    def process(self, pencil: Pencil) -> Pencil:
        pencil.stage_log.append("Station 3: eraser holder installed")
        if random.random() < 0.04:
            pencil.mark_defective("Eraser holder not aligned")
        else:
            pencil.eraser_holder = True
        return pencil


class EraserInstallStation(Station):
    name = "Eraser Install"

    def process(self, pencil: Pencil) -> Pencil:
        pencil.stage_log.append("Station 4: eraser installed")
        if random.random() < 0.04:
            pencil.mark_defective("Eraser missing or loose")
        else:
            pencil.eraser = True
        return pencil


class QualityPackagingStation(Station):
    name = "QC and Packaging"

    def process(self, pencil: Pencil) -> Pencil:
        pencil.stage_log.append("Station 5: quality control inspection")
        if not all([pencil.graphite_core, pencil.wooden_body, pencil.eraser_holder, pencil.eraser]):
            pencil.mark_defective("One or more pencil components are missing")
        else:
            pencil.packaged = True
            pencil.stage_log.append("Station 5: pencil packaged successfully")
        return pencil
