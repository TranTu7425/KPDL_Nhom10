# Phân khúc khách hàng TMĐT dựa trên RFM kết hợp các thuật toán phân cụm – Online Retail II

Bài tập lớn môn Khai phá dữ liệu – Trường CNTT Phenikaa.

## 1. Dữ liệu
- Nguồn: UCI Machine Learning Repository – *Online Retail II* (id 502): https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Phạm vi sử dụng: sheet **Year 2010-2011** (01/12/2010 – 09/12/2011), 541.910 dòng, 8 thuộc tính.
- Đặt file vào: `data/online_retail_II.xlsx`. Nếu tải từ UCI về bản có 2 sheet, cần dùng sheet "Year 2010-2011".

## 2. Cài đặt
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Thứ tự chạy
Chạy các notebook trong thư mục `notebooks/` theo thứ tự (mở bằng Jupyter/VS Code, chọn *Run All*):

| Notebook | Nội dung | Đầu ra |
|---|---|---|
| `01_EDA.ipynb` | Phân tích khám phá: kích thước, thuộc tính, dữ liệu thiếu, trùng lặp, ngoại lệ, thời gian, quốc gia, sản phẩm, khách hàng | `figures/fig01–fig08` |
| `02_preprocessing_RFM.ipynb` | Làm sạch, tính RFM và đặc trưng mở rộng, xử lý phân phối, chuẩn hóa, baseline RFM scoring | `outputs/*`, `figures/fig09–fig14` |
| `03_clustering_classic.ipynb` | K-Means, Hierarchical (Ward + so sánh linkage), GMM (BIC, reg_covar); so sánh chỉ số, độ ổn định, ARI, hồ sơ cụm; thử nghiệm RFM 6 chiều | `figures/fig15–fig25`, `outputs/*classic*`, `scan_*.csv` |
| `04_clustering_modern.ipynb` | DBSCAN, HDBSCAN (+ DBCV, GLOSH, thí nghiệm khử rời rạc), UMAP + HDBSCAN/K-Means, Autoencoder + K-Means; bảng so sánh 8 phương pháp | `figures/fig26–fig32`, `outputs/labels_modern.csv`, `metrics_all.csv` |
| `05_evaluation_comparison.ipynb` | So sánh, diễn giải phân khúc | *(đang thực hiện)* |

Lần chạy đầu, `01_EDA` đọc file Excel (~20 giây) và tạo cache `data/online_retail_II_raw.parquet`; các lần sau chỉ mất khoảng 1 giây.

## 4. Cấu trúc thư mục
```
data/        dữ liệu gốc (+ cache parquet)
notebooks/   notebook thực nghiệm
src/         data_utils.py (làm sạch, RFM), modern.py (UMAP/Autoencoder pipeline), cluster_utils.py (đánh giá, ổn định, hồ sơ cụm), viz.py (style biểu đồ)
figures/     hình xuất cho báo cáo/slide
outputs/     dữ liệu sạch, đặc trưng RFM, ma trận đầu vào mô hình
```

## 5. Các file trong outputs/
| File | Mô tả |
|---|---|
| `cleaning_log.csv` | Số dòng sau từng bước làm sạch |
| `clean_transactions.parquet` | 391.150 giao dịch mua hợp lệ |
| `rfm_features.csv` | 4.320 khách × (Recency, Frequency, Monetary, Tenure, AOV, NumProducts, ReturnRate, …) – giá trị gốc |
| `rfm_model_input.csv` | Đầu vào chính: `Recency_s, Frequency_s, Monetary_s` (log1p + z-score) |
| `rfm_ext_input.csv` | Đầu vào mở rộng 6 chiều: R, F, M, Tenure, AOV, NumProducts (Yeo-Johnson + chuẩn hóa) |
| `rfm_scores.csv` | Điểm R, F, M (1–5) và phân khúc baseline theo quy tắc |
| `labels_classic.csv` | Nhãn cụm của K-Means, Agglomerative, GMM (+ xác suất lớn nhất của GMM) |
| `metrics_classic.csv` | Bảng so sánh chỉ số 3 thuật toán tại K = 4 |
| `profiles_classic.csv` | Hồ sơ cụm (trung vị R/F/M, % khách, % doanh thu) |
| `scan_kmeans.csv`, `scan_hierarchical.csv`, `scan_gmm.csv` | Kết quả khảo sát K = 2–10 |
| `labels_modern.csv` | Nhãn của DBSCAN, HDBSCAN, UMAP+HDBSCAN, UMAP+K-Means, Autoencoder+K-Means (−1 = nhiễu) và điểm GLOSH |
| `metrics_all.csv` | Bảng so sánh tổng hợp 8 phương pháp (cổ điển + hiện đại) |

> Lưu ý: `04_clustering_modern.ipynb` chạy khoảng 3 phút (UMAP và đánh giá độ ổn định). Lần chạy UMAP đầu tiên chậm hơn do numba biên dịch.
