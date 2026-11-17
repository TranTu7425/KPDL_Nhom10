"""Các pipeline phân cụm hiện đại, đóng gói dưới dạng có fit_predict() để đánh giá thống nhất
(bao gồm cả đánh giá độ ổn định bằng bootstrap)."""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.neural_network import MLPRegressor


class UMAPCluster:
    """UMAP giảm chiều -> phân cụm trên không gian nhúng (HDBSCAN hoặc K-Means)."""

    def __init__(self, clusterer, n_neighbors=30, min_dist=0.0, n_components=2, random_state=42):
        self.clusterer = clusterer
        self.umap_kw = dict(n_neighbors=n_neighbors, min_dist=min_dist,
                            n_components=n_components, random_state=random_state)

    def fit_predict(self, X):
        import umap
        self.reducer_ = umap.UMAP(**self.umap_kw)
        self.embedding_ = self.reducer_.fit_transform(X)
        self.labels_ = np.asarray(self.clusterer().fit_predict(self.embedding_))
        return self.labels_


class AutoencoderKMeans:
    """Autoencoder (MLP đối xứng, hàm kích hoạt tanh) học biểu diễn nén,
    sau đó K-Means trên không gian ẩn (latent). Đây là dạng đơn giản của deep clustering
    hai giai đoạn (pre-train AE -> cluster), tương tự bước khởi tạo của DEC (Xie et al., 2016)."""

    def __init__(self, n_clusters=4, hidden=(16, 8, 3, 8, 16), random_state=42, max_iter=2000):
        self.n_clusters = n_clusters
        self.hidden = hidden
        self.random_state = random_state
        self.max_iter = max_iter

    def encode(self, X):
        h = np.asarray(X)
        n_enc = len(self.hidden) // 2 + 1          # số lớp từ input tới lớp latent
        for W, b in zip(self.ae_.coefs_[:n_enc], self.ae_.intercepts_[:n_enc]):
            h = np.tanh(h @ W + b)
        return h

    def fit_predict(self, X):
        X = np.asarray(X)
        self.ae_ = MLPRegressor(hidden_layer_sizes=self.hidden, activation="tanh", solver="adam",
                                learning_rate_init=1e-3, alpha=1e-4, max_iter=self.max_iter,
                                early_stopping=True, random_state=self.random_state)
        self.ae_.fit(X, X)                          # mục tiêu = chính đầu vào (tái tạo)
        recon = self.ae_.predict(X)
        self.r2_ = 1 - ((recon - X) ** 2).sum() / ((X - X.mean(0)) ** 2).sum()
        self.latent_ = self.encode(X)
        self.km_ = KMeans(self.n_clusters, n_init=10, random_state=self.random_state)
        self.labels_ = self.km_.fit_predict(self.latent_)
        return self.labels_


def dequantize(rfm, seed=42):
    """Khử rời rạc: cộng nhiễu đều vào biến đếm Frequency (±0,5) và Recency (0..1 ngày)
    để kiểm tra xem cấu trúc mật độ có phải do tính rời rạc gây ra hay không."""
    rng = np.random.default_rng(seed)
    z = rfm[["Recency", "Frequency", "Monetary"]].astype(float).copy()
    z["Frequency"] += rng.uniform(-0.5, 0.5, len(z))
    z["Recency"] += rng.uniform(0, 1, len(z))
    return z
