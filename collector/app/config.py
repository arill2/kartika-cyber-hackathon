import os


def _int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, "").strip() or default)
    except ValueError:
        return default


class Config:
    HOST = os.getenv("POLARIS_HOST", "127.0.0.1")
    PORT = _int("POLARIS_BIND_PORT", 8787)
    TOKEN = os.getenv("POLARIS_TOKEN", "polaris-dev-token")
    DB_PATH = os.getenv("POLARIS_DB", os.path.join(os.path.expanduser("~"), ".polaris", "polaris.db"))

    # korelasi & skoring
    CORR_WINDOW_SEC = _int("POLARIS_CORR_WINDOW_SEC", 900)   # jendela penggabungan incident
    FP_WINDOW_SEC = _int("POLARIS_FP_WINDOW_SEC", 60)        # jendela fingerprinting pola

    # alert channels
    TELEGRAM_TOKEN = os.getenv("POLARIS_TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT = os.getenv("POLARIS_TELEGRAM_CHAT", "")
    WEBHOOK_URL = os.getenv("POLARIS_WEBHOOK_URL", "")

    # AI summarizer opsional
    OPENAI_API_KEY = os.getenv("POLARIS_OPENAI_API_KEY", "")

    # --- Pengurangan noise terukur (auditable) -------------------------------
    # IP yang dianggap infrastruktur tepercaya (mis. host monitoring). Kosong by default.
    ALLOWLIST_IPS = [x.strip() for x in os.getenv("POLARIS_ALLOWLIST_IPS", "").split(",") if x.strip()]

    # Pola aktivitas otomatis yang dikenal jinak (health check / probe internal).
    # Event yang cocok TIDAK dijadikan incident, tetapi tetap dicatat (suppressed)
    # untuk audit -> menjaga klaim zero-FP tetap jujur & dapat diaudit.
    SUPPRESS_PATTERNS = [
        x.strip() for x in os.getenv(
            "POLARIS_SUPPRESS_PATTERNS",
            "/health,kube-probe,ELB-HealthChecker,GoogleHC,Consul-Health,"
            "blackbox_exporter,traceparent,x-b3-,nginx-ingress-healthcheck",
        ).split(",") if x.strip()
    ]

    # ambang deteksi brute force (jumlah koneksi SSH dalam jendela fingerprint)
    BRUTEFORCE_MIN = _int("POLARIS_BRUTEFORCE_MIN", 3)

    @classmethod
    def telegram_enabled(cls) -> bool:
        return bool(cls.TELEGRAM_TOKEN and cls.TELEGRAM_CHAT)


cfg = Config()
