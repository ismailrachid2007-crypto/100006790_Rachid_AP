import time
import tkinter as tk
from typing import Dict, Optional
from models import Pencil
from production_line import ProductionLine


class ProductionLineHMI:
    """Modern dark HMI for the pencil production-line simulator."""

    BG = "#f3f4f6"
    OUTER = "#293044"
    INNER = "#e7edf7"
    PANEL = "#111827"
    CARD = "#232b3d"
    CARD_BORDER = "#3b465f"
    MUTED = "#aeb7ca"
    WHITE = "#f8fafc"
    YELLOW = "#facc15"
    GREEN = "#6bd36f"
    RED = "#e55752"
    BLUE = "#5b7bea"
    ORANGE = "#f59e0b"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.line = ProductionLine()
        self.auto_job = None
        self.kpi_labels: Dict[str, tk.Label] = {}
        self.status_labels: Dict[str, tk.Label] = {}
        self.stage_labels: Dict[str, tk.Label] = {}
        self.log_box: Optional[tk.Text] = None
        self.latest_error: Optional[tk.Label] = None
        self.current_stage = "Waiting"
        self.build_window()
        self.build_widgets()
        self.update_status_labels()

    def build_window(self) -> None:
        self.root.title("Pencil Line HMI")
        self.root.geometry("980x690")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

    def build_widgets(self) -> None:
        # Big industrial tablet-style frame
        shell = tk.Frame(self.root, bg=self.OUTER)
        shell.pack(fill="both", expand=True, padx=28, pady=24)

        bezel = tk.Frame(shell, bg=self.INNER)
        bezel.pack(fill="both", expand=True, padx=22, pady=22)

        panel = tk.Frame(bezel, bg=self.PANEL)
        panel.pack(fill="both", expand=True, padx=18, pady=18)

        # Header
        tk.Label(
            panel,
            text="Pencil Line HMI",
            bg=self.PANEL,
            fg=self.WHITE,
            font=("Segoe UI", 26, "bold"),
        ).pack(anchor="w", padx=30, pady=(22, 0))
        tk.Label(
            panel,
            text="Operator screen for controlling and monitoring the pencil production simulator",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 11),
        ).pack(anchor="w", padx=31, pady=(2, 16))

        # Buttons
        button_frame = tk.Frame(panel, bg=self.PANEL)
        button_frame.pack(anchor="w", padx=30, pady=(0, 22))
        self.make_button(button_frame, "START", self.GREEN, self.start_machine).pack(side="left", padx=(0, 18))
        self.make_button(button_frame, "STOP", self.RED, self.stop_machine).pack(side="left", padx=(0, 18))
        self.make_button(button_frame, "RESET", self.BLUE, self.reset_machine).pack(side="left", padx=(0, 18))
        self.make_button(button_frame, "PRODUCE ONE PART", self.ORANGE, self.produce_once, width=18).pack(side="left")

        # KPI cards in two columns
        card_grid = tk.Frame(panel, bg=self.PANEL)
        card_grid.pack(fill="x", padx=30, pady=(0, 12))
        card_grid.columnconfigure(0, weight=1)
        card_grid.columnconfigure(1, weight=1)

        self.make_card(card_grid, "Machine State", "Machine State", 0, 0)
        self.make_card(card_grid, "Current Stage", "Current Stage", 0, 1)
        self.make_card(card_grid, "Good Parts", "Good Parts", 1, 0)
        self.make_card(card_grid, "Defective Parts", "Defective Parts", 1, 1)
        self.make_card(card_grid, "Total Parts", "Total Parts", 2, 0)
        self.make_card(card_grid, "Faulted", "Faulted", 2, 1)

        # Latest error banner
        self.latest_error = tk.Label(
            panel,
            text="Latest Error: None",
            bg="#321b22",
            fg="#fecaca",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=14,
            pady=7,
            highlightthickness=1,
            highlightbackground=self.RED,
        )
        self.latest_error.pack(fill="x", padx=30, pady=(0, 18))

        # Station progress row
        station_title = tk.Label(
            panel,
            text="5 STATION PRODUCTION FLOW",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        station_title.pack(fill="x", padx=30, pady=(0, 7))
        station_row = tk.Frame(panel, bg=self.PANEL)
        station_row.pack(fill="x", padx=30, pady=(0, 18))
        stations = [
            "Graphite\nInsert",
            "Wooden Body\nAssembly",
            "Eraser Holder\nInstall",
            "Eraser\nInstall",
            "QC &\nPackaging",
        ]
        for station in stations:
            box = tk.Label(
                station_row,
                text=station,
                bg=self.CARD,
                fg=self.WHITE,
                font=("Segoe UI", 10, "bold"),
                height=3,
                highlightthickness=1,
                highlightbackground=self.CARD_BORDER,
            )
            box.pack(side="left", expand=True, fill="x", padx=(0, 10))
            self.stage_labels[station] = box

        # Production log
        log_title = tk.Label(
            panel,
            text="LIVE PRODUCTION LOG",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        log_title.pack(fill="x", padx=30, pady=(0, 6))
        self.log_box = tk.Text(
            panel,
            height=8,
            bg="#0b1220",
            fg="#e5edf7",
            insertbackground="white",
            font=("Consolas", 9),
            bd=0,
            padx=12,
            pady=10,
        )
        self.log_box.pack(fill="both", expand=True, padx=30, pady=(0, 24))
        self.add_log("System ready. Press START or PRODUCE ONE PART.")

    def make_button(self, parent, text: str, color: str, command, width: int = 12) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            width=width,
            height=2,
            bd=0,
            relief="flat",
            cursor="hand2",
        )

    def make_card(self, parent, title: str, key: str, row: int, col: int) -> None:
        card = tk.Frame(parent, bg=self.CARD, highlightthickness=1, highlightbackground=self.CARD_BORDER)
        card.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 18, 0), pady=(0, 14), ipady=8)
        tk.Label(card, text=title, bg=self.CARD, fg=self.MUTED, font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=16, pady=(5, 0))
        value = tk.Label(card, text="-", bg=self.CARD, fg=self.YELLOW, font=("Segoe UI", 15, "bold"), anchor="w")
        value.pack(fill="x", padx=16, pady=(4, 3))
        self.kpi_labels[key] = value

    def start_machine(self) -> None:
        self.line.start()
        self.current_stage = "Running"
        self.add_log("Machine started in PRODUCTIVE state.")
        self.update_status_labels()
        self.run_auto_cycle()

    def stop_machine(self) -> None:
        self.cancel_auto_cycle()
        self.line.stop()
        self.current_stage = "Stopped"
        self.add_log("Machine stopped. State changed to STANDBY.")
        self.update_status_labels()

    def reset_machine(self) -> None:
        self.cancel_auto_cycle()
        self.line.reset()
        self.current_stage = "Waiting"
        self.clear_log()
        self.add_log("Machine reset. Counters cleared.")
        self.update_status_labels()

    def produce_once(self) -> None:
        if self.line.machine_state in ["IDLE", "STANDBY", "STOPPED"]:
            self.line.start()
        pencil = self.line.produce_one_part()
        self.current_stage = "QC & Packaging" if not pencil.defective else "Fault Detected"
        self.add_product_log(pencil)
        self.update_status_labels()

    def run_auto_cycle(self) -> None:
        if not self.line.running:
            return
        pencil = self.line.produce_one_part()
        self.current_stage = "QC & Packaging" if not pencil.defective else "Fault Detected"
        self.add_product_log(pencil)
        self.update_status_labels()
        if self.line.faulted:
            self.add_log("Fault detected. Automatic cycle stopped.")
            return
        self.auto_job = self.root.after(1200, self.run_auto_cycle)

    def cancel_auto_cycle(self) -> None:
        if self.auto_job is not None:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None

    def update_status_labels(self) -> None:
        status = self.line.get_status()
        status["Current Stage"] = self.current_stage
        for key, label in self.kpi_labels.items():
            label.config(text=status.get(key, "-"))

        state = status.get("Machine State", "IDLE")
        if state == "PRODUCTIVE":
            self.kpi_labels["Machine State"].config(fg=self.YELLOW)
        elif state == "UNSCHEDULED_DOWNTIME":
            self.kpi_labels["Machine State"].config(fg=self.RED)
        else:
            self.kpi_labels["Machine State"].config(fg=self.MUTED)

        if self.latest_error is not None:
            self.latest_error.config(text=f"Latest Error: {status.get('Last Error', 'None')}")

        for name, box in self.stage_labels.items():
            if status.get("Machine State") == "PRODUCTIVE":
                box.config(bg="#243553", fg="#f8fafc", highlightbackground="#5b7bea")
            elif status.get("Machine State") == "UNSCHEDULED_DOWNTIME":
                box.config(bg="#3a2027", fg="#fecaca", highlightbackground=self.RED)
            else:
                box.config(bg=self.CARD, fg=self.WHITE, highlightbackground=self.CARD_BORDER)

    def add_product_log(self, pencil: Pencil) -> None:
        result = "DEFECTIVE" if pencil.defective else "GOOD"
        self.add_log(f"Pencil #{pencil.pencil_id} completed: {result}")
        for entry in pencil.stage_log:
            self.add_log(f"   {entry}")

    def add_log(self, message: str) -> None:
        if self.log_box is not None:
            self.log_box.insert("end", f"{time.strftime('%H:%M:%S')}  {message}\n")
            self.log_box.see("end")

    def clear_log(self) -> None:
        if self.log_box is not None:
            self.log_box.delete("1.0", "end")
