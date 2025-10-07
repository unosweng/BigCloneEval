#!/usr/bin/env python3
# h2_query.py
#
# pip install jaydebeapi jpype1 tabulate

"""
python find_clone.py \
  --db "/Users/myoungkyu/Documents/0-git-repo/0-research-BigCloneEval/bigclonebenchdb/BigCloneBench_BCEvalVersion/bcb" \
  --jar "/Users/myoungkyu/Documents/0-git-repo/0-research-BigCloneEval/libs/h2-1.3.176.jar" \
  --function-id 80378 \
  --function-id-two 18548122
"""

import argparse
from pathlib import Path
import jaydebeapi

try:
    from tabulate import tabulate
except Exception:
    tabulate = None


def to_h2_file_base(path: Path) -> str:
    """
    H2 'file' URLs want the base path (without the .mv.db / .h2.db suffix).
    Accepts any of:
      /.../bcb
      /.../bcb.mv.db
      /.../bcb.h2.db
    """
    if path.suffix in (".mv.db", ".h2.db"):
        return str(path.with_suffix(""))
    return str(path)


def make_jdbc_url(db_path: Path) -> str:
    base = to_h2_file_base(db_path)
    # Use the simple mode the H2 Console uses.
    # Add options as needed (e.g., ;AUTO_SERVER=TRUE).
    return f"jdbc:h2:file:{base}"


def run_query(conn, sql: str, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or [])
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
    return cols, rows


def print_table(cols, rows, title=None):
    if title:
        print(f"\n=== {title} ===")
    if not rows:
        print("(no rows)")
        return
    if tabulate:
        print(tabulate(rows, headers=cols, tablefmt="github"))
    else:
        # Minimal fallback printer
        print("\t".join(cols))
        for r in rows:
            print("\t".join("" if v is None else str(v) for v in r))


def main():
    p = argparse.ArgumentParser(description="Query an H2 database (file mode) via JDBC.")
    p.add_argument(
        "--db",
        type=Path,
        required=True,
        help="Path to the H2 database file or its base (e.g., .../bcb or .../bcb.mv.db).",
    )
    p.add_argument(
        "--jar",
        type=Path,
        required=True,
        help="Path to h2-*.jar (e.g., libs/h2-1.3.176.jar).",
    )
    p.add_argument(
        "--user", default="sa",
        help="DB user (default: sa)."
    )
    p.add_argument(
        "--password", default="",
        help="DB password (default: empty)."
    )
    # Convenience flags to mirror the screenshot queries
    p.add_argument("--function-id", type=int, help="FUNCTIONS.id to look up.")
    p.add_argument("--function-id-two", type=int, help="CLONES.function_id_two for pair query.")
    p.add_argument(
        "--sql",
        help="Run an arbitrary SQL query instead of the convenience queries."
    )
    args = p.parse_args()

    jdbc_url = make_jdbc_url(args.db)
    driver = "org.h2.Driver"
    jvm_args = []  # extend if you need memory opts, etc.

    # Connect
    conn = jaydebeapi.connect(
        jclassname=driver,
        url=jdbc_url,
        driver_args=[args.user, args.password],
        jars=str(args.jar),
        jvm_options=jvm_args
    )

    try:
        if args.sql:
            cols, rows = run_query(conn, args.sql)
            print_table(cols, rows, "Query")
        else:
            ran_any = False
            if args.function_id is not None:
                q1 = "SELECT * FROM FUNCTIONS WHERE ID = ?"
                cols, rows = run_query(conn, q1, [args.function_id])
                print_table(cols, rows, f"FUNCTIONS (ID={args.function_id})")
                ran_any = True

            if args.function_id is not None and args.function_id_two is not None:
                q2 = """
                SELECT * FROM CLONES
                WHERE FUNCTION_ID_ONE = ? AND FUNCTION_ID_TWO = ?
                """
                cols, rows = run_query(conn, q2, [args.function_id, args.function_id_two])
                print_table(cols, rows, f"CLONES (ONE={args.function_id}, TWO={args.function_id_two})")
                ran_any = True

            if not ran_any:
                # If nothing specified, show a quick peek at tables like the console tree
                for table in ("FUNCTIONS", "CLONES"):
                    try:
                        cols, rows = run_query(conn, f"SELECT * FROM {table} LIMIT 5")
                        print_table(cols, rows, f"{table} (first 5)")
                    except Exception as e:
                        print(f"{table}: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
