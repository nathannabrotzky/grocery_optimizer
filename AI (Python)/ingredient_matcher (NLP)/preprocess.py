import re
import unicodedata
from typing import List
import json
from nltk.stem import WordNetLemmatizer
import nltk
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

# Common units and descriptors to remove
UNITS = [
    "teaspoon", "tablespoon", "cup", "ounce", "fluid ounce", "pound", "pinch", "dash", "jigger",
    "can", "bottle", "package", "envelope", "slice", "stalk", "large", "small", "tablespoons",
    "teaspoons", "pounds", "cups", "cans", "bunch", "fluid ounces", "ounces", "gallons",
    "bag", "whole", "bottles", "slices", "dashes", "packages", "container"
]
DESCRIPTORS = [
    "chopped", "fresh", "ground", "peeled", "cored", "optional", "divided", "threaded", "such as",
    "to taste", "as needed", "cut in half", "freshly", "minced", "toasted", "sliced", "melted",
    "ice-cold", "boiling", "cubed", "grated", "large", "medium", "small", "uncooked", "cold", "packed",
    "miniature", "cut", "drained", "warm", "diced", "frozen", "coarsely", "sprigs", "crispy",
    "superfine", "beaten", "softened", "thick", "refrigerated", "pitted", "chunks", "quartered",
    "halved", "seeded", "room temperature", "thawed", "trimmed", "shredded", "slivered", "regular",
    "finely", "leaves", "crumbled", "or for frying", "or more", "or", "yolk", "garlic stuffed",
    "on a toothpick", "processed", "cocktail sized", "for dusting"
]

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def lemmatize(text: str) -> str:
    return " ".join(lemmatizer.lemmatize(word) for word in text.split())

def clean_ingredient(raw: str) -> str:
    # Normalize unicode fractions (e.g., ½ → 1/2)
    text = normalize_unicode(raw.lower())

    # Remove quantities and measurements
    text = text.replace("-", " ")
    text = re.sub(r"\d+(\s\d+/\d+)?|\d+/\d+", "", text)  # Remove numbers and fractions
    text = re.sub(r"\([^)]*\)", "", text)  # Remove parentheses
    text = re.sub(r"[^\w\s-]", "", text)  # Remove punctuation

    # Remove units and descriptors
    for word in UNITS + DESCRIPTORS:
        text = re.sub(rf"\b{re.escape(word)}\b", "", text)

    # Collapse whitespace and trim
    return lemmatize(re.sub(r"\s+", " ", text).strip())

def parse_ingredients_block(block: str) -> List[dict]:
    lines = block.split("\n")
    return [
        {"original": line.strip(), "normalized": clean_ingredient(line)}
        for line in lines if line.strip()
    ]

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_phrases(phrases: List[str]) -> np.ndarray:
    return model.encode(phrases, convert_to_numpy=True, normalize_embeddings=True)

def match_ingredients(recipe_ings: List[str], store_ings: List[str], threshold=0.75) -> dict:
    recipe_vecs = embed_phrases(recipe_ings)
    store_vecs = embed_phrases(store_ings)

    matches = {}
    for i, r_vec in enumerate(recipe_vecs):
        sims = cosine_similarity([r_vec], store_vecs)[0]
        matched = [
            {"store_ingredient": store_ings[j], "score": float(sims[j])}
            for j in np.where(sims >= threshold)[0]
        ]
        matches[recipe_ings[i]] = sorted(matched, key=lambda x: -x["score"])
    return matches

def normalize_store_ingredient(name: str) -> str:
    return clean_ingredient(name)

def load_and_normalize_store_ingredients(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        raw = [json.loads(line)["title"].strip() for line in f]
    return list(set(normalize_store_ingredient(name) for name in raw if name.strip()))

# Example usage
if __name__ == "__main__":
    with open(r"C:\Users\nabro\Desktop\Portfolio Projects\grocery_optimizer\ETL (Python)\recipes.jsonl", "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    
    sample_block = lines[0:10]
    for recipe in sample_block:
        recipe_ings = parse_ingredients_block(recipe["ingredients"])
        store_ings = load_and_normalize_store_ingredients(r"C:\Users\nabro\Desktop\Portfolio Projects\grocery_optimizer\ETL (Python)\ingredients.jsonl")
        normalized_ings = [item["normalized"] for item in recipe_ings]
        matches = match_ingredients(normalized_ings, store_ings)
        for ing_dict in recipe_ings:
            ing = ing_dict["normalized"]
            print(f"\n🔗 {ing_dict['original']} → {ing}")
            for m in matches.get(ing, []):
                print(f"  → {m['store_ingredient']} ({m['score']:.2f})")

