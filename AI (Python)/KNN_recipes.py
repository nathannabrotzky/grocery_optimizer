import json
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
import nltk

nltk.download("punkt")
nltk.download("stopwords")

# === Load and clean data ===
with open(r"C:\Users\nabro\Desktop\Portfolio Projects\grocery_optimizer\ETL (Python)\recipes.jsonl", "r", encoding="utf-8") as f:
    lines = [json.loads(line) for line in f]

df = pd.DataFrame(lines)
df = df.dropna(subset=["title", "ingredients"])

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

df["ingredients_clean"] = df["ingredients"].apply(clean_text)

# === Vectorize ingredients ===
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(df["ingredients_clean"])

# === Compute similarity and cluster ===
similarity = cosine_similarity(X)
clustering = AgglomerativeClustering(n_clusters=500, metric="precomputed", linkage="average")
labels = clustering.fit_predict(1 - similarity)
df["group_id"] = [f"group_{i}" for i in labels]

# === Output as JSONL ===
output_fields = ["title", "url", "ingredients", "details", "quantity", "group_id"]
with open("recipes_knn.jsonl", "w", encoding="utf-8") as f:
    for _, row in df[output_fields].iterrows():
        f.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")