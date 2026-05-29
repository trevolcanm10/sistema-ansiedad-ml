"""
API Flask para predicción de riesgo de ansiedad.

Carga 6 modelos de Machine Learning (.pkl) y expone un endpoint REST
para recibir los datos del cuestionario y retornar la predicción
del nivel de riesgo de ansiedad (BAJO, MODERADO, ALTO).

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
CORS(app)  # Permitir peticiones CORS desde el backend Java

# ============================================================
# RUTA DONDE ESTÁN LOS MODELOS
# ============================================================

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# ============================================================
# NOMBRES DE LOS FEATURES (en el orden que espera el modelo)
# ============================================================

FEATURE_NAMES = [
    "phq9",
    "gad7",
    "sleepHours",
    "exerciseFreq",
    "socialActivity",
    "onlineStress",
    "gpa",
    "familySupport",
    "screenTime",
    "academicStress",
    "dietQuality",
    "selfEfficacy",
    "peerRelationship",
    "financialStress",
    "sleepQuality",
]

# ============================================================
# MAPEO DE PREDICCIÓN A ETIQUETA
# ============================================================

# Los modelos pueden retornar 0, 1, 2 (clases numéricas)
# o strings directos. Este mapeo convierte números a etiquetas.
LABEL_MAP = {
    0: "BAJO",
    1: "MODERADO",
    2: "ALTO",
    "BAJO": "BAJO",
    "MODERADO": "MODERADO",
    "ALTO": "ALTO",
    "Low": "BAJO",
    "Medium": "MODERADO",
    "High": "ALTO",
    "LOW": "BAJO",
    "MEDIUM": "MODERADO",
    "HIGH": "ALTO",
    "Bajo": "BAJO",
    "Moderado": "MODERADO",
    "Alto": "ALTO",
}

# ============================================================
# NOMBRES AMIGABLES DE LOS MODELOS
# ============================================================

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
                display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
                print(f"  ✅ {display_name} cargado correctamente")
            except Exception as e:
                print(f"  ❌ Error cargando {filename}: {str(e)}")

    print("=" * 60)
    print(f"Total modelos cargados: {len(models)}/{len(os.listdir(MODELS_DIR))}")
    print("=" * 60)


# Cargar modelos al arrancar
load_models()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalize_label(raw_prediction):
    """Convierte la predicción cruda del modelo a una etiqueta estándar."""
    if isinstance(raw_prediction, (np.ndarray, list)):
        raw_prediction = raw_prediction[0]

    # Si es un número, convertir a entero
    if isinstance(raw_prediction, (np.floating, float)):
        raw_prediction = int(round(float(raw_prediction)))
    elif isinstance(raw_prediction, (np.integer, int)):
        raw_prediction = int(raw_prediction)

    return LABEL_MAP.get(raw_prediction, str(raw_prediction))


def get_recomendaciones(nivel_riesgo, features):
    """
    Genera recomendaciones personalizadas basadas en el nivel de riesgo
    y los valores específicos del cuestionario del usuario.
    """
    recomendaciones = []

    # Recomendaciones generales por nivel
    if nivel_riesgo == "ALTO":
        recomendaciones.append(
            "🔴 Se recomienda consultar con un profesional de salud mental de forma urgente."
        )
        recomendaciones.append(
            "📞 Si estás en crisis, contacta la línea de ayuda: 106 (SALUD MENTAL - Perú)."
        )
    elif nivel_riesgo == "MODERADO":
        recomendaciones.append(
            "🟡 Considera agendar una cita con el orientador psicológico de tu universidad."
        )
        recomendaciones.append(
            "📝 Lleva un diario emocional para identificar tus patrones de estrés."
        )
    else:
        recomendaciones.append(
            "🟢 Tu nivel de riesgo es bajo. ¡Sigue cuidando tu bienestar!"
        )

    # Recomendaciones específicas por feature
    if features.get("sleepHours", 8) < 6:
        recomendaciones.append(
            "😴 Intenta dormir al menos 7-8 horas. La falta de sueño afecta directamente la ansiedad."
        )

    if features.get("sleepQuality", 5) < 4:
        recomendaciones.append(
            "🛏️ Tu calidad de sueño es baja. Evita pantallas 1 hora antes de dormir."
        )

    if features.get("exerciseFreq", 3) < 2:
        recomendaciones.append(
            "🏃 Realiza actividad física al menos 3 veces por semana. El ejercicio reduce la ansiedad."
        )

    if features.get("screenTime", 5) > 8:
        recomendaciones.append(
            "📱 Tu tiempo de pantalla es alto. Intenta reducirlo y tomarte descansos digitales."
        )

    if features.get("socialActivity", 5) < 3:
        recomendaciones.append(
            "👥 Intenta socializar más. Las relaciones sociales son un factor protector importante."
        )

    if features.get("academicStress", 5) > 7:
        recomendaciones.append(
            "📚 Tu estrés académico es alto. Considera organizar tu tiempo con un plan de estudio."
        )

    if features.get("dietQuality", 5) < 4:
        recomendaciones.append(
            "🥗 Mejora tu alimentación. Una dieta balanceada influye positivamente en tu salud mental."
        )

    if features.get("financialStress", 5) > 7:
        recomendaciones.append(
            "💰 El estrés financiero es significativo. Busca apoyo en programas de becas o asesoría."
        )

    if features.get("familySupport", 5) < 3:
        recomendaciones.append(
            "👨‍👩‍👧 Busca apoyo en tu círculo familiar o en personas de confianza."
        )

    if features.get("selfEfficacy", 5) < 4:
        recomendaciones.append(
            "💪 Trabaja en tu autoestima. Establece metas pequeñas y celebra cada logro."
        )

    if features.get("onlineStress", 5) > 7:
        recomendaciones.append(
            "🌐 El estrés digital es alto. Considera tomar descansos de redes sociales."
        )

    return recomendaciones


# ============================================================
# ENDPOINTS DE LA API
# ============================================================

@app.route("/", methods=["GET"])
def index():
    """Endpoint de prueba para verificar que el servicio está corriendo."""
    return jsonify({
        "service": "ML Prediction Service",
        "status": "running",
        "models_loaded": len(models),
        "models": [MODEL_DISPLAY_NAMES.get(m, m) for m in models_loaded],
    })


@app.route("/health", methods=["GET"])
def health():
    """Endpoint de health check para Docker."""
    return jsonify({"status": "healthy", "models_count": len(models)})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint principal de predicción.

    Recibe un JSON con los 15 features del cuestionario y retorna
    la predicción del nivel de riesgo de ansiedad usando voto mayoritario
    de los 6 modelos.

    Body esperado:
    {
        "phq9": 5.0,
        "gad7": 8.0,
        "sleepHours": 6.0,
        "exerciseFreq": 2.0,
        "socialActivity": 5.0,
        "onlineStress": 7.0,
        "gpa": 8.5,
        "familySupport": 7.0,
        "screenTime": 6.0,
        "academicStress": 6.0,
        "dietQuality": 5.0,
        "selfEfficacy": 5.0,
        "peerRelationship": 6.0,
        "financialStress": 4.0,
        "sleepQuality": 5.0
    }
    """

    # Verificar que hay modelos cargados
    if not models:
        return jsonify({
            "error": "No hay modelos cargados en el servidor"
        }), 500

    # Obtener datos del request
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No se recibieron datos. Envía un JSON con los 15 features."
        }), 400

    # Verificar que todos los features estén presentes
    missing_features = [f for f in FEATURE_NAMES if f not in data]
    if missing_features:
        return jsonify({
            "error": f"Faltan los siguientes campos: {', '.join(missing_features)}"
        }), 400

    # Extraer features en el orden correcto
    features = []
    for feature_name in FEATURE_NAMES:
        try:
            value = float(data[feature_name])
            features.append(value)
        except (ValueError, TypeError):
            return jsonify({
                "error": f"El campo '{feature_name}' debe ser un número. Valor recibido: {data[feature_name]}"
            }), 400

    # Crear DataFrame para predicción
    features_array = np.array([features])
    features_df = pd.DataFrame([features], columns=FEATURE_NAMES)

    # Ejecutar predicción con cada modelo
    predicciones = {}
    votos = {"BAJO": 0, "MODERADO": 0, "ALTO": 0}

    for model_name, model in models.items():
        try:
            raw_pred = model.predict(features_df)
            label = normalize_label(raw_pred)
            predicciones[MODEL_DISPLAY_NAMES.get(model_name, model_name)] = label
            if label in votos:
                votos[label] += 1
            else:
                votos[label] = votos.get(label, 0) + 1
        except Exception as e:
            display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
            predicciones[display_name] = f"Error: {str(e)}"

    # Calcular predicción final por voto mayoritario
    nivel_riesgo = max(votos, key=votos.get)

    # Calcular confianza (porcentaje de modelos que votaron por el ganador)
    modelos_validos = sum(1 for v in predicciones.values() if not str(v).startswith("Error"))
    confianza = round(votos[nivel_riesgo] / modelos_validos, 2) if modelos_validos > 0 else 0.0

    # Generar recomendaciones personalizadas
    recomendaciones = get_recomendaciones(nivel_riesgo, data)

    # Construir respuesta
    response = {
        "nivel_riesgo": nivel_riesgo,
        "confianza": confianza,
        "votos": votos,
        "predicciones": predicciones,
        "recomendaciones": recomendaciones,
    }

    return jsonify(response)


@app.route("/predict/<model_name>", methods=["POST"])
def predict_single(model_name):
    """
    Predicción con un modelo específico.

    Permite seleccionar qué modelo usar en lugar del voto mayoritario.
    """
    if not models:
        return jsonify({"error": "No hay modelos cargados"}), 500

    # Buscar el modelo por nombre (acepta tanto el nombre interno como el display)
    found_model = None
    found_key = None

    for key in models:
        display = MODEL_DISPLAY_NAMES.get(key, key)
        if key == model_name or display.lower().replace(" ", "_") == model_name.lower().replace(" ", "_"):
            found_model = models[key]
            found_key = key
            break

    if not found_model:
        available = [MODEL_DISPLAY_NAMES.get(k, k) for k in models]
        return jsonify({
            "error": f"Modelo '{model_name}' no encontrado",
            "modelos_disponibles": available
        }), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Envía un JSON con los 15 features"}), 400

    missing = [f for f in FEATURE_NAMES if f not in data]
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

    features = [float(data[f]) for f in FEATURE_NAMES]
    features_df = pd.DataFrame([features], columns=FEATURE_NAMES)

    try:
        raw_pred = found_model.predict(features_df)
        label = normalize_label(raw_pred)

        return jsonify({
            "modelo": MODEL_DISPLAY_NAMES.get(found_key, found_key),
            "nivel_riesgo": label,
        })
    except Exception as e:
        return jsonify({"error": f"Error en predicción: {str(e)}"}), 500


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Servicio ML iniciado en http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)