import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import settings as s

engine = create_engine(URL.create(
    "postgresql+psycopg",
    username=s.DB_USER,
    password=s.DB_PASSWORD,
    host=s.DB_HOST,
    port=s.DB_PORT,
    database=s.DB_NAME,
))


def loader(df: pd.DataFrame, table_name: str, conn=engine):
    if df.empty:
        print("Bu jadval bo'sh")
        return
    df.to_sql(table_name, conn, if_exists='replace', index=False)








# db_url = f"postgresql://postgres:mdev3112@localhost:5432/amocrm"
# db_url = f"postgresql://postgres:mdev3112@host.docker.internal:5432/amocrm"