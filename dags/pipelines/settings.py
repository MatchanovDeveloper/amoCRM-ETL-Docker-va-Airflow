import os

# ===== SHU YERNI O'ZINGIZ TO'LDIRASIZ =====
AMO_SUBDOMAIN = os.getenv("AMO_SUBDOMAIN", "matchanovmatchanboy1")
AMO_LONG_TOKEN = os.getenv("AMO_LONG_TOKEN", "")


DB_USER = os.getenv("PG_USER", "postgres")   #database logini
DB_PASSWORD = os.getenv("PG_PASSWORD", "")
DB_NAME = os.getenv("PG_NAME", "amocrm")
DB_PORT = int(os.getenv("PG_PORT", "5432"))
DB_HOST = os.getenv("PG_HOST", "auto")



# ===== BU YERDAN PASTGA TEGMANG =====

# Docker ichidami yoki Windows'dami, shuni aniqlaydi
IN_DOCKER = os.path.exists("/.dockerenv")

if DB_HOST == "auto":
    DB_HOST = "host.docker.internal" if IN_DOCKER else "localhost"

# Token fayllari papkasi: Docker'da ulangan papka, lokalda loyiha ildizi
if IN_DOCKER:
    TOKENS_DIR = "/opt/airflow/amo"
else:
    TOKENS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
