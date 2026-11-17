"""Hàm dùng chung cho các notebook phân cụm: đánh giá, sắp xếp nhãn, độ ổn định, mô tả cụm."""
import time

import numpy as np
import pandas as pd
from sklearn.metrics import (adjusted_rand_score, calinski_harabasz_score,
                             davies_bouldin_score, normalized_mutual_info_score,
                             silhouette_score)


def internal_metrics(X, labels, ignore_noise: bool = True) -> dict:
    """Silhouette (↑), Davies-Bouldin (↓), Calinski-Harabasz (↑).
    Với thuật toán có nhãn nhiễu (-1), mặc định chỉ tính trên các điểm không nhiễu."""
    X = np.asarray(X); labels = np.asarray(labels)
    mask = labels != -1 if ignore_noise else np.ones(len(labels), bool)
    k = len(set(labels[mask]))
    if k < 2:
        return {"Silhouette": np.nan, "Davies-Bouldin": np.nan, "Calinski-Harabasz": np.nan}
    return {
        "Silhouette": silhouette_score(X[mask], labels[mask]),
        "Davies-Bouldin": davies_bouldin_score(X[mask], labels[mask]),
        "Calinski-Harabasz": calinski_harabasz_score(X[mask], labels[mask]),
    }


def timed_fit(make_model, X):
    """Huấn luyện model (fit_predict) và đo thời gian (giây)."""
    t0 = time.perf_counter()
    model = make_model()
    labels = model.fit_predict(X)
    return model, np.asarray(labels), time.perf_counter() - t0


def relabel_by_value(labels, monetary) -> np.ndarray:
    """Đánh lại nhãn cụm theo Monetary trung bình giảm dần (cụm 0 = giá trị cao nhất),
    để các thuật toán có thứ tự nhãn thống nhất, dễ so sánh. Giữ nguyên nhãn nhiễu -1."""
    labels = np.asarray(labels)
    s = pd.Series(np.asarray(monetary)).groupby(labels).mean()
    s = s.drop(index=-1, errors="ignore").sort_values(ascending=False)
    mapping = {old: new for new, old in enumerate(s.index)}
    mapping[-1] = -1
    return np.array([mapping[l] for l in labels])


def bootstrap_stability(make_model, X, ref_labels, n_runs: int = 20, frac: float = 0.8, seed: int = 0):
    """Độ ổn định: huấn luyện lại trên n_runs mẫu con (frac dữ liệu, không hoàn lại),
    so sánh nhãn mới với nhãn trên toàn bộ dữ liệu (trên cùng các điểm) bằng ARI.
    ARI ≈ 1: cấu trúc cụm ổn định; ARI thấp: kết quả phụ thuộc mạnh vào mẫu."""
    X = np.asarray(X); rng = np.random.default_rng(seed); scores = []
    for _ in range(n_runs):
        idx = rng.choice(len(X), int(frac * len(X)), replace=False)
        lab = make_model().fit_predict(X[idx])
        scores.append(adjusted_rand_score(ref_labels[idx], lab))
    return float(np.mean(scores)), float(np.std(scores))


def agreement(a, b) -> dict:
    return {"ARI": adjusted_rand_score(a, b), "NMI": normalized_mutual_info_score(a, b)}


def profile(rfm: pd.DataFrame, labels, cols=("Recency", "Frequency", "Monetary")) -> pd.DataFrame:
    """Hồ sơ cụm: số khách, % khách, trung vị R/F/M, % doanh thu."""
    d = rfm.assign(Cluster=labels)
    p = d.groupby("Cluster").agg(**{"Số khách": ("Recency", "size")},
                                 **{f"{c} (trung vị)": (c, "median") for c in cols},
                                 **{"Monetary TB": ("Monetary", "mean"), "Tổng Monetary": ("Monetary", "sum")})
    p["% khách"] = 100 * p["Số khách"] / p["Số khách"].sum()
    p["% doanh thu"] = 100 * p["Tổng Monetary"] / p["Tổng Monetary"].sum()
    return p.drop(columns="Tổng Monetary")


def name_clusters(X_scaled: pd.DataFrame, labels) -> dict:
    """Gán tên phân khúc theo vị trí tâm cụm trong không gian đã chuẩn hóa (z-score):
    - Recency: R_s < -0,5 = mua gần đây; R_s > 0,5 = lâu không mua; còn lại = trung bình
    - Giá trị: trung bình (F_s + M_s)/2; > 0,8 = rất cao, > 0 = trên trung bình"""
    d = X_scaled.assign(Cluster=labels)
    d = d[d["Cluster"] != -1].groupby("Cluster").mean()
    names = {}
    for c, row in d.iterrows():
        r = row["Recency_s"]
        value = (row["Frequency_s"] + row["Monetary_s"]) / 2
        recent, inactive = r < -0.5, r > 0.5          # |z| > 0,5: lệch rõ so với trung bình
        if recent and value > 0.8:
            n = "Champions (VIP)"
        elif recent and value > 0:
            n = "Trung thành"
        elif recent:
            n = "Khách mới"
        elif inactive and value > 0:
            n = "Có nguy cơ rời bỏ"
        elif inactive:
            n = "Ngủ đông / Rời bỏ"
        elif value > 0:
            n = "Trung thành – cần chăm sóc"
        else:
            n = "Cần quan tâm"
        names[c] = n
    # nếu trùng tên, thêm hậu tố theo thứ tự cụm
    seen = {}
    for c in sorted(names):
        seen[names[c]] = seen.get(names[c], 0) + 1
        if list(names.values()).count(names[c]) > 1:
            names[c] = f"{names[c]} ({seen[names[c]]})"
    if -1 in set(np.asarray(labels)):
        names[-1] = "Nhiễu"
    return names
