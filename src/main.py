import tkinter as tk
from hmi import ProductionLineHMI


def main() -> None:
    root = tk.Tk()
    ProductionLineHMI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
