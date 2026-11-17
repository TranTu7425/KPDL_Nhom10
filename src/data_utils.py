"""Hàm dùng chung: đọc dữ liệu, làm sạch, tính đặc trưng RFM.

Dùng trong các notebook 01_EDA và 02_preprocessing_RFM (và các notebook phân cụm sau này).
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_XLSX = DATA_DIR / "online_retail_II.xlsx"
RAW_CACHE = DATA_DIR / "online_retail_II_raw.parquet"

# Mã StockCode không phải sản phẩm (phí vận chuyển, phí ngân hàng, điều chỉnh thủ công, ...)
NON_PRODUCT_CODES = {
    "POST", "DOT", "M", "m", "C2", "D", "S", "B", "BANK CHARGES",
    "AMAZONFEE", "CRUK", "PADS",
}


def load_raw(use_cache: bool = True) -> pd.DataFrame:
    """Đọc file Excel gốc; lưu cache parquet để các lần sau đọc nhanh (~1s thay vì ~20s)."""
    if use_cache and RAW_CACHE.exists():
        return pd.read_parquet(RAW_CACHE)
    df = pd.read_excel(
        RAW_XLSX,
        dtype={"Invoice": str, "StockCode": str, "Description": str, "Country": str},
    )
    if use_cache:
        df.to_parquet(RAW_CACHE, index=False)
    return df


def is_non_product(stock_code: pd.Series) -> pd.Series:
    """True nếu StockCode là mã dịch vụ/điều chỉnh, không phải hàng hóa."""
    sc = stock_code.astype(str)
    return sc.isin(NON_PRODUCT_CODES) | sc.str.startswith("gift_0001")


def clean_transactions(df: pd.DataFrame, verbose: bool = True):
    """Pipeline làm sạch cấp giao dịch.

    Trả về (sales, returns, log):
      - sales  : dòng mua hàng hợp lệ (đã có Customer ID, Quantity>0, Price>0, là sản phẩm)
      - returns: dòng hóa đơn hủy/trả hàng (Invoice bắt đầu bằng 'C') của khách có ID
      - log    : bảng số dòng sau mỗi bước (dùng cho báo cáo)
    """
    log = []

    def step(name, frame):
        log.append({"Bước": name, "Số dòng còn lại": len(frame)})

    d = df.copy()
    step("0. Dữ liệu gốc", d)

    d = d.drop_duplicates()
    step("1. Loại dòng trùng lặp hoàn toàn", d)

    d = d.dropna(subset=["Customer ID"])
    d["Customer ID"] = d["Customer ID"].astype(int)
    step("2. Loại dòng thiếu Customer ID", d)

    is_cancel = d["Invoice"].str.startswith("C")
    returns = d[is_cancel].copy()
    d = d[~is_cancel]
    step("3. Tách hóa đơn hủy (Invoice 'C...')", d)

    d = d[(d["Quantity"] > 0) & (d["Price"] > 0)]
    step("4. Loại Quantity <= 0 hoặc Price <= 0", d)

    d = d[~is_non_product(d["StockCode"])]
    returns = returns[~is_non_product(returns["StockCode"])]
    step("5. Loại mã không phải sản phẩm (POST, M, ...)", d)

    d["TotalPrice"] = d["Quantity"] * d["Price"]
    returns["TotalPrice"] = returns["Quantity"] * returns["Price"]  # giá trị âm

    log = pd.DataFrame(log)
    log["Số dòng bị loại"] = (-log["Số dòng còn lại"].diff()).fillna(0).astype(int)
    log["% còn lại so với gốc"] = (100 * log["Số dòng còn lại"] / len(df)).round(2)
    if verbose:
        print(log.to_string(index=False))
    return d.reset_index(drop=True), returns.reset_index(drop=True), log


def build_rfm(sales: pd.DataFrame, returns: pd.DataFrame, snapshot=None) -> pd.DataFrame:
    """Tính RFM và các đặc trưng mở rộng cho từng khách hàng.

    - Recency   : số ngày từ lần mua cuối đến ngày tham chiếu (snapshot = ngày cuối + 1)
    - Frequency : số hóa đơn mua hàng khác nhau
    - Monetary  : doanh thu ròng = tổng tiền mua - tổng tiền hàng trả lại
    - Tenure    : số ngày từ lần mua đầu tiên đến snapshot
    - AOV       : giá trị trung bình mỗi hóa đơn = Monetary / Frequency
    - NumProducts: số mã sản phẩm khác nhau đã mua
    - ReturnRate: tỉ lệ giá trị trả lại / giá trị mua
    """
    if snapshot is None:
        snapshot = sales["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)

    g = sales.groupby("Customer ID")
    rfm = pd.DataFrame({
        "Recency": (snapshot - g["InvoiceDate"].max()).dt.days,
        "Frequency": g["Invoice"].nunique(),
        "GrossMonetary": g["TotalPrice"].sum(),
        "Tenure": (snapshot - g["InvoiceDate"].min()).dt.days,
        "NumProducts": g["StockCode"].nunique(),
        "Country": g["Country"].agg(lambda s: s.mode().iat[0]),
    })
    returned = (-returns.groupby("Customer ID")["TotalPrice"].sum()).rename("ReturnedValue")
    rfm = rfm.join(returned, how="left").fillna({"ReturnedValue": 0.0})
    rfm["Monetary"] = (rfm["GrossMonetary"] - rfm["ReturnedValue"]).round(2)  # làm tròn tránh sai số dấu phẩy động
    rfm["AOV"] = rfm["Monetary"] / rfm["Frequency"]
    rfm["ReturnRate"] = (rfm["ReturnedValue"] / rfm["GrossMonetary"]).clip(0, 1)
    cols = ["Recency", "Frequency", "Monetary", "Tenure", "AOV", "NumProducts",
            "ReturnRate", "GrossMonetary", "ReturnedValue", "Country"]
    return rfm[cols], snapshot


def iqr_bounds(s: pd.Series, k: float = 1.5):
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def outlier_report(frame: pd.DataFrame, cols, k: float = 1.5) -> pd.DataFrame:
    rows = []
    for c in cols:
        lo, hi = iqr_bounds(frame[c], k)
        n = int(((frame[c] < lo) | (frame[c] > hi)).sum())
        rows.append({"Thuộc tính": c, "Q1": frame[c].quantile(.25), "Q3": frame[c].quantile(.75),
                     "Cận dưới": lo, "Cận trên": hi, "Số ngoại lệ": n,
                     "% ngoại lệ": round(100 * n / len(frame), 2),
                     "Skewness": round(frame[c].skew(), 2)})
    return pd.DataFrame(rows)


def rfm_scores(rfm: pd.DataFrame) -> pd.DataFrame:
    """Chấm điểm R, F, M theo ngũ phân vị (1-5) và gán phân khúc theo quy tắc nghiệp vụ.
    Đây là baseline không dùng học máy để so sánh với các thuật toán phân cụm."""
    out = rfm[["Recency", "Frequency", "Monetary"]].copy()
    out["R"] = pd.qcut(out["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    # Frequency có nhiều giá trị trùng -> xếp hạng trước khi chia ngũ phân vị
    out["F"] = pd.qcut(out["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    out["M"] = pd.qcut(out["Monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    out["RFM_Score"] = out["R"].astype(str) + out["F"].astype(str) + out["M"].astype(str)
    fm = (out["F"] + out["M"]) / 2

    def seg(r, f_m):
        if r >= 4 and f_m >= 4:
            return "Champions"
        if r >= 3 and f_m >= 3:
            return "Loyal Customers"
        if r >= 4 and f_m < 3:
            return "New / Promising"
        if r == 3 and f_m < 3:
            return "Need Attention"
        if r <= 2 and f_m >= 3:
            return "At Risk"
        if r == 2 and f_m < 3:
            return "Hibernating"
        return "Lost"

    out["Segment_Rule"] = [seg(r, x) for r, x in zip(out["R"], fm)]
    return out
