import json
import pandas as pd

# === Load clustered data ===
INPUT_FILE = "ingredients_knn.jsonl"

def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return pd.DataFrame([json.loads(line) for line in f])

def query_group(df, group_id):
    group = df[df["group_id"] == group_id]
    if group.empty:
        print(f"❌ No entries found for group_id: {group_id}")
    else:
        print(f"✅ Found {len(group)} entries in {group_id}:\n")
        for _, row in group.iterrows():
            print(f"- {row.get('title', '[No title]')} | {row.get('price', '')} | {row.get('quantity', '')}")

# === Run query ===
if __name__ == "__main__":
    df = load_data(INPUT_FILE)
    while True:
        group_id = input("\nEnter a group_id to view its members (or type 'exit' to quit): ").strip()
        if group_id.lower() == "exit":
            break
        query_group(df, group_id)