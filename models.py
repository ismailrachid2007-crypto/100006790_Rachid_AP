from dataclasses import dataclass, field
from typing import List


@dataclass
class Pencil:
    """One pencil moving through the production line."""
    pencil_id: int
    graphite_core: bool = False
    wooden_body: bool = False
    eraser_holder: bool = False
    eraser: bool = False
    packaged: bool = False
    defective: bool = False
    defect_reason: str = "None"
    stage_log: List[str] = field(default_factory=list)

    def mark_defective(self, reason: str) -> None:
        self.defective = True
        self.defect_reason = reason
        self.stage_log.append(f"DEFECT: {reason}")
