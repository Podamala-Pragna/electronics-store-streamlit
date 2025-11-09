import os
import pandas as pd
import mysql.connector as mysql
from dotenv import load_dotenv   # <- correct import

load_dotenv()

CFG = dict(
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DB", "ElectronicsStore"),
)

def get_conn():
    return mysql.connect(**CFG)

def query_df(sql: str, params: tuple | None = None) -> pd.DataFrame:
    """Return a pandas DataFrame for a SELECT."""
    cn = get_conn()
    try:
        return pd.read_sql(sql, cn, params=params)
    finally:
        cn.close()

def execute(sql: str, params: tuple | None = None) -> int:
    """Execute INSERT/UPDATE/DELETE and return affected row count."""
    cn = get_conn()
    try:
        cur = cn.cursor()
        cur.execute(sql, params or ())
        cn.commit()
        return cur.rowcount
    finally:
        cn.close()

def execute_many(sql: str, rows: list[tuple]):
    """Batch execute with executemany."""
    cn = get_conn()
    try:
        cur = cn.cursor()
        cur.executemany(sql, rows)
        cn.commit()
    finally:
        cn.close()

def call_proc(name: str, args: tuple = ()):
    """
    Call a stored procedure and return the first result set (if any) as DataFrame.
    """
    cn = get_conn()
    try:
        cur = cn.cursor()
        cur.callproc(name, args)
        for result in cur.stored_results():
            rows = result.fetchall()
            cols = [d[0] for d in result.description]
            return pd.DataFrame(rows, columns=cols)
        return pd.DataFrame()
    finally:
        cn.close()
