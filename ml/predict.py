"""
API Flask para predicción de riesgo de ansiedad.

Carga 6 modelos de Machine Learning (.pkl) y expone un endpoint REST
para recibir los datos del cuestionario y retornar la predicción
del nivel de riesgo de ansiedad (ALTO, MODERADO o BAJO) usando
el promedio de probabilidades de los 6 modelos.

Los modelos fueron entrenados únicamente con 7 variables en formato PascalCase:
  PHQ9, GAD7, OnlineStress, FinancialStress, ExerciseFreq, SocialActivity, SleepHours

El backend Java envía 15 variables en camelCase. Este servicio:
  1. Valida las 15 variables camelCase
  2. Mapea las 7 necesarias a PascalCase para los modelos
  3. Ejecuta los 6 modelos y calcula P(BAJO) promedio
  4. Clasifica en ALTO (≤40%), MODERADO (40-70%) o BAJO (≥70%)
  5. Retorna nivel de riesgo + recomendaciones personalizadas

Modelos cargados:
  1. Random Forest
  2. XGBoost
  3. LightGBM
  4. CatBoost
  5. KNN (K-Nearest Neighbors)
  6. Logistic Regression
"""

import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

# ============================================================
# INICIALIZACIÓN DE FLASK
# ============================================================

app = Flask(__name__)
CORS(app)

# ============================================================
# RUTA DONDE ESTÁN LOS MODELOS
# ============================================================

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# ============================================================
# DEFINICIÓN DE CAMPOS
# ============================================================

# Los 15 campos que Java envía en camelCase (para validación del JSON)
ALL_INPUT_FIELDS = [
    "phq9", "gad7", "sleepHours", "exerciseFreq", "socialActivity",
    "onlineStress", "gpa", "familySupport", "screenTime",
    "academicStress", "dietQuality", "selfEfficacy",
    "peerRelationship", "financialStress", "sleepQuality",
]

# Mapeo camelCase (Java) → PascalCase (modelos entrenados)
FIELD_MAPPING = {
    "phq9": "PHQ9",
    "gad7": "GAD7",
    "onlineStress": "OnlineStress",
    "financialStress": "FinancialStress",
    "exerciseFreq": "ExerciseFreq",
    "socialActivity": "SocialActivity",
    "sleepHours": "SleepHours",
}

# Las 7 columnas PascalCase que los modelos necesitan
MODEL_FEATURES = list(FIELD_MAPPING.values())

# Nombres amigables de los modelos
MODEL_DISPLAY_NAMES = {
    "random_forest_model": "Random Forest",
    "xgboost_weighted_model": "XGBoost",
    "lightgbm_model": "LightGBM",
    "catboost_weighted_model": "CatBoost",
    "knn_model": "KNN",
    "logistic_regression_model": "Logistic Regression",
}

# ============================================================
# UMBRALES PARA LOS 3 NIVELES (ÚNICO CRITERIO DE DECISIÓN)
# ============================================================
# Se usa el promedio de P(BAJO) entre los 6 modelos:
#   P(BAJO) ≤ 0.40  → ALTO
#   0.40 < P(BAJO) ≤ 0.70  → MODERADO
#   P(BAJO) > 0.70  → BAJO
#
# Los votos binarios (P(BAJO) > 0.5 → BAJO) son SOLO informativos.
# La decisión final SIEMPRE se basa en el promedio de probabilidades.

UMBRAL_ALTO = 0.40    # Por debajo de esto → ALTO
UMBRAL_BAJO = 0.70    # Por encima de esto → BAJO
# Entre ambos → MODERADO

# ============================================================
# CARGA DE MODELOS AL INICIAR EL SERVIDOR
# ============================================================

models = {}
models_loaded = []


def load_models():
    """Carga todos los modelos .pkl desde la carpeta models/."""
    global models, models_loaded
    print("=" * 60)
    print("CARGANDO MODELOS DE MACHINE LEARNING")
    print("=" * 60)
    for filename in sorted(os.listdir(MODELS_DIR)):
        if filename.endswith(".pkl"):
            model_name = filename.replace(".pkl", "")
            filepath = os.path.join(MODELS_DIR, filename)
            try:
                model = joblib.load(filepath)
                models[model_name] = model
                models_loaded.append(model_name)
                print(f"  ✅ {MODEL_DISPLAY_NAMES.get(model_name, model_name)} cargado")
            except Exception as e:
                print(f"  ❌ Error cargando {filename}: {str(e)}")
    print(f"Total modelos cargados: {len(models)}/{len(os.listdir(MODELS_DIR))}")
    print("=" * 60)


load_models()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def build_model_dataframe(data):
    """Construye DataFrame con las 7 columnas PascalCase para los modelos."""
    model_data = {}
    for camel_name, pascal_name in FIELD_MAPPING.items():
        model_data[pascal_name] = [float(data[camel_name])]
    return pd.DataFrame(model_data, columns=MODEL_FEATURES)


def ejecutar_prediccion(features_df):
    """
    Ejecuta la predicción usando el promedio de probabilidades de los 6 modelos ML.
    
    ÚNICO CRITERIO: Promedio de P(BAJO) con umbrales:
      - ALTO:     P(BAJO) promedio ≤ 0.40
      - MODERADO: 0.40 < P(BAJO) promedio ≤ 0.70
      - BAJO:     P(BAJO) promedio > 0.70
    
    Los votos binarios (threshold 0.5) son SOLO informativos, no deciden.
    
    NOTA: Los modelos fueron entrenados con:
      clase 0 = ALTO riesgo, clase 1 = BAJO riesgo
    predict_proba[0][1] = P(BAJO)
    """
    # 1. Obtener P(BAJO) de cada modelo
    probabilidades = {}
    predicciones_individuales = {}

    for model_name, model in models.items():
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features_df)
                prob_bajo = float(proba[0][1])  # Probabilidad de clase 1 = BAJO
                probabilidades[display_name] = prob_bajo
                
                # Voto binario SOLO informativo (threshold 0.5)
                voto = "BAJO" if prob_bajo >= 0.5 else "ALTO"
                predicciones_individuales[display_name] = {
                    "voto": voto,
                    "probabilidad_BAJO": round(prob_bajo, 4)
                }
                
                print(f"  {display_name}: P(BAJO)={prob_bajo:.4f} → voto_binario={voto}")
            else:
                # Modelos sin predict_proba (usar predict directo)
                raw_pred = model.predict(features_df)
                label = int(raw_pred[0])
                prob_bajo = 1.0 if label == 1 else 0.0
                probabilidades[display_name] = prob_bajo
                nivel = "BAJO" if label == 1 else "ALTO"
                predicciones_individuales[display_name] = {
                    "voto": nivel,
                    "probabilidad_BAJO": prob_bajo
                }
                
                print(f"  {display_name}: predicción_cruda={label} → voto_binario={nivel}")
        except Exception as e:
            print(f"  ⚠️ Error en {display_name}: {str(e)}")

    # 2. Calcular P(BAJO) promedio (ÚNICO CRITERIO DE DECISIÓN)
    if not probabilidades:
        return "BAJO", 0.0, {"ALTO": 0, "BAJO": 0}, {}, 0.0

    promedio_bajo = float(np.mean(list(probabilidades.values())))
    
    print(f"\n  P(BAJO) promedio: {promedio_bajo:.4f} (ÚNICO criterio de decisión)")

    # 3. Determinar nivel por umbrales de probabilidad
    if promedio_bajo <= UMBRAL_ALTO:
        nivel_riesgo = "ALTO"
    elif promedio_bajo <= UMBRAL_BAJO:
        nivel_riesgo = "MODERADO"
    else:
        nivel_riesgo = "BAJO"

    # 4. Calcular confianza basada en qué tan lejos está del centro del rango
    if nivel_riesgo == "ALTO":
        confianza = round(1.0 - (promedio_bajo / UMBRAL_ALTO), 2) if UMBRAL_ALTO > 0 else 0.0
    elif nivel_riesgo == "BAJO":
        confianza = round((promedio_bajo - UMBRAL_BAJO) / (1.0 - UMBRAL_BAJO), 2)
    else:  # MODERADO
        centro = (UMBRAL_ALTO + UMBRAL_BAJO) / 2.0  # 0.55
        distancia_al_centro = abs(promedio_bajo - centro)
        max_distancia = centro - UMBRAL_ALTO  # 0.15
        if max_distancia > 0:
            confianza_baja = distancia_al_centro / max_distancia
            confianza = round(1.0 - confianza_baja, 2)
        else:
            confianza = 0.5
    
    confianza = max(0.0, min(1.0, confianza))

    # 5. Votos binarios: SOLO informativos (no afectan la decisión final)
    votos_bajo = sum(1 for p in probabilidades.values() if p > 0.5)
    votos_alto = len(probabilidades) - votos_bajo
    votos = {"ALTO": votos_alto, "BAJO": votos_bajo}

    print(f"\n  🎯 RESULTADO FINAL (por P(BAJO) promedio):")
    print(f"     Nivel: {nivel_riesgo}")
    print(f"     P(BAJO) promedio: {promedio_bajo:.2%}")
    print(f"     Confianza: {confianza}")
    print(f"     Votos binarios (solo informativo): ALTO={votos_alto}, BAJO={votos_bajo}")

    return nivel_riesgo, confianza, votos, predicciones_individuales, promedio_bajo


def get_recomendaciones(nivel_riesgo, features, promedio_bajo=None):
    """Genera recomendaciones personalizadas basadas en el nivel y features."""
    recomendaciones = []

    if nivel_riesgo == "ALTO":
        recomendaciones.append("🔴 Tu nivel de ansiedad es ALTO. Se recomienda consultar con un profesional de salud mental de forma urgente.")
        recomendaciones.append("📞 Si estás en crisis, contacta la línea de ayuda: 106 (SALUD MENTAL - Perú).")
    elif nivel_riesgo == "MODERADO":
        recomendaciones.append("🟡 Tu nivel de ansiedad es MODERADO. Es recomendable buscar apoyo profesional para monitorear tu salud mental.")
        recomendaciones.append("📋 Realiza un seguimiento de tus síntomas. Si empeoran, no dudes en consultar a un especialista.")
    else:
        recomendaciones.append("🟢 Tu nivel de riesgo es BAJO. ¡Sigue cuidando tu bienestar!")

    if features.get("sleepHours", 8) < 6:
        recomendaciones.append("😴 Intenta dormir al menos 7-8 horas. La falta de sueño afecta directamente la ansiedad.")
    if features.get("sleepQuality", 5) < 4:
        recomendaciones.append("🛏️ Tu calidad de sueño es baja. Evita pantallas 1 hora antes de dormir.")
    if features.get("exerciseFreq", 3) < 2:
        recomendaciones.append("🏃 Realiza actividad física al menos 3 veces por semana.")
    if features.get("screenTime", 5) > 8:
        recomendaciones.append("📱 Tu tiempo de pantalla es alto. Intenta reducirlo.")
    if features.get("socialActivity", 5) < 3:
        recomendaciones.append("👥 Intenta socializar más. Las relaciones sociales son un factor protector.")
    if features.get("academicStress", 5) > 7:
        recomendaciones.append("📚 Tu estrés académico es alto. Organiza tu tiempo con un plan de estudio.")
    if features.get("dietQuality", 5) < 4:
        recomendaciones.append("🥗 Mejora tu alimentación. Una dieta balanceada influye en tu salud mental.")
    if features.get("financialStress", 5) > 7:
        recomendaciones.append("💰 Busca apoyo en programas de becas o asesoría financiera.")
    if features.get("familySupport", 5) < 3:
        recomendaciones.append("👨‍👩‍👧 Busca apoyo en tu círculo familiar o en personas de confianza.")
    if features.get("selfEfficacy", 5) < 4:
        recomendaciones.append("💪 Trabaja en tu autoestima. Establece metas pequeñas y celebra cada logro.")
    if features.get("onlineStress", 5) > 7:
        recomendaciones.append("🌐 El estrés digital es alto. Toma descansos de redes sociales.")

    return recomendaciones


# ============================================================
# ENDPOINTS
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "ML Prediction Service",
        "status": "running",
        "models_loaded": len(models),
        "models": [MODEL_DISPLAY_NAMES.get(m, m) for m in models_loaded],
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "models_count": len(models)})


@app.route("/predict", methods=["POST"])
def predict():
    """Endpoint principal de predicción con 3 niveles: ALTO, MODERADO, BAJO."""
    if not models:
        return jsonify({"error": "No hay modelos cargados"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Envía un JSON con los 15 features."}), 400

    missing = [f for f in ALL_INPUT_FIELDS if f not in data]
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

    for field in ALL_INPUT_FIELDS:
        try:
            float(data[field])
        except (ValueError, TypeError):
            return jsonify({"error": f"'{field}' debe ser numérico. Valor: {data[field]}"}), 400

    try:
        features_df = build_model_dataframe(data)
    except KeyError as e:
        return jsonify({"error": f"Error al mapear: {str(e)}"}), 400

    nivel_riesgo, confianza, votos, predicciones, promedio_bajo = ejecutar_prediccion(features_df)
    recomendaciones = get_recomendaciones(nivel_riesgo, data, promedio_bajo)

    return jsonify({
        "nivel_riesgo": nivel_riesgo,
        "confianza": confianza,
        "votos": votos,
        "predicciones": predicciones,
        "recomendaciones": recomendaciones,
        "probabilidad_bajo_promedio": round(promedio_bajo, 4),
    })


@app.route("/predict/<model_name>", methods=["POST"])
def predict_single(model_name):
    """Predicción con un modelo específico."""
    if not models:
        return jsonify({"error": "No hay modelos cargados"}), 500

    found_model = None
    found_key = None
    for key in models:
        display = MODEL_DISPLAY_NAMES.get(key, key)
        if key == model_name or display.lower().replace(" ", "_") == model_name.lower().replace(" ", "_"):
            found_model = models[key]
            found_key = key
            break

    if not found_model:
        return jsonify({"error": f"Modelo '{model_name}' no encontrado", "disponibles": list(MODEL_DISPLAY_NAMES.values())}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Envía un JSON con los 15 features"}), 400

    missing = [f for f in ALL_INPUT_FIELDS if f not in data]
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

    features_df = build_model_dataframe(data)
    try:
        raw_pred = found_model.predict(features_df)
        label = int(raw_pred[0]) if isinstance(raw_pred[0], (np.integer, int, np.floating)) else str(raw_pred[0])
        nivel = "BAJO" if label == 1 else "ALTO"

        result = {"modelo": MODEL_DISPLAY_NAMES.get(found_key, found_key), "prediccion": nivel}

        if hasattr(found_model, "predict_proba"):
            proba = found_model.predict_proba(features_df)
            result["probabilidad_BAJO"] = round(float(proba[0][1]), 4)
            result["probabilidad_ALTO"] = round(float(proba[0][0]), 4)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Servicio ML iniciado en http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)