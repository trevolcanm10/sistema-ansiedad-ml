"""
API Flask para predicción de riesgo de ansiedad.

Carga 6 modelos de Machine Learning (.pkl) y expone un endpoint REST
para recibir los datos del cuestionario y retornar la predicción
del nivel de riesgo de ansiedad (ALTO o BAJO) usando Ensemble por votos.

Los modelos fueron entrenados únicamente con 7 variables en formato PascalCase:
  PHQ9, GAD7, OnlineStress, FinancialStress, ExerciseFreq, SocialActivity, SleepHours

El backend Java envía 15 variables en camelCase. Este servicio:
  1. Valida las 15 variables camelCase
  2. Mapea las 7 necesarias a PascalCase para los modelos
  3. Ejecuta los 6 modelos y cada uno vota ALTO o BAJO
  4. Retorna nivel de riesgo por mayoría + recomendaciones personalizadas

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


def ejecutar_prediccion(features_df):
    """
    Ejecuta la predicción usando Ensemble por votos de los 6 modelos ML.

    Cada modelo predice ALTO (1) o BAJO (0).
    El resultado final es el que tenga más votos.
    La confianza = modelos que votaron ganador / total de modelos.
    """
    # 1. Cada modelo vota ALTO o BAJO
    # IMPORTANTE: Los modelos fueron entrenados con:
    #   clase 0 = ALTO riesgo, clase 1 = BAJO riesgo
    # Por lo tanto, invertimos la interpretación.
    votos = {"ALTO": 0, "BAJO": 0}
    predicciones = {}
    probabilidades = {}

    for model_name, model in models.items():
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features_df)
                prob_clase_1 = float(proba[0][1])  # Probabilidad de clase 1 (BAJO)
                probabilidades[display_name] = prob_clase_1

                # Predicción binaria: prob_clase_1 >= 0.5 → BAJO, sino → ALTO
                # (invertido porque clase 0 = ALTO, clase 1 = BAJO)
                nivel = "BAJO" if prob_clase_1 >= 0.5 else "ALTO"
                predicciones[display_name] = nivel
                votos[nivel] += 1

                print(f"  {display_name}: prob_BAJO={prob_clase_1:.4f} → {nivel}")
            else:
                # Modelos sin predict_proba (usar predict directo)
                raw_pred = model.predict(features_df)
                label = int(raw_pred[0])
                nivel = "BAJO" if label == 1 else "ALTO"
                predicciones[display_name] = nivel
                votos[nivel] += 1

                print(f"  {display_name}: predicción_cruda={label} → {nivel}")
        except Exception as e:
            print(f"  ⚠️ Error en {display_name}: {str(e)}")

    # 2. Determinar resultado por mayoría de votos
    total_modelos = sum(votos.values())
    if total_modelos == 0:
        nivel_riesgo = "BAJO"
        confianza = 0.0
    else:
        if votos["ALTO"] > votos["BAJO"]:
            nivel_riesgo = "ALTO"
            confianza = votos["ALTO"] / total_modelos
        elif votos["BAJO"] > votos["ALTO"]:
            nivel_riesgo = "BAJO"
            confianza = votos["BAJO"] / total_modelos
        else:
            # Empate: usar la probabilidad promedio para decidir
            promedio_prob = np.mean(list(probabilidades.values())) if probabilidades else 0.5
            nivel_riesgo = "BAJO" if promedio_prob >= 0.5 else "ALTO"
            confianza = 0.5  # Empate = confianza baja

    # Redondear confianza a 2 decimales
    confianza = round(confianza, 2)

    print(f"\n  Resultado final: {nivel_riesgo}")
    print(f"  Votos: {votos}")
    print(f"  Confianza: {confianza}")

    return nivel_riesgo, confianza, votos, predicciones


def get_recomendaciones(nivel_riesgo, features):
    """Genera recomendaciones personalizadas basadas en el nivel y features."""
    recomendaciones = []

    if nivel_riesgo == "ALTO":
        recomendaciones.append("🔴 Se recomienda consultar con un profesional de salud mental de forma urgente.")
        recomendaciones.append("📞 Si estás en crisis, contacta la línea de ayuda: 106 (SALUD MENTAL - Perú).")
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

    nivel_riesgo, confianza, votos, predicciones = ejecutar_prediccion(features_df)
    recomendaciones = get_recomendaciones(nivel_riesgo, data)

    return jsonify({
        "nivel_riesgo": nivel_riesgo,
        "confianza": confianza,
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