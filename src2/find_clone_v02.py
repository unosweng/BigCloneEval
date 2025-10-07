# find_clone.py
import argparse
import os
from pathlib import Path
import jpype
import jpype.imports
import jaydebeapi
from tabulate import tabulate

def jvm_path_from_java_home():
    # Works on macOS JDK 17+
    java_home = os.environ.get("JAVA_HOME")
    if not java_home:
        raise RuntimeError("JAVA_HOME is not set")
    # Prefer libjli.dylib (launcher) if present, else libjvm.dylib
    p1 = Path(java_home) / "lib" / "jli" / "libjli.dylib"
    p2 = Path(java_home) / "jre" / "lib" / "server" / "libjvm.dylib"
    p3 = Path(java_home) / "lib" / "server" / "libjvm.dylib"
    for p in (p1, p2, p3):
        if p.exists():
            return str(p)
    # Fallback to JPype’s detector
    return jpype.getDefaultJVMPath()

def start_jvm_with_jar(h2_jar: Path):
    if not jpype.isJVMStarted():
        jvm_path = jvm_path_from_java_home()
        # Add H2 jar to classpath
        jpype.startJVM(jvm_path, f"-Djava.class.path={h2_jar}")

def run_query(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or [])
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
    return cols, rows

def print_table(cols, rows, title=None):
    if title:
        print(f"\n=== {title} ===")
    if rows:
        print(tabulate(rows, headers=cols, tablefmt="github"))
    else:
        print("(no rows)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, required=True,
                    help="H2 db base or file path (…/bcb or …/bcb.mv.db)")
    ap.add_argument("--jar", type=Path, required=True,
                    help="Path to h2-*.jar (e.g., h2-1.3.176.jar)")
    ap.add_argument("--user", default="sa")
    ap.add_argument("--password", default="")
    ap.add_argument("--function-id", type=int)
    ap.add_argument("--function-id-two", type=int)
    ap.add_argument("--sql")
    args = ap.parse_args()

    # Normalize the H2 file URL
    base = str(args.db.with_suffix("")) if args.db.suffix in (".mv.db", ".h2.db") else str(args.db)
    jdbc_url = f"jdbc:h2:file:{base}"

    # 1) Start JVM with your JDK 17 and the H2 jar on the classpath
    start_jvm_with_jar(args.jar)

    # 2) Connect (no jars=, JVM already started)
    conn = jaydebeapi.connect("org.h2.Driver", jdbc_url, [args.user, args.password])

    try:
        if args.sql:
            cols, rows = run_query(conn, args.sql)
            print_table(cols, rows, "Query")
        else:
            ran = False
            if args.function_id is not None:
                cols, rows = run_query(conn, "SELECT * FROM FUNCTIONS WHERE ID = ?", [args.function_id])
                print_table(cols, rows, f"FUNCTIONS (ID={args.function_id})")
                ran = True
            if args.function_id is not None and args.function_id_two is not None:
                sql = """SELECT * FROM CLONES
                         WHERE FUNCTION_ID_ONE = ? AND FUNCTION_ID_TWO = ?"""
                cols, rows = run_query(conn, sql, [args.function_id, args.function_id_two])
                print_table(cols, rows, f"CLONES (ONE={args.function_id}, TWO={args.function_id_two})")
                ran = True
            if not ran:
                for t in ("FUNCTIONS", "CLONES"):
                    try:
                        cols, rows = run_query(conn, f"SELECT * FROM {t} LIMIT 5")
                        print_table(cols, rows, f"{t} (first 5)")
                    except Exception as e:
                        print(f"{t}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
