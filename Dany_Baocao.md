# Dàn ý chi tiết báo cáo BTL – Phân khúc khách hàng RFM + phân cụm (Online Retail II)
 
Mục tiêu độ dài: ~45–55 trang (không tính phụ lục). Hình fig01–fig32 nằm trong figures/; số liệu trong outputs/ và claude/ke-hoach-bao-cao-RFM.md.
 
## Phần đầu
Bìa (Phenikaa, môn Khai phá dữ liệu, tên đề tài, GVHD, 2 SV + MSV, lớp tín chỉ, Hà Nội tháng ../2026) · Bảng phân công · Lời mở đầu · Lời cảm ơn · Mục lục · Danh mục hình · Danh mục bảng · Danh mục từ viết tắt (RFM, EDA, KDD, CRISP-DM, GMM, EM, BIC, HDBSCAN, DBSCAN, UMAP, AE, ARI, NMI, DB, CH, DBCV, GLOSH, AOV).
 
## Chương 1. Tổng quan đề tài (3–4 tr)
1.1 Lý do chọn đề tài · 1.2 Mục tiêu (4 mục tiêu) · 1.3 Đối tượng & phạm vi (sheet 2010–2011, 4.320 KH, chỉ RFM hành vi) · 1.4 Phương pháp (CRISP-DM, sơ đồ pipeline) · 1.5 Đóng góp · 1.6 Bố cục.
 
## Chương 2. Cơ sở lý thuyết (10–12 tr)
2.1 KPDL & quy trình KDD/CRISP-DM · 2.2 Phân khúc khách hàng & RFM (định nghĩa, scoring ngũ phân vị, biến thể RFMT/LRFM) · 2.3 Bài toán phân cụm & tiền xử lý (khoảng cách, log/Yeo-Johnson, z-score) · 2.4 Thuật toán cổ điển: K-Means(++), Agglomerative (4 linkage, Ward), GMM/EM/BIC/reg_covar · 2.5 Thuật toán hiện đại: DBSCAN, HDBSCAN (mreach, MST, condensed tree, stability, GLOSH), UMAP, Autoencoder/DEC · 2.6 Chỉ số đánh giá: Silhouette, DB, CH, DBCV, ARI, NMI, bootstrap stability · 2.7 Nghiên cứu liên quan (Chen, Sain & Guo 2012 + 2–4 bài gần đây) · 2.8 Công cụ.
 
## Chương 3. Mô tả & phân tích dữ liệu (6–8 tr) – notebook 01
3.1 Nguồn (UCI 502) · 3.2 Kích thước & thuộc tính (bảng 8 cột) · 3.3 Thống kê mô tả · 3.4 Thiếu & trùng (fig01) · 3.5 Bất thường: hủy, Price≤0, mã phi SP, cặp mua–hủy · 3.6 Phân phối & ngoại lệ (fig02) · 3.7 Thời gian (fig03, fig04) · 3.8 Quốc gia (fig05) · 3.9 Sản phẩm (fig06) · 3.10 Khách hàng, Pareto (fig07, fig08) · 3.11 Bảng tổng hợp vấn đề → quyết định.
 
## Chương 4. Tiền xử lý & xây dựng đặc trưng (5–6 tr) – notebook 02
4.1 Pipeline làm sạch (bảng cleaning_log, fig09) · 4.2 Định nghĩa RFM + mở rộng, Monetary ròng, loại 14 KH · 4.3 Ngoại lệ cấp KH (fig10), không loại · 4.4 Biến đổi phân phối (bảng skew, fig11) · 4.5 Chuẩn hóa, tương quan, PCA (fig12, fig13) · 4.6 Baseline RFM scoring (fig14).
 
## Chương 5. Áp dụng thuật toán & thực nghiệm (10–12 tr) – notebook 03, 04
5.1 Thiết lập (dữ liệu, seed, K 2–10, nguyên tắc so sánh công bằng) · 5.2 K-Means (fig15, fig16, tâm cụm) · 5.3 Agglomerative (fig17, fig18, bảng linkage) · 5.4 GMM (suy biến fig19, BIC fig20, posterior fig21) · 5.5 DBSCAN (fig26) · 5.6 HDBSCAN (bảng tham số, DBCV, fig27, fig28, khử rời rạc fig29, GLOSH) · 5.7 UMAP + clustering (fig30) · 5.8 Autoencoder + K-Means (fig31) · 5.9 Thử nghiệm RFM 6 chiều.
 
## Chương 6. Đánh giá, so sánh & thảo luận (6–8 tr)
6.1 Bảng tổng hợp 8 phương pháp (metrics_all, fig32) · 6.2 So sánh trong nhóm cổ điển (fig22, fig23) · 6.3 Phân tích khác biệt cổ điển vs hiện đại (4 luận điểm) · 6.4 So sánh với baseline & nghiên cứu liên quan (fig25) · 6.5 Diễn giải 4 phân khúc + chiến lược (fig24, bảng hồ sơ) · 6.6 Ứng dụng GLOSH · 6.7 Mối đe dọa tính hợp lệ.
 
## Chương 7. Kết luận (2–3 tr)
7.1 Kết quả đạt được · 7.2 Hạn chế · 7.3 Hướng phát triển.
 
## Tài liệu tham khảo (IEEE) & Phụ lục (README, cấu trúc mã, bảng scan, link GitHub/Drive).
 
## Gợi ý chia việc 2 người
SV A: Ch1, Ch3, Ch4, phần 2.1–2.3 + K-Means/Ward/GMM lý thuyết, notebook 01–03. SV B: Ch2.5–2.7, Ch5.5–5.9, Ch6, Ch7, notebook 04. Cả hai: rà soát chéo, slide.
 