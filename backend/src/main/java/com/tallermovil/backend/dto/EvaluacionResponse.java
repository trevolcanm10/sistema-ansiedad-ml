package com.tallermovil.backend.dto;

import java.util.List;
import java.util.Map;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * DTO que representa la respuesta al crear una evaluación.
 * 
 * Incluye el resultado de la predicción ML, las recomendaciones
 * y los detalles de cada modelo individual.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class EvaluacionResponse {

    /** Mensaje de confirmación */
    private String mensaje;

    /** Nivel de riesgo predicho (BAJO o ALTO) */
    private String nivelRiesgo;

    /** Confianza de la predicción (0.0 a 1.0) */
    private Double confianza;

    /** Votos de cada categoría por parte de los modelos */
    private Map<String, Integer> votos;

    /** Predicción individual de cada modelo */
    private Map<String, String> prediccionesModelos;

    /** Lista de recomendaciones personalizadas */
    private List<String> recomendaciones;
}