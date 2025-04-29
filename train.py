import spacy 
from spacy.tokens import DocBin
from spacy.cli.train import train 

import json
import random
from sklearn.model_selection import train_test_split  # Usada para dividir os dados em treino e validação


nlp = spacy.load("pt_core_news_lg")

with open("train_data.json", "r", encoding="utf8") as f:
    train_data = json.load(f)

random.seed(42)
random.shuffle(train_data)
train_examples, dev_examples = train_test_split(train_data, test_size=0.2, random_state=42)

def create_docbin(examples, filename):
    db = DocBin()  
    for example in examples:
        doc = nlp.make_doc(example["text"])

        ents = []  
        for ent in example["entities"]:
            span = doc.char_span(ent["start"], ent["end"], label=ent["label"])
            if span:  
                ents.append(span)
        doc.ents = ents  

        cats = {
            "ligar": example["intent"] == "ligar",
            "desligar": example["intent"] == "desligar",
            "aumentar_temp": example["intent"] == "aumentar_temp",
            "diminuir_temp": example["intent"] == "diminuir_temp",
            "consultar_temp": example["intent"] == "consultar_temp", 
            "setar_temp": example["intent"] == "setar_temp",
            "no_intent": example["intent"] == "no_intent"
            
        }
        doc.cats = cats  

        db.add(doc)  
    db.to_disk(filename)  
    print(f"Arquivo {filename} foi criado com sucesso, contendo {len(examples)} exemplos")
    
create_docbin(train_examples, "train.spacy")
create_docbin(dev_examples, "dev.spacy")

train("config.cfg", output_path="myfirstmodel", overrides={
    "paths.train": "train.spacy",  
    "paths.dev": "dev.spacy"       
})

dev_nlp = spacy.load("myfirstmodel/model-best")
dev_db = DocBin().from_disk("dev.spacy")
dev_docs = list(dev_db.get_docs(dev_nlp.vocab))

for doc in dev_docs[:5]:
    pred_doc = dev_nlp(doc.text)  
    pred_intent = max(pred_doc.cats, key=pred_doc.cats.get)  
    true_intent = max(doc.cats, key=doc.cats.get)  

    print(f"\nTexto: {doc.text}")
    print(f"Intent esperada: {true_intent}")
    print(f"Intent detectada: {pred_intent}")
    print(f"Entidades esperadas: {[(ent.text, ent.label_) for ent in doc.ents]}")
    print(f"Entidades detectadas: {[(ent.text, ent.label_) for ent in pred_doc.ents]}")




