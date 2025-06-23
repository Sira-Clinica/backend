import numpy as np
import joblib
import re
import unidecode
from scipy.sparse import hstack
from sentence_transformers import SentenceTransformer, util


modelo = joblib.load("backend_clinico/external/model/modelo_rf_mejorado.pkl")
label_encoder = joblib.load("backend_clinico/external/vectorizers/label_encoder_mejorado.pkl")
vectorizer_motivo = joblib.load("backend_clinico/external/vectorizers/vectorizer_motivo_mejorado.pkl")
vectorizer_examen = joblib.load("backend_clinico/external/vectorizers/vectorizer_examen_mejorado.pkl")
vectorizer_texto = joblib.load("backend_clinico/external/vectorizers/vectorizer_texto_final.pkl")
encoder_gz = joblib.load("backend_clinico/external/vectorizers/grupo_zona_encoder.pkl")


embedder = SentenceTransformer('distiluse-base-multilingual-cased-v1')


sinonimos = {
        
        "tos productiva": [
            "tos con flema", "expectoracion", "secrecion bronquial", "flema",
            "secreción mucosa", "moco", "secreciones"
        ],
        "roncus": [
            "sibilancias", "sonidos bronquiales", "ruidos respiratorios anormales",
            "ruidos roncos", "ruidos al respirar", "ruido bronquial"
        ],
        "dificultad respiratoria": [
            "disnea", "problemas al respirar", "jadeo", "sensacion de falta de aire",
            "respiracion dificultosa", "fatiga al respirar"
        ],

        
        "dolor de garganta": [
            "odinofagia", "garganta irritada", "molestia al tragar",
            "picazon en la garganta", "garganta inflamada", "ardor de garganta"
        ],
        "placas en garganta": [
            "placas blanquecinas", "secrecion purulenta faringea",
            "inflamacion faringea", "amigdalas inflamadas", "secreciones faríngeas"
        ],
        "ganglios inflamados": [
            "adenopatias", "inflamacion ganglionar", "nodulos en cuello",
            "bultos en cuello", "ganglios cervicales aumentados"
        ],

        
        "ronquera": [
            "voz ronca", "disfonia", "perdida de voz", "cambio de voz",
            "alteracion de la voz", "fatiga vocal", "voz apagada"
        ],
        "dolor al hablar": [
            "molestia al hablar", "esfuerzo vocal", "dolor de cuerdas vocales",
            "molestia fonatoria", "dolor laringeo"
        ],
        "edema en cuerdas vocales": [
            "inflamacion laringea", "cuerdas inflamadas", "eritema laringeo",
            "edema laringeo", "inflamación de la glotis"
        ],

        
        "faringe": [
            "garganta", "zona faringea", "faringitis"
        ],
        "laringe": [
            "cuerdas vocales", "laringe", "voz", "zona laringea", "laringitis"
        ],
        "bronquios": [
            "bronquial", "pulmon", "bronquitis", "arbol bronquial"
        ]
    }

canonicos = list(sinonimos.keys())
canonico_embeddings = {term: embedder.encode(term) for term in canonicos}

def normalizar_texto(texto):
    texto = str(texto).lower()
    texto = unidecode.unidecode(texto)  
    texto = re.sub(r"<.*?>", " ", texto)  
    texto = re.sub(r"[^a-z\s]", " ", texto)  
    texto = re.sub(r"\s+", " ", texto).strip()

    
    

    for canonico, variantes in sinonimos.items():
        for variante in variantes:
            if variante in texto:
                texto = texto.replace(variante, canonico)

    
    palabras = texto.split()
    for i, palabra in enumerate(palabras):
        if palabra in canonicos:
            continue  

        emb_palabra = embedder.encode(palabra)
        similitudes = [(c, util.cos_sim(emb_palabra, canonico_embeddings[c]).item()) for c in canonicos]
        mejor_canonico, sim = max(similitudes, key=lambda x: x[1])

        if sim > 0.75:
            palabras[i] = mejor_canonico
           

    return " ".join(palabras)


def clasificar_grupo_zona(texto):
    if any(palabra in texto for palabra in ["bronquios", "tos productiva", "roncus", "dificultad respiratoria"]):
        return "bronquios"
    elif any(palabra in texto for palabra in ["faringe", "dolor de garganta", "placas en garganta", "ganglios inflamados"]):
        return "faringe"
    elif any(palabra in texto for palabra in ["laringe", "ronquera", "dolor al hablar", "edema en cuerdas vocales"]):
        return "laringe"
    return "otro"

def predecir_diagnostico(temperatura, edad, f_card, f_resp, talla, peso, genero, motivo_consulta, examenfisico):
    genero_cod = 0 if genero.lower() == "m" else 1
    X_num = np.array([[temperatura, edad, f_card, f_resp, talla, peso, genero_cod]])

    motivo_normalizado = normalizar_texto(motivo_consulta)
    examen_normalizado = normalizar_texto(examenfisico)
    texto_final = motivo_normalizado + " " + examen_normalizado

    X_motivo = vectorizer_motivo.transform([motivo_normalizado])
    X_examen = vectorizer_examen.transform([examen_normalizado])
    X_texto = vectorizer_texto.transform([texto_final]).multiply(2.0)
    gz_encoded = encoder_gz.transform([clasificar_grupo_zona(texto_final)]).reshape(1, -1)

    X_final = hstack([X_num, X_motivo, X_examen, X_texto, gz_encoded])
    y_pred = modelo.predict(X_final)
    return label_encoder.inverse_transform(y_pred)[0]
