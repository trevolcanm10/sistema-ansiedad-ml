"""
Script de testing de rendimiento para los modelos de predicción de ansiedad.

Carga los 6 modelos .pkl y evalúa su rendimiento individual y colectivo
usando datos sintéticos basados en rangos clínicos válidos.

Ejecutar: python ml/test_models.py
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

# ============================================================
# CONFIGURACIÓN
# ============================================================

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

MODEL_FEATURES = ["PHQ9", "GAD7", "OnlineStress", "FinancialStress",
                   "ExerciseFreq", "SocialActivity", "SleepHours"]

MODEL_DISPLAY_NAMES = {
    "random_forest_model": "Random Forest",
    "xgboost_weighted_model": "XGBoost",
    "lightgbm_model": "LightGBM",
    "catboost_weighted_model": "CatBoost",
    "knn_model": "KNN",
    "logistic_regression_model": "Logistic Regression",
}

# ============================================================
# GENERACIÓN DE DATOS SINTÉTICOS
# ============================================================

def generar_datos_sinteticos(n_por_clase=100, seed=42):
    """
    Genera datos sintéticos basados en rangos clínicos válidos.
    
    Clase 0 = BAJO riesgo (datos que indican buena salud mental)
    Clase 1 = ALTO riesgo (datos que indican riesgo de ansiedad)
    
    Rangos según instrumentos clínicos:
    - PHQ-9: 0-27 (depresión, >10 = moderada-severa)
    - GAD-7: 0-21 (ansiedad, >10 = moderada-severa)
    - OnlineStress: 0-10
    - FinancialStress: 0-10
    - ExerciseFreq: 0-7 (días por semana)
    - SocialActivity: 0-10
    - SleepHours: 0-12
    """
    np.random.seed(seed)
    
    datos = []
    etiquetas = []
    
    # --- CLASE 0: BAJO RIESGO ---
    for _ in range(n_por_clase):
        phq9 = np.random.uniform(0, 9)        # Bajo: 0-9
        gad7 = np.random.uniform(0, 9)         # Bajo: 0-9
        online_stress = np.random.uniform(0, 5)
        financial_stress = np.random.uniform(0, 4)
        exercise_freq = np.random.uniform(3, 7)  # Hace ejercicio regular
        social_activity = np.random.uniform(5, 10)  # Buena socialización
        sleep_hours = np.random.uniform(6, 9)   # Duerme bien
        
        datos.append([phq9, gad7, online_stress, financial_stress,
                      exercise_freq, social_activity, sleep_hours])
        etiquetas.append(0)  # BAJO
    
    # --- CLASE 1: ALTO RIESGO ---
    for _ in range(n_por_clase):
        phq9 = np.random.uniform(12, 27)       # Alto: 12-27
        gad7 = np.random.uniform(11, 21)       # Alto: 11-21
        online_stress = np.random.uniform(6, 10)
        financial_stress = np.random.uniform(6, 10)
        exercise_freq = np.random.uniform(0, 2)  # Poco ejercicio
        social_activity = np.random.uniform(0, 4)  # Aislamiento
        sleep_hours = np.random.uniform(3, 6)   # Poco sueño
        
        datos.append([phq9, gad7, online_stress, financial_stress,
                      exercise_freq, social_activity, sleep_hours])
        etiquetas.append(1)  # ALTO
    
    X = pd.DataFrame(datos, columns=MODEL_FEATURES)
    y = np.array(etiquetas)
    
    return X, y


# ============================================================
# CARGA DE MODELOS
# ============================================================

def cargar_modelos():
    """Carga todos los modelos .pkl desde la carpeta models/."""
    modelos = {}
    print("=" * 60)
    print("CARGANDO MODELOS")
    print("=" * 60)
    for filename in sorted(os.listdir(MODELS_DIR)):
        if filename.endswith(".pkl"):
            model_name = filename.replace(".pkl", "")
            filepath = os.path.join(MODELS_DIR, filename)
            try:
                model = joblib.load(filepath)
                modelos[model_name] = model
                print(f"  ✅ {MODEL_DISPLAY_NAMES.get(model_name, model_name)}")
            except Exception as e:
                print(f"  ❌ Error cargando {filename}: {str(e)}")
    print(f"\nTotal modelos cargados: {len(modelos)}")
    return modelos


# ============================================================
# EVALUACIÓN INDIVIDUAL
# ============================================================

def evaluar_modelo_individual(modelo, nombre, X_test, y_test):
    """Evalúa un modelo individual y retorna métricas."""
    try:
        # Predicción
        # IMPORTANTE: Los modelos tienen invertidas las etiquetas:
        # clase 0 = ALTO riesgo, clase 1 = BAJO riesgo
        y_pred = modelo.predict(X_test)
        y_pred = y_pred.astype(int)
        y_pred = np.where(y_pred == 1, 0, 1)  # Invertir: 1→0(BAJO), 0→1(ALTO)
        
        # Probabilidades (si disponible)
        probabilidades = None
        if hasattr(modelo, "predict_proba"):
            probabilidades = modelo.predict_proba(X_test)
        
        # Métricas
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        return {
            "nombre": nombre,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "y_pred": y_pred,
            "probabilidades": probabilidades,
            "error": None
        }
    except Exception as e:
        return {
            "nombre": nombre,
            "accuracy": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
            "y_pred": None,
            "probabilidades": None,
            "error": str(e)
        }


# ============================================================
# EVALUACIÓN DEL ENSEMBLE
# ============================================================

def evaluar_ensemble(modelos, X_test, y_test):
    """
    Evalúa el ensemble por votos (mismo método que predict.py).
    Cada modelo vota ALTO (1) o BAJO (0), gana la mayoría.
    """
    n_samples = len(X_test)
    votos_alto = np.zeros(n_samples)
    votos_bajo = np.zeros(n_samples)
    
    print("\n--- Probabilidades de un caso ALTO (primera instancia de test) ---")
    caso_alto = X_test.iloc[0:1]
    
    for model_name, model in modelos.items():
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        try:
            y_pred_raw = model.predict(X_test).astype(int)
            # Invertir: clase 0 = ALTO, clase 1 = BAJO
            y_pred = np.where(y_pred_raw == 1, 0, 1)
            votos_alto += (y_pred == 1)
            votos_bajo += (y_pred == 0)
            
            # Mostrar probabilidad del primer caso
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(caso_alto)
                print(f"  {display_name}: P(BAJO)={proba[0][1]:.4f}, P(ALTO)={proba[0][0]:.4f}")
        except Exception as e:
            print(f"  ⚠️ Error en {display_name}: {str(e)}")
    
    # Decisión por mayoría
    y_pred_ensemble = np.where(votos_alto > votos_bajo, 1, 0)
    
    # Empates → predecir BAJO (conservador)
    empates = votos_alto == votos_bajo
    y_pred_ensemble[empates] = 0
    
    # Métricas del ensemble
    accuracy = accuracy_score(y_test, y_pred_ensemble)
    precision = precision_score(y_test, y_pred_ensemble, zero_division=0)
    recall = recall_score(y_test, y_pred_ensemble, zero_division=0)
    f1 = f1_score(y_test, y_pred_ensemble, zero_division=0)
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "y_pred": y_pred_ensemble,
        "votos_alto": votos_alto,
        "votos_bajo": votos_bajo
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("  TEST DE RENDIMIENTO DE MODELOS DE ANSIEDAD")
    print("=" * 60)
    
    # 1. Cargar modelos
    modelos = cargar_modelos()
    if not modelos:
        print("\n❌ No se cargaron modelos. Verifica la carpeta models/")
        return
    
    # 2. Generar datos sintéticos
    print("\n" + "-" * 60)
    print("GENERANDO DATOS SINTÉTICOS")
    print("-" * 60)
    X, y = generar_datos_sinteticos(n_por_clase=200, seed=42)
    print(f"  Total muestras: {len(X)}")
    print(f"  Clase BAJO (0): {sum(y == 0)}")
    print(f"  Clase ALTO (1): {sum(y == 1)}")
    print(f"  Features: {MODEL_FEATURES}")
    
    # 3. Split train/test (80/20)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n  Train: {len(X_train)} muestras")
    print(f"  Test:  {len(X_test)} muestras")
    
    # 4. Evaluar cada modelo individualmente
    print("\n" + "=" * 60)
    print("RENDIMIENTO INDIVIDUAL DE CADA MODELO")
    print("=" * 60)
    
    resultados = []
    for model_name, model in modelos.items():
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        resultado = evaluar_modelo_individual(model, display_name, X_test, y_test)
        resultados.append(resultado)
        
        if resultado["error"]:
            print(f"\n  ❌ {display_name}: ERROR - {resultado['error']}")
        else:
            print(f"\n  📊 {display_name}:")
            print(f"     Accuracy:  {resultado['accuracy']:.4f} ({resultado['accuracy']*100:.1f}%)")
            print(f"     Precision: {resultado['precision']:.4f}")
            print(f"     Recall:    {resultado['recall']:.4f}")
            print(f"     F1-Score:  {resultado['f1']:.4f}")
    
    # 5. Evaluar Ensemble
    print("\n" + "=" * 60)
    print("RENDIMIENTO DEL ENSEMBLE (VOTOS)")
    print("=" * 60)
    
    ensemble = evaluar_ensemble(modelos, X_test, y_test)
    print(f"\n  🏆 ENSEMBLE:")
    print(f"     Accuracy:  {ensemble['accuracy']:.4f} ({ensemble['accuracy']*100:.1f}%)")
    print(f"     Precision: {ensemble['precision']:.4f}")
    print(f"     Recall:    {ensemble['recall']:.4f}")
    print(f"     F1-Score:  {ensemble['f1']:.4f}")
    
    # 6. Matriz de confusión del ensemble
    print("\n--- Matriz de Confusión (Ensemble) ---")
    cm = confusion_matrix(y_test, ensemble["y_pred"])
    print(f"  Predicted BAJO  Predicted ALTO")
    print(f"  Actual BAJO:    {cm[0][0]:>4}          {cm[0][1]:>4}")
    print(f"  Actual ALTO:    {cm[1][0]:>4}          {cm[1][1]:>4}")
    
    # 7. Resumen
    print("\n" + "=" * 60)
    print("RESUMEN COMPARATIVO")
    print("=" * 60)
    print(f"\n  {'Modelo':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print("  " + "-" * 65)
    
    for r in resultados:
        if not r["error"]:
            print(f"  {r['nombre']:<25} {r['accuracy']*100:>9.1f}% {r['precision']*100:>9.1f}% {r['recall']*100:>9.1f}% {r['f1']*100:>9.1f}%")
    
    print("  " + "-" * 65)
    print(f"  {'🏆 ENSEMBLE':<25} {ensemble['accuracy']*100:>9.1f}% {ensemble['precision']*100:>9.1f}% {ensemble['recall']*100:>9.1f}% {ensemble['f1']*100:>9.1f}%")
    
    # 8. Verificar predicción de un caso conocido
    print("\n" + "=" * 60)
    print("VERIFICACIÓN CON CASOS REALES")
    print("=" * 60)
    
    # Caso 1: Estudiante sano
    caso_bajo = pd.DataFrame([{
        "PHQ9": 3, "GAD7": 2, "OnlineStress": 2, "FinancialStress": 1,
        "ExerciseFreq": 5, "SocialActivity": 8, "SleepHours": 8
    }])
    
    # Caso 2: Estudiante con riesgo alto
    caso_alto = pd.DataFrame([{
        "PHQ9": 20, "GAD7": 18, "OnlineStress": 9, "FinancialStress": 8,
        "ExerciseFreq": 1, "SocialActivity": 2, "SleepHours": 4
    }])
    
    print("\n  🟢 CASO BAJO (estudiante sano):")
    print("     PHQ9=3, GAD7=2, ExerciseFreq=5, SleepHours=8")
    votos_bajo = 0
    votos_alto = 0
    for model_name, model in modelos.items():
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        try:
            pred = model.predict(caso_bajo)[0]
            # Invertir: clase 0 = ALTO, clase 1 = BAJO
            nivel = "BAJO" if pred == 1 else "ALTO"
            if nivel == "ALTO":
                votos_alto += 1
            else:
                votos_bajo += 1
            print(f"     {display_name}: {nivel}")
        except:
            pass
    resultado_bajo = "ALTO" if votos_alto > votos_bajo else "BAJO"
    print(f"     → Resultado ensemble: {resultado_bajo} (ALTO={votos_alto}, BAJO={votos_bajo})")
    
    print("\n  🔴 CASO ALTO (estudiante en riesgo):")
    print("     PHQ9=20, GAD7=18, ExerciseFreq=1, SleepHours=4")
    votos_bajo = 0
    votos_alto = 0
    for model_name, model in modelos.items():
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        try:
            pred = model.predict(caso_alto)[0]
            # Invertir: clase 0 = ALTO, clase 1 = BAJO
            nivel = "BAJO" if pred == 1 else "ALTO"
            if nivel == "ALTO":
                votos_alto += 1
            else:
                votos_bajo += 1
            print(f"     {display_name}: {nivel}")
        except:
            pass
    resultado_alto = "ALTO" if votos_alto > votos_bajo else "BAJO"
    print(f"     → Resultado ensemble: {resultado_alto} (ALTO={votos_alto}, BAJO={votos_bajo})")
    
    print("\n" + "=" * 60)
    print("  TEST COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()