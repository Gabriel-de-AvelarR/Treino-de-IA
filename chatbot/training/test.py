import spacy
from pathlib import Path

default_models_dir = Path(__file__).parent.parent.parent/"models"
model_path = default_models_dir/"model-best"

nlp = spacy.load(model_path)

texto = "está muito calor no auditorio"

doc = nlp(texto)

intent = max(doc.cats, key=doc.cats.get)

entidades = [(ent.text, ent.label_) for ent in doc.ents]

print(f"\nTexto: {texto}")
print(f"Intent detectada: {intent}")
print(f"Entidades detectadas: {entidades}")
