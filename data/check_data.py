import json
from collections import Counter
from pathlib import Path

data_dir = Path(__file__).parent/"raw"
data_file = data_dir/"train_data.json"

with open(data_file, "r", encoding="utf8") as f:
    train_data = json.load(f)

intent_counter = Counter()

for entry in train_data:
    intent_counter[entry["intent"]] += 1
    
    for ent in entry["entities"]:
        span_text = entry["text"][ent["start"]:ent["end"]]
        print(f'{span_text} → {ent["label"]}')

# Exibe as contagens de cada intenção
print("\nContagem de intents:")
for intent, count in intent_counter.items():
    print(f"{intent}: {count}")
