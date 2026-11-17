"""Thiết lập style biểu đồ thống nhất cho báo cáo (matplotlib/seaborn)."""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl

FIG_DIR = Path(__file__).resolve().parents[1] / "figures"
FIG_DIR.mkdir(exist_ok=True)

# Bảng màu phân loại (thứ tự cố định, đã kiểm tra phân biệt được với người mù màu)
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
MAIN = PALETTE[0]
ACCENT = PALETTE[1]
GREY = "#a9a8a2"
INK = "#0b0b0b"
INK2 = "#52514e"
SEQ_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "blue_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"])
DIV_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "div", ["#2a78d6", "#f0efec", "#eb6834"])


def setup():
    mpl.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
        "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
        "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6,
        "axes.axisbelow": True, "axes.prop_cycle": mpl.cycler(color=PALETTE),
        "xtick.color": INK2, "ytick.color": INK2, "font.size": 10,
        "lines.linewidth": 2, "legend.frameon": False,
    })


def save(fig, name: str):
    """Lưu hình vào thư mục figures/ để chèn vào báo cáo và slide."""
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path)
    return path
