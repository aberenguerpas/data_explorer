from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import matplotlib.pyplot as plt

# === CONFIGURACIÓN ===
model_name = 'Snowflake/snowflake-arctic-embed-m-v2.0'
model = SentenceTransformer(model_name, trust_remote_code=True)

# === TUS DATOS ===
pairs = [
    ("El gato duerme en el sofá", "Un felino descansa en el sillón"),  # similares
    ("Hoy hace sol en Madrid", "Llueve mucho en Berlín"),              # distintas
    ("Compra boletos en línea", "Adquiere entradas por internet"),     # similares
    ("Estoy aprendiendo a cocinar", "Los gatos son muy curiosos"),      # distintas
    ("El perro ladra en el jardín", "Un canino hace ruido en el patio"), # similares
    ("Me gusta el café por la mañana", "Prefiero el té al atardecer"),  # distintas
    ("Voy a correr en el parque", "Salgo a trotar en el jardín"),       # similares
    ("El cielo está despejado", "Hay muchas nubes hoy"),               # distintas
    ("Leer un libro es relajante", "Ver una película es entretenido"),  # distintas
    ("Necesito comprar pan", "Debo adquirir leche"),                   # similares
    ("El niño juega en el parque", "Los niños corren en el jardín"),   # similares
    ("El agua hierve a 100 grados", "El hielo se derrite a 0 grados"), # similares
    ("Me encanta la pizza", "Odio la pasta"),                          # distintas
    ("Voy a viajar a París", "Visitaré Roma el próximo mes"),          # similares
    ("El coche está en el garaje", "La moto está en el estacionamiento"), # similares
    ("Hoy es un día soleado", "Ayer estuvo nublado"),                  # distintas
    ("Me gusta escuchar música", "Disfruto bailar"),                   # similares
    ("El libro está en la mesa", "La revista está en el estante"),     # similares
    ("Voy a nadar en la piscina", "Me gusta bucear en el mar"),        # similares
    ("El pastel está en el horno", "Las galletas están en la nevera"), # distintas
    ("El tren llega a las 5", "El autobús sale a las 6"),              # similares
    ("Me duele la cabeza", "Tengo dolor de estómago"),                 # similares
    ("El teléfono está sonando", "La puerta está abierta"),            # distintas
    ("Voy a estudiar para el examen", "Necesito repasar el tema"),     # similares
    ("El sol sale por el este", "La luna brilla de noche"),            # distintas
    ("Me gusta el chocolate", "Prefiero las fresas"),                  # distintas
    ("El avión despega a las 8", "El barco zarpa a las 9"),            # similares
    ("Voy a limpiar la casa", "Necesito lavar la ropa"),               # similares
    ("El reloj marca las 3", "El calendario muestra mayo"),            # distintas
    ("Me gusta pintar", "Disfruto dibujar")                            # similares
]

# Etiquetas: 1 si son similares, 0 si no
labels = [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1]


# === OBTENER EMBEDDINGS ===
sents1 = [p[0] for p in pairs]
sents2 = [p[1] for p in pairs]

emb1 = model.encode(sents1, convert_to_tensor=True, normalize_embeddings=True)
emb2 = model.encode(sents2, convert_to_tensor=True, normalize_embeddings=True)

# === CALCULAR SIMILITUD POR COSENO ===
sims = cosine_similarity(emb1.cpu(), emb2.cpu())
sim_scores = np.diag(sims)  # extraer valores diagonales

# === EVALUAR DIFERENTES THRESHOLDS ===
thresholds = np.arange(0.5, 0.96, 0.01)
best_f1 = 0
best_threshold = 0
results = []

for threshold in thresholds:
    preds = (sim_scores >= threshold).astype(int)
    acc = accuracy_score(labels, preds)
    prec = precision_score(labels, preds, zero_division=0)
    rec = recall_score(labels, preds)
    f1 = f1_score(labels, preds)

    results.append((threshold, acc, prec, rec, f1))

    if f1 > best_f1:
        best_f1 = f1
        best_threshold = threshold

# === MOSTRAR RESULTADOS ===
print(f"🔍 Mejor threshold: {best_threshold:.2f} con F1 = {best_f1:.4f}")
print("\nThresholds evaluados:")
for t, acc, prec, rec, f1 in results:
    print(f"  t={t:.2f} | Acc={acc:.2f} | Prec={prec:.2f} | Rec={rec:.2f} | F1={f1:.2f}")

# === OPCIONAL: GRAFICAR ===
ts = [r[0] for r in results]
f1s = [r[4] for r in results]

plt.plot(ts, f1s, label='F1-score')
plt.axvline(best_threshold, color='red', linestyle='--', label=f'Mejor threshold ({best_threshold:.2f})')
plt.xlabel("Threshold")
plt.ylabel("F1-score")
plt.title("Optimización de Threshold para Frases Similares")
plt.legend()
plt.grid(True)
plt.show()
