import json

INPUT_FILE = "scraped_products.jsonl"
OUTPUT_FILE = "scraped_products_deduped.jsonl"

def deduplicate_jsonl(input_path, output_path):
    seen = set()
    unique_entries = []

    with open(input_path, "r", encoding="utf-8") as infile:
        for line in infile:
            try:
                obj = json.loads(line)
                key = json.dumps(obj, sort_keys=True)  # Convert dict to canonical string
                if key not in seen:
                    seen.add(key)
                    unique_entries.append(obj)
            except json.JSONDecodeError as e:
                print(f"⚠️ Skipping invalid JSON line: {e}")

    with open(output_path, "w", encoding="utf-8") as outfile:
        for entry in unique_entries:
            outfile.write(json.dumps(entry) + "\n")

    print(f"✅ Deduplicated: {len(unique_entries)} unique entries written to {output_path}")

if __name__ == "__main__":
    deduplicate_jsonl(INPUT_FILE, OUTPUT_FILE)