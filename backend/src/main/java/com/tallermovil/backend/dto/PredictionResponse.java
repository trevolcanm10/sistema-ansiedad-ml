package com.tallermovil.backend.dto;

import java.util.List;
import java.util.Map;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * DTO que representa la respuesta del servicio ML (Flask API).
 * 
 * Ejemplo de respuesta:
 * {
 *   "nivel_riesgo": "ALTO",
 *   "confianza": 0.83,
 *   "votos": {"ALTO": 5, "BAJO": 1},
 *   "predicciones": {"Random Forest": "ALTO", "XGBoost": "BAJO", ...},
 *   "recomendaciones": ["Recomendación 1", "Recomendación 2", ...]
 * }
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class PredictionResponse {

    /** Nivel de riesgo final (ALTO o BAJO) */
    private String nivel_riesgo;

    /** Confianza de la predicción (0.0 a 1.0) */
    private Double confianza;

    /** Votos de cada modelo por categoría */
    private Map<String, Integer> votos;

    /** Predicción individual de cada modelo (puede ser String o Map anidado) */
    private Map<String, Object> predicciones;

    /** Lista de recomendaciones personalizadas */
    private List<String> recomendaciones;
}