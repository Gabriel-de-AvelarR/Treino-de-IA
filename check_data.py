import json
from collections import Counter

with open("train_data.json", "r", encoding="utf8") as f:
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
