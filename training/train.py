import os 
import spacy
from spacy.tokens import DocBin
from spacy.cli.train import train

from spacy.training import Example
from spacy.util import load_config

from thinc.api import set_gpu_allocator, require_gpu

import json
import random
import time
from sklearn.model_selection import train_test_split  
from pathlib import Path


PARENT_DIR = Path(__file__).parent
BASE_DIR = Path(__file__).parent.parent

MODELS_DIR = BASE_DIR/"models"
DATA_PROCESSED_DIR = BASE_DIR/"data"/"processed"
DATA_RAW_PATH = BASE_DIR/"data"/"raw"/"train_data.json"
CONFIG_PATH = PARENT_DIR/"config.cfg"


DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

nlp = spacy.load("pt_core_news_lg")

with open(DATA_RAW_PATH, "r", encoding="utf8") as f:
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
            "diminuir a temperatura": example["intent"] == "diminuir a temperatura",
            "aumentar a temperatura": example["intent"] == "aumentar a temperatura",
            "consultar a temperatura": example["intent"] == "consultar a temperatura", 
            "ajustar a temperatura": example["intent"] == "ajustar a temperatura",
            "no_intent": example["intent"] == "no_intent"
            
        }
        doc.cats = cats  

        db.add(doc)  
    output_path = DATA_PROCESSED_DIR/filename
    db.to_disk(output_path)  
    print(f"Arquivo {filename} foi criado com sucesso, contendo {len(examples)} exemplos")
    
create_docbin(train_examples, "train.spacy")
create_docbin(dev_examples, "dev.spacy")


################ CONFIGURACAO DE GPU ################
'''
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
set_gpu_allocator("pytorch")
try:
    require_gpu(0)
    print("Usando a GPU")
except Exception:
    print("GPU nao disponivel, usando CPU")
'''
################ BENCHMARK CPU VS GPU ####################
def benchmark():
    config = load_config(CONFIG_PATH)
    nlp = spacy.util.load_model_from_config(config, auto_fill=True)
    
    doc_bin = DocBin().from_disk("data/processed/train.spacy")

    train_docs = list(doc_bin.get_docs(nlp.vocab))
    examples = [Example.from_dict(doc, {"entities": [ (ent.start_char, ent.end_char, ent.label_) for ent in doc.ents], "cats": doc.cats}) for doc in train_docs]


    num_repeticoes = 10
    tempos = []

    for i in range(num_repeticoes):
        optimizer = nlp.initialize(lambda: examples)
        start_time = time.time()

        for epoch in range(config["training"]["max_epochs"]):
            losses = {}
            nlp.update(examples, sgd=optimizer, losses=losses)

        end_time = time.time()
        elipsed_time = end_time - start_time
        print(f"Rodada {i}: {elipsed_time:.2f} segundos")
        tempos.append(elipsed_time)
    '''
    for i, t in enumerate(tempos, 1):
        print(f"Rodada {i}: {t:.2f} segundos")
    '''
    media = sum(tempos) / len(tempos)
    print(f"Tempo medio de treinamento: {media:.2f} segundos")


benchmark()

############### CRIACAO E VALIDACAO ################

def create_model():
    train(str(PARENT_DIR/"config.cfg"), output_path=str(MODELS_DIR), overrides={
        "paths.train": str(DATA_PROCESSED_DIR/"train.spacy"),  
        "paths.dev": str(DATA_PROCESSED_DIR/"dev.spacy")
        },
        use_gpu = 0)

    dev_nlp = spacy.load(str(MODELS_DIR/ "model-best"))
    dev_db = DocBin().from_disk(str(DATA_PROCESSED_DIR/"dev.spacy"))
    dev_docs = list(dev_db.get_docs(dev_nlp.vocab))
'''
    for doc in dev_docs[:5]:
        pred_doc = dev_nlp(doc.text)  
        pred_intent = max(pred_doc.cats, key=pred_doc.cats.get)  
        true_intent = max(doc.cats, key=doc.cats.get)  

        print(f"\nTexto: {doc.text}")
        print(f"Intent esperada: {true_intent}")
        print(f"Intent detectada: {pred_intent}")
        print(f"Entidades esperadas: {[(ent.text, ent.label_) for ent in doc.ents]}")
        print(f"Entidades detectadas: {[(ent.text, ent.label_) for ent in pred_doc.ents]}")
'''

#create_model()

