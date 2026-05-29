"""
API Flask para predicción de riesgo de ansiedad.

Carga 6 modelos de Machine Learning (.pkl) y expone un endpoint REST
para recibir los datos del cuestionario y retornar la predicción
del nivel de riesgo de ansiedad (BAJO, MODERADO, ALTO).

Los modelos fueron entrenados únicamente con 7 variables en formato PascalCase:
  PHQ9, GAD7, OnlineStress, FinancialStress, ExerciseFreq, SocialActivity, SleepHours

El backend Java envía 15 variables en camelCase. Este servicio:
  1. Valida las 15 variables camelCase
  2. Mapea las 7 necesarias a PascalCase para los modelos
  3. Calcula un score clínico basado en reglas con los 15 features
  4. Retorna nivel de riesgo + recomendaciones personalizadas

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


def calcular_score_clinico(features):
    """
    Calcula un score clínico de riesgo de ansiedad (0-100) basado en
    los 15 features usando reglas clínicas establecidas.

    Basado en PHQ-9, GAD-7 y factores de riesgo psicosocial.
    """
    score = 0.0

    # === FACTORES CLAVE (60 pts máximo) ===
    # PHQ-9 (Depresión) 0-27 → 20 pts
    score += (features.get("phq9", 0) / 27.0) * 20.0
    # GAD-7 (Ansiedad) 0-21 → 20 pts
    score += (features.get("gad7", 0) / 21.0) * 20.0
    # Estrés académico 0-10 → 10 pts
    score += (features.get("academicStress", 5) / 10.0) * 10.0
    # Estrés financiero 0-10 → 10 pts
    score += (features.get("financialStress", 5) / 10.0) * 10.0

    # === FACTORES MODERADORES (25 pts máximo) ===
    # Estrés online 0-10 → 8 pts
    score += (features.get("onlineStress", 5) / 10.0) * 8.0
    # Calidad del sueño 0-10 (invertido) → 8 pts
    score += ((10.0 - features.get("sleepQuality", 5)) / 10.0) * 8.0
    # Horas de sueño (invertido) → 5 pts
    sleep_h = features.get("sleepHours", 7)
    if sleep_h < 5:
        score += 5.0
    elif sleep_h < 7:
        score += 2.5
    # Autoeficacia 0-10 (invertido) → 4 pts
    score += ((10.0 - features.get("selfEfficacy", 5)) / 10.0) * 4.0

    # === FACTORES PROTECTORES (restan riesgo) ===
    score -= (features.get("exerciseFreq", 3) / 7.0) * 5.0
    score -= (features.get("socialActivity", 5) / 10.0) * 5.0
    score -= (features.get("familySupport", 5) / 10.0) * 5.0

    return round(max(0.0, min(100.0, score)), 2)


def get_recomendaciones(nivel_riesgo, features):
    """Genera recomendaciones personalizadas basadas en el nivel y features."""
    recomendaciones = []

    if nivel_riesgo == "ALTO":
        recomendaciones.append("🔴 Se recomienda consultar con un profesional de salud mental de forma urgente.")
        recomendaciones.append("📞 Si estás en crisis, contacta la línea de ayuda: 106 (SALUD MENTAL - Perú).")
    elif nivel_riesgo == "MODERADO":
        recomendaciones.append("🟡 Considera agendar una cita con el orientador psicológico de tu universidad.")
        recomendaciones.append("📝 Lleva un diario emocional para identificar tus patrones de estrés.")
    else:
        recomendaciones.append("🟢 Tu nivel de riesgo es bajo. ¡Sigue cuidando tu bienestar!")

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


def ejecutar_prediccion(features_df, data_features):
    """
    Ejecuta la predicción usando score clínico (100% determinante)
    y probabilidades ML como referencia informativa.

    Los modelos ML son binarios y no discriminan entre niveles de riesgo,
    por lo que el score clínico es el determinante principal.
    """
    # 1. Score clínico
    score_clinico = calcular_score_clinico(data_features)
    print(f"\n  Score clínico: {score_clinico}/100")

    # 2. Probabilidades ML (solo informativo)
    probabilidades_clase_1 = []
    for model_name, model in models.items():
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features_df)
                prob_clase_1 = float(proba[0][1])
                probabilidades_clase_1.append(prob_clase_1)
                print(f"  {MODEL_DISPLAY_NAMES.get(model_name, model_name)}: prob_riesgo={prob_clase_1:.6f}")
        except Exception:
            pass

    # 3. Score final = 100% clínico
    score_final = score_clinico
    print(f"  Score final (100% clínico): {score_final}/100")

    # 4. Mapear a nivel de riesgo
    if score_final >= 55:
        nivel_riesgo = "ALTO"
    elif score_final >= 30:
        nivel_riesgo = "MODERADO"
    else:
        nivel_riesgo = "BAJO"

    # 5. Confianza
    if score_final >= 70 or score_final <= 15:
        confianza = 0.9
    elif score_final >= 55 or score_final >= 30:
        confianza = 0.7
    else:
        confianza = 0.6

    # 6. Votos y predicciones
    votos = {"BAJO": 0, "MODERADO": 0, "ALTO": 0}
    predicciones = {}

    if score_clinico >= 55:
        predicciones["Score Clínico"] = "ALTO"
        votos["ALTO"] += 1
    elif score_clinico >= 30:
        predicciones["Score Clínico"] = "MODERADO"
        votos["MODERADO"] += 1
    else:
        predicciones["Score Clínico"] = "BAJO"
        votos["BAJO"] += 1

    for model_name, model in models.items():
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features_df)
                prob = float(proba[0][1])
                nivel = "ALTO" if prob >= 0.5 else ("MODERADO" if prob >= 0.2 else "BAJO")
                predicciones[MODEL_DISPLAY_NAMES.get(model_name, model_name)] = nivel
                votos[nivel] += 1
        except Exception:
            pass

    print(f"  Nivel final: {nivel_riesgo} (confianza: {confianza})")
    return nivel_riesgo, confianza, votos, predicciones, score_clinico


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
    """Endpoint principal de predicción."""
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

    nivel_riesgo, confianza, votos, predicciones, score_clinico = ejecutar_prediccion(features_df, data)
    recomendaciones = get_recomendaciones(nivel_riesgo, data)

    return jsonify({
        "nivel_riesgo": nivel_riesgo,
        "confianza": confianza,
        "score_clinico": score_clinico,
        "votos": votos,
        "predicciones": predicciones,
        "recomendaciones": recomendaciones,
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
        return jsonify({"modelo": MODEL_DISPLAY_NAMES.get(found_key, found_key), "prediccion_cruda": str(label)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Servicio ML iniciado en http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)