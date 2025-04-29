import spacy

nlp = spacy.load("myfirstmodel/model-best")

texto = "esfrie a sala"

doc = nlp(texto)

intent = max(doc.cats, key=doc.cats.get)

entidades = [(ent.text, ent.label_) for ent in doc.ents]

print(f"\nTexto: {texto}")
print(f"Intent detectada: {intent}")
print(f"Entidades detectadas: {entidades}")
