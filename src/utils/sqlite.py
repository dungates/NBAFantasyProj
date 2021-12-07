import sqlite3


def update_data_table(
    table_name, headers, data_rows, primary_keys=None, extra_values=None
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
