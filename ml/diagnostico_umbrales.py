"""
Script de diagnóstico para determinar los umbrales reales de P(BAJO).
Barre combinaciones de PHQ9 y GAD7 para ver cómo se comportan los modelos.

Ejecutar: python ml/diagnostico_umbrales.py
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd

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

# Valores neutrales para las variables que no estamos variando
VALORES_NEUTRALES = {
    "OnlineStress": 5,
    "FinancialStress": 5,
    "ExerciseFreq": 3,
    "SocialActivity": 5,
    "SleepHours": 7,
}

# ============================================================
# CARGA DE MODELOS
# ============================================================

def cargar_modelos():
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
    print(f"\nTotal: {len(modelos)} modelos cargados")
    return modelos


def predecir_p_bajo(modelos, phq9, gad7):
    """Calcula P(BAJO) promedio para una combinación PHQ9/GAD7."""
    caso = pd.DataFrame([{
        "PHQ9": phq9,
        "GAD7": gad7,
        "OnlineStress": VALORES_NEUTRALES["OnlineStress"],
        "FinancialStress": VALORES_NEUTRALES["FinancialStress"],
        "ExerciseFreq": VALORES_NEUTRALES["ExerciseFreq"],
        "SocialActivity": VALORES_NEUTRALES["SocialActivity"],
        "SleepHours": VALORES_NEUTRALES["SleepHours"],
    }])
    
    probabilidades = {}
    for model_name, model in modelos.items():
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(caso)
                prob_bajo = float(proba[0][1])  # P(BAJO)
                probabilidades[display_name] = prob_bajo
            else:
                raw_pred = int(model.predict(caso)[0])
                probabilidades[display_name] = 1.0 if raw_pred == 1 else 0.0
        except Exception as e:
            probabilidades[display_name] = -1
    
    promedio = float(np.mean(list(probabilidades.values())))
    return promedio, probabilidades


# ============================================================
# BARRIDO COMPLETO
# ============================================================

def barrido_completo(modelos):
    """
    Barre todas las combinaciones de PHQ9 (0-27) y GAD7 (0-21)
    y muestra P(BAJO) promedio para cada una.
    """
    print("\n" + "=" * 60)
    print("BARRIDO PHQ9 x GAD7 - P(BAJO) PROMEDIO")
    print("=" * 60)
    
    # Valores fijos para otras variables (neutros)
    otros_fijos = ", ".join([f"{k}={v}" for k, v in VALORES_NEUTRALES.items()])
    print(f"Valores fijos: {otros_fijos}")
    
    phq9_values = list(range(0, 28, 3))  # 0, 3, 6, 9, 12, 15, 18, 21, 24, 27
    gad7_values = list(range(0, 22, 3))  # 0, 3, 6, 9, 12, 15, 18, 21
    
    # Encabezado
    print(f"\n{'PHQ9':>5}", end="")
    for g in gad7_values:
        print(f"  GAD7={g:>2}", end="")
    print()
    print(" " * 5 + "-" * (len(gad7_values) * 10))
    
    for p in phq9_values:
        print(f"{p:>5}", end="")
        for g in gad7_values:
            promedio, _ = predecir_p_bajo(modelos, p, g)
            print(f"   {promedio:.2%}", end="")
        print()
    
    return phq9_values, gad7_values


def barrido_detallado_phq9(modelos, gad7_fijo):
    """
    Barre PHQ9 de 0 a 27 con un GAD7 fijo,
    mostrando P(BAJO) de cada modelo individualmente.
    """
    print(f"\n\n" + "=" * 60)
    print(f"DETALLE POR MODELO - GAD7={gad7_fijo}")
    print("=" * 60)
    
    phq9_values = list(range(0, 28, 2))  # 0, 2, 4, ..., 26
    
    # Encabezado
    headers = ["PHQ9"] + list(MODEL_DISPLAY_NAMES.values()) + ["PROMEDIO"]
    print(f"\n{'PHQ9':>5}", end="")
    for h in MODEL_DISPLAY_NAMES.values():
        print(f"  {h:>20}", end="")
    print("  PROMEDIO")
    print(" " * 5 + "-" * (len(MODEL_DISPLAY_NAMES) * 23 + 10))
    
    for p in phq9_values:
        promedio, probs = predecir_p_bajo(modelos, p, gad7_fijo)
        print(f"{p:>5}", end="")
        for name in MODEL_DISPLAY_NAMES.values():
            prob = probs.get(name, -1)
            print(f"  {prob:>20.4f}", end="")
        print(f"  {promedio:.4f}")


def encontrar_umbrales_recomendados(modelos):
    """
    Encuentra los umbrales recomendados basados en los datos.
    Estrategia:
    - Ejecuta casos claramente BAJO: PHQ9=0, GAD7=0 → debe dar P(BAJO) muy alto
    - Ejecuta casos claramente ALTO: PHQ9=27, GAD7=21 → debe dar P(BAJO) muy bajo
    - Busca el punto donde se empieza a "inclinar" la probabilidad
    """
    print("\n\n" + "=" * 60)
    print("ANÁLISIS DE UMBRALES RECOMENDADOS")
    print("=" * 60)
    
    # Casos extremos
    print("\n--- CASOS EXTREMOS ---")
    casos = [
        ("BAJO extremo", 0, 0),
        ("BAJO suave", 3, 2),
        ("BAJO-moderado", 6, 5),
        ("Moderado-bajo", 9, 7),
        ("Moderado-alto", 12, 10),
        ("ALTO-moderado", 15, 12),
        ("ALTO severo", 20, 18),
        ("ALTO extremo", 27, 21),
    ]
    
    for nombre, p, g in casos:
        promedio, probs = predecir_p_bajo(modelos, p, g)
        votos_bajo = sum(1 for v in probs.values() if v > 0.5)
        votos_alto = len(probs) - votos_bajo
        print(f"\n  {nombre:20} PHQ9={p:>2}, GAD7={g:>2}:")
        print(f"    P(BAJO) promedio: {promedio:.4f} ({promedio:.2%})")
        print(f"    Votos (informativos): ALTO={votos_alto}, BAJO={votos_bajo}")
        for name, prob in probs.items():
            print(f"      {name:25}: P(BAJO)={prob:.4f}")
    
    # Buscar el punto de inflexión de PHQ9 con GAD7 fijo en 7
    print("\n\n--- PUNTO DE INFLEXIÓN (GAD7=7, buscando dónde P(BAJO) cruza 0.50) ---")
    for p in range(0, 28):
        promedio, probs = predecir_p_bajo(modelos, p, 7)
        if promedio < 0.50:
            print(f"  PHQ9={p}, GAD7=7 → P(BAJO)={promedio:.4f} (CRUZA debajo de 0.50)")
            break
        else:
            print(f"  PHQ9={p}, GAD7=7 → P(BAJO)={promedio:.4f}")
    
    # Buscar el punto de inflexión de GAD7 con PHQ9 fijo en 7
    print("\n--- PUNTO DE INFLEXIÓN (PHQ9=7, buscando dónde P(BAJO) cruza 0.50) ---")
    for g in range(0, 22):
        promedio, probs = predecir_p_bajo(modelos, 7, g)
        if promedio < 0.50:
            print(f"  PHQ9=7, GAD7={g} → P(BAJO)={promedio:.4f} (CRUZA debajo de 0.50)")
            break
        else:
            print(f"  PHQ9=7, GAD7={g} → P(BAJO)={promedio:.4f}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  DIAGNÓSTICO DE UMBRALES PARA 3 NIVELES")
    print("=" * 60)
    
    modelos = cargar_modelos()
    if not modelos:
        print("\n❌ No se cargaron modelos. Abortando.")
        sys.exit(1)
    
    # 1. Barrido completo PHQ9 x GAD7 (matriz de P(BAJO) promedio)
    barrido_completo(modelos)
    
    # 2. Detalle por modelo para GAD7 fijo (ver comportamiento individual)
    barrido_detallado_phq9(modelos, gad7_fijo=5)
    barrido_detallado_phq9(modelos, gad7_fijo=10)
    
    # 3. Análisis de umbrales recomendados
    encontrar_umbrales_recomendados(modelos)
    
    print("\n\n" + "=" * 60)
    print("  DIAGNÓSTICO COMPLETADO")
    print("  Revisa los resultados para ajustar UMBRAL_ALTO y UMBRAL_BAJO")
    print("=" * 60)


if __name__ == "__main__":
    main()