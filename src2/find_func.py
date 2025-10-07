import json
import argparse
from pathlib import Path

# Default path
DIR = "/Users/myoungkyu/Documents/0-research-unixcoder"
DEFAULT_PATH = Path(f"{DIR}/GraphCodeBERT/clonedetection/dataset/data.jsonl")

def print_func_by_idx(target_idx, file_path):
    """Print the 'func' field from a JSONL file given an idx value."""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            if str(obj.get("idx")) == str(target_idx):
                print(obj["func"])
                return
    print(f"❌ Index {target_idx} not found in {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Print the 'func' field from data.jsonl by idx.")
    parser.add_argument("idx", help="The idx value to search for.")
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_PATH,
        help=f"Path to data.jsonl file (default: {DEFAULT_PATH})"
    )

    args = parser.parse_args()
    print_func_by_idx(args.idx, args.path)

if __name__ == "__main__":
    main()
