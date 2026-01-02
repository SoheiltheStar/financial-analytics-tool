import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional

DB_PATH = Path("data/financial_analytics.duckdb")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))

def init_database():
    con = get_connection()
    con.execute("""
        CREATE TABLE IF NOT EXISTS financial_snapshots (
            id INTEGER PRIMARY KEY,
            month_tag VARCHAR NOT NULL,
            market VARCHAR NOT NULL,
            ledger VARCHAR NOT NULL,
            actual DOUBLE,
            plan DOUBLE,
            forecast DOUBLE,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(month_tag, market, ledger)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS ledger_mapping (
            ledger VARCHAR PRIMARY KEY,
            bucket VARCHAR,
            driver VARCHAR,
            controllable BOOLEAN DEFAULT TRUE
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS column_mapping (
            id INTEGER PRIMARY KEY,
            market_col VARCHAR,
            ledger_col VARCHAR,
            actual_col VARCHAR,
            plan_col VARCHAR,
            forecast_col VARCHAR
        )
    """)
    con.close()

def save_column_mapping(market_col: str, ledger_col: str, actual_col: str, plan_col: str, forecast_col: str):
    con = get_connection()
    con.execute("DELETE FROM column_mapping")
    con.execute("""
        INSERT INTO column_mapping (id, market_col, ledger_col, actual_col, plan_col, forecast_col)
        VALUES (1, ?, ?, ?, ?, ?)
    """, [market_col, ledger_col, actual_col, plan_col, forecast_col])
    con.close()

def get_column_mapping() -> Optional[dict]:
    con = get_connection()
    result = con.execute("SELECT * FROM column_mapping LIMIT 1").fetchone()
    con.close()
    if result:
        return {
            "market_col": result[1],
            "ledger_col": result[2],
            "actual_col": result[3],
            "plan_col": result[4],
            "forecast_col": result[5]
        }
    return None

def save_ledger_mapping(df: pd.DataFrame):
    con = get_connection()
    con.execute("DELETE FROM ledger_mapping")
    for _, row in df.iterrows():
        con.execute("""
            INSERT INTO ledger_mapping (ledger, bucket, driver, controllable)
            VALUES (?, ?, ?, ?)
        """, [row['ledger'], row['bucket'], row['driver'], row['controllable']])
    con.close()

def get_ledger_mapping() -> pd.DataFrame:
    con = get_connection()
    result = con.execute("SELECT * FROM ledger_mapping").fetchdf()
    con.close()
    return result

def save_financial_snapshot(df: pd.DataFrame, month_tag: str, mapping: dict):
    con = get_connection()
    con.execute("DELETE FROM financial_snapshots WHERE month_tag = ?", [month_tag])
    for _, row in df.iterrows():
        con.execute("""
            INSERT INTO financial_snapshots (month_tag, market, ledger, actual, plan, forecast)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            month_tag,
            str(row[mapping['market_col']]),
            str(row[mapping['ledger_col']]),
            float(row[mapping['actual_col']]) if pd.notna(row[mapping['actual_col']]) else 0,
            float(row[mapping['plan_col']]) if pd.notna(row[mapping['plan_col']]) else 0,
            float(row[mapping['forecast_col']]) if pd.notna(row[mapping['forecast_col']]) else 0
        ])
    con.close()

def get_all_snapshots() -> pd.DataFrame:
    con = get_connection()
    result = con.execute("""
        SELECT fs.*, lm.bucket, lm.driver, lm.controllable
        FROM financial_snapshots fs
        LEFT JOIN ledger_mapping lm ON fs.ledger = lm.ledger
        ORDER BY month_tag DESC
    """).fetchdf()
    con.close()
    return result

def get_available_months() -> list:
    con = get_connection()
    result = con.execute("SELECT DISTINCT month_tag FROM financial_snapshots ORDER BY month_tag DESC").fetchall()
    con.close()
    return [r[0] for r in result]

def get_snapshot_by_month(month_tag: str) -> pd.DataFrame:
    con = get_connection()
    result = con.execute("""
        SELECT fs.*, lm.bucket, lm.driver, lm.controllable
        FROM financial_snapshots fs
        LEFT JOIN ledger_mapping lm ON fs.ledger = lm.ledger
        WHERE month_tag = ?
    """, [month_tag]).fetchdf()
    con.close()
    return result

def get_markets() -> list:
    con = get_connection()
    result = con.execute("SELECT DISTINCT market FROM financial_snapshots ORDER BY market").fetchall()
    con.close()
    return [r[0] for r in result]

