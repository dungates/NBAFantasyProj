import sqlite3
from typing import Any, Dict, List, Tuple


def update_data_table(
    table_name: str,
    headers: List[str],
    data_rows: List[List[Any]],
    primary_keys: List[str] | None = None,
    extra_values: List[Tuple[str, Any]] | None = None,
):
    extra_headers = (
        list(map(lambda entry: entry[0], extra_values)) if extra_values else []
    )
    headers_list = extra_headers + headers
    pk_list = [f"PRIMARY KEY ({','.join(primary_keys)})"] if primary_keys else []
    schema = ",".join(headers_list + pk_list)

    con = sqlite3.connect("nba.db")
    cur = con.cursor()

    cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});")

    qmarks = ",".join(["?"] * len(headers_list))
    extra_data = list(map(lambda entry: entry[1], extra_values)) if extra_values else []
    data_tuples = list(map(lambda row: tuple(extra_data + row), data_rows))

    cur.executemany(f"REPLACE INTO {table_name} VALUES ({qmarks});", data_tuples)

    con.commit()
    con.close()


def update_data_table_from_dicts(
    table_name: str,
    data_dicts: List[Dict[str, Any]],
    primary_keys: List[str] | None = None,
    extra_values: List[Tuple[str, Any]] | None = None,
):
    headers = list(data_dicts[0].keys())
    data_rows = list(map(lambda game: list(game.values()), data_dicts))
    update_data_table(table_name, headers, data_rows, primary_keys, extra_values)
