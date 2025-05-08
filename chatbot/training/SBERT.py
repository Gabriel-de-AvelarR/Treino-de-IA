from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import classification_report
import re

# Carrega o modelo SBERT
modelo = SentenceTransformer("distiluse-base-multilingual-cased-v1")


dados_teste = [
    ("ligue o ar condicionado", "ligar_ar"),
    ("desligue o ar", "desligar_ar"),
    ("tá muito frio aqui", "aumentar_temp"),
    ("estou suando", "diminuir_temp"),
    ("quanto está a temperatura?", "consultar_temp"),
    ("coloque 18 graus", "setar_temp"),
    ("me conte uma piada", "no_intent"),
]


# Exemplos de cada intenção (com variações mais realistas)
intencoes = {
    "ligar_ar": [
        "ligue o ar", "ative o ar condicionado", "quero ligar o ar", "por favor ligue o ar",
        "habilite o ar", "prepare o ar", "deixe o ar pronto", "comece o ar"
    ],
    "desligar_ar": [
        "desligue o ar", "pare o ar", "por favor desligue o ar", "desative o ar condicionado",
        "quero desligar o ar", "desligue imediatamente", "encerre a refrigeração"
    ],
    "aumentar_temp": [
        "aumente a temperatura", "suba o ar", "quero mais quente","menos gelado","está frio", "coloque 18 graus", "menos gelado", "deixe mais quente","estou congelando",
    ],
    "diminuir_temp": [
        "diminua a temperatura", "baixe o ar","quero mais frio" , "mais gelado","está quente", "aumente pra 28", "deixe mais frio", "estou suando",
    ],
    "consultar_temp": [
        "qual a temperatura", "me diga a temperatura", "quanto está fazendo", "como está o clima"
    ]
}

# Função de pré-processamento
def limpar_frase(frase):
    frase = frase.lower()
    frase = re.sub(r'[^\w\s]', '', frase)  # remove pontuação
    return frase

# Função para reforçar decisão com palavras-chave
def detectar_keywords(frase):
    frase = frase.lower()
    
    # Ajuste para 'habilitar' sendo interpretado como 'ligar'
    if "habilite" in frase or "prepare" in frase:
        return "ligar_ar"
    
    if any(p in frase for p in ["desligue", "desative", "encerre"]):
        return "desligar_ar"
    if any(p in frase for p in ["ligue", "ative", "comece"]):
        return "ligar_ar"
    if any(p in frase for p in ["aumente", "menos frio", "menos gelado"]):
        return "aumentar_temp"
    if any(p in frase for p in ["diminua", "mais gelado", "menos quente"]):
        return "diminuir_temp"
    if "temperatura" in frase or "quanto está" in frase:
        return "consultar_temp"
    return None

# Classificação usando SBERT
def classificar_intencao(frase_usuario):
    entrada = modelo.encode(limpar_frase(frase_usuario), convert_to_tensor=True)
    melhor_intencao = None
    melhor_score = -1

    for intencao, exemplos in intencoes.items():
        for exemplo in exemplos:
            emb_exemplo = modelo.encode(exemplo, convert_to_tensor=True)
            score = util.pytorch_cos_sim(entrada, emb_exemplo).item()
            if score > melhor_score:
                melhor_score = score
                melhor_intencao = intencao

    return melhor_intencao, round(melhor_score, 3)

# Extrai valor numérico da frase (graus)
def extrair_temperatura(frase):
    match = re.search(r"(\d{1,2})\s*(graus)?", frase)
    if match:
        return int(match.group(1))
    return None

# Interpretador principal
def interpretar(frase):
    print(f"\n🗣️ Frase: \"{frase}\"")
    
    # Reforço baseado em palavras-chave
    keyword_intent = detectar_keywords(frase)
    if keyword_intent:
        print(f"⚡ Palavra-chave detectada: {keyword_intent}")
        if keyword_intent in ["aumentar_temp", "diminuir_temp"]:
            temp = extrair_temperatura(frase)
            if temp:
                return {"acao": "set_temp", "valor": temp}
        return {"acao": keyword_intent}

    # Classificação com SBERT
    intencao, score = classificar_intencao(frase)
    print(f"🤖 SBERT: {intencao} (confiança: {score})")

    # Análise da intenção
    if intencao in ["aumentar_temp", "diminuir_temp"]:
        valor = extrair_temperatura(frase)
        if valor:
            return {"acao": "set_temp", "valor": valor}
        else:
            return {"acao": intencao, "confianca": score}
    elif intencao in ["ligar_ar", "desligar_ar", "consultar_temp"]:
        return {"acao": intencao, "confianca": score}
    else:
        return {"acao": "desconhecida", "confianca": score}

# Avaliação
y_true = []
y_pred = []


for frase, esperado in dados_teste:
    previsto, _ = classificar_intencao(frase)
    y_true.append(esperado)
    y_pred.append(previsto)

# Relatório de desempenho
print("\n========== Relatório de Classificação ==========")
print(classification_report(y_true, y_pred, digits=2))

while True:
    i = input("Insira um comando:")
    if i == "sair":
        break
    print(interpretar(i))
