import jaydebeapi
import argparse
import os
import sys

def display_function_code(file_path, start_line, end_line):
    """
    Reads a file and prints the lines between start_line and end_line.
    """
    try:
        # Use error handling for different file encodings
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Adjust for 0-based indexing (file lines are 1-based)
        start_index = start_line - 1
        end_index = end_line

        if start_index < 0 or end_index > len(lines):
            print(f"Error: Line numbers ({start_line}-{end_line}) are out of range for file {file_path}.")
            return

        print("-" * 60)
        print(f"Displaying: {os.path.basename(file_path)} (Lines {start_line}-{end_line})")
        print("-" * 60)
        
        for i in range(start_index, end_index):
            # Prepend line number for context
            print(f"{i+1:4d}| {lines[i].rstrip()}")
        print("-" * 60 + "\n")

    except FileNotFoundError:
        print(f"\nError: Source code file not found at '{file_path}'")
    except Exception as e:
        print(f"\nAn error occurred while reading the file: {e}")


def query_bigclonebench(function_ids, project_root):
    """
    Connects to the BigCloneBench H2 database and queries for information
    about a specific function or a specific clone pair.

    Args:
        function_ids (list[int]): A list containing one or two function IDs.
        project_root (str): The absolute path to the BigCloneEval project root.
    """
    # --- 1. Define Paths ---
    h2_jar_path = os.path.join(project_root, "libs", "h2-1.3.176.jar")
    db_path = os.path.join(project_root, "bigclonebenchdb", "BigCloneBench_BCEvalVersion", "bcb")
    jdbc_url = f"jdbc:h2:file:{db_path}"

    if not os.path.exists(h2_jar_path):
        print(f"Error: H2 JAR not found at '{h2_jar_path}'")
        sys.exit(1)
    if not os.path.exists(f"{db_path}.h2.db") and not os.path.exists(f"{db_path}.mv.db"):
         print(f"Error: Database file not found for prefix '{db_path}'")
         sys.exit(1)

    conn = None
    try:
        # --- 2. Establish Connection ---
        print("Connecting to the database...")
        conn = jaydebeapi.connect(
            "org.h2.Driver",
            jdbc_url,
            ["sa", ""],
            jars=[h2_jar_path]
        )
        print("Connection successful.\n")
        curs = conn.cursor()

        # --- 3. Query based on number of IDs ---
        if len(function_ids) == 1:
            # --- Logic for a single function ID ---
            function_id = function_ids[0]
            print(f"--- Querying for Function ID: {function_id} ---")
            query_func = "SELECT * FROM FUNCTIONS WHERE ID = ?"
            curs.execute(query_func, (function_id,))
            func_column_names = [desc[0] for desc in curs.description] # Store function columns
            results_func = curs.fetchall()

            if results_func:
                print("Function Details:")
                header = "  ".join(f"{name:<18}" for name in func_column_names)
                separator = "-" * len(header)
                print(header)
                print(separator)
                for row in results_func:
                    formatted_row = "  ".join(f"{str(item):<18}" for item in row)
                    print(formatted_row)
            else:
                print("No function found with that ID.")

            print("\n" + "="*len(header) + "\n")

            print(f"--- Querying for all Clone Pairs involving Function ID: {function_id} ---")
            query_clones = """
                SELECT *
                FROM CLONES
                WHERE FUNCTION_ID_ONE = ? OR FUNCTION_ID_TWO = ?
            """
            curs.execute(query_clones, (function_id, function_id))
            results_clones = curs.fetchall()
            
            if results_clones:
                print("Found Clone Pairs:")
                clone_column_names = [desc[0] for desc in curs.description]
                header = "  ".join(f"{name:<18}" for name in clone_column_names)
                separator = "-" * len(header)
                print(header)
                print(separator)
                for row in results_clones:
                    formatted_row = "  ".join(f"{str(item):<18}" for item in row)
                    print(formatted_row)
            else:
                print("No clone pairs found for that function ID.")

        elif len(function_ids) == 2:
            # --- Logic for two function IDs ---
            id_one, id_two = function_ids[0], function_ids[1]
            print(f"--- Querying for details of Functions {id_one} and {id_two} ---")
            query_func = "SELECT * FROM FUNCTIONS WHERE ID = ? OR ID = ?"
            curs.execute(query_func, (id_one, id_two))
            func_column_names = [desc[0] for desc in curs.description] # Store function columns
            results_func = curs.fetchall()
            
            header_len = 95 # Default width
            if results_func:
                print("Function Details:")
                header = "  ".join(f"{name:<18}" for name in func_column_names)
                separator = "-" * len(header)
                header_len = len(header)
                print(header)
                print(separator)
                for row in results_func:
                    formatted_row = "  ".join(f"{str(item):<18}" for item in row)
                    print(formatted_row)
            else:
                print("One or both functions not found.")
            
            print("\n" + "="*header_len + "\n")

            print(f"--- Querying for specific Clone Pair between {id_one} and {id_two} ---")
            query_clones = """
                SELECT *
                FROM CLONES
                WHERE (FUNCTION_ID_ONE = ? AND FUNCTION_ID_TWO = ?) OR (FUNCTION_ID_ONE = ? AND FUNCTION_ID_TWO = ?)
            """
            curs.execute(query_clones, (id_one, id_two, id_two, id_one))
            clone_column_names = [desc[0] for desc in curs.description] # Store clone columns
            results_clones = curs.fetchall()
            
            if results_clones:
                print("Found Clone Pair:")
                header = "  ".join(f"{name:<18}" for name in clone_column_names)
                separator = "-" * len(header)
                header_len = len(header)
                print(header)
                print(separator)
                for row in results_clones:
                    formatted_row = "  ".join(f"{str(item):<18}" for item in row)
                    print(formatted_row)
            else:
                print("No direct clone pair found between the two specified functions.")
            
            # --- Display the source code for both functions ---
            if results_func and results_clones:
                print("\n" + "="*header_len + "\n")
                print("--- Displaying Source Code ---")

                try:
                    functionality_id_index = clone_column_names.index("FUNCTIONALITY_ID")
                    functionality_id = results_clones[0][functionality_id_index]

                    id_idx = func_column_names.index("ID")
                    name_idx = func_column_names.index("NAME")
                    type_idx = func_column_names.index("TYPE")
                    start_idx = func_column_names.index("STARTLINE")
                    end_idx = func_column_names.index("ENDLINE")

                    func_details_map = {row[id_idx]: row for row in results_func}

                    for func_id in function_ids:
                        if func_id in func_details_map:
                            details = func_details_map[func_id]
                            file_name = details[name_idx]
                            file_type = details[type_idx]
                            start_line = details[start_idx]
                            end_line = details[end_idx]

                            file_path = os.path.join(project_root, "ijadataset", "dataset",
                                                     file_type, file_name)
                            
                            display_function_code(file_path, start_line, end_line)
                        else:
                            print(f"Could not find details for function ID {func_id} to display its source.")
                except ValueError as e:
                    print(f"Error: Could not find a required column to locate source files: {e}")


    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Query BigCloneBench for function and clone pair details.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "function_ids",
        type=int,
        nargs='+', # Accept one or more arguments
        help="One or two function IDs to look up."
    )
    parser.add_argument(
        "--path",
        type=str,
        default=os.getcwd(),
        help="The absolute path to the BigCloneEval project root directory.\nDefaults to the current working directory."
    )
    args = parser.parse_args()
    
    if len(args.function_ids) > 2:
        print("Error: Please provide either one or two function IDs.")
        sys.exit(1)

    # Verify the provided path looks like a BigCloneEval directory
    if not os.path.isdir(os.path.join(args.path, "bigclonebenchdb")):
         print(f"Error: The path '{args.path}' does not appear to be the BigCloneEval root directory.")
         print("Please provide the correct path using the --path argument.")
         sys.exit(1)

    query_bigclonebench(args.function_ids, args.path)

