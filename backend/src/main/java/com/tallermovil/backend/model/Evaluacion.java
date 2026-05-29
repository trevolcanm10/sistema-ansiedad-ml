package com.tallermovil.backend.model;


import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "evaluacion")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Evaluacion {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long usuarioId;

    // === FEATURES DEL CUESTIONARIO ===
    private Double phq9;
    private Double gad7;
    private Double sleepHours;
    private Double exerciseFreq;
    private Double socialActivity;
    private Double onlineStress;
    private Double gpa;
    private Double familySupport;
    private Double screenTime;
    private Double academicStress;
    private Double dietQuality;
    private Double selfEfficacy;
    private Double peerRelationship;
    private Double financialStress;
    private Double sleepQuality;

    // === RESULTADO DE LA PREDICCIÓN ML ===

    /** Nivel de riesgo predicho por el modelo ML (LOW o HIGH) */
    @Enumerated(EnumType.STRING)
    @Column(name = "mental_health_status")
    private MentalHealthStatus mentalHealthStatus;

    /** Confianza de la predicción (0.0 a 1.0) */
    private Double confianza;

    /** Votos de los modelos como JSON (ej: {"ALTO":5,"BAJO":1}) */
    @Column(columnDefinition = "TEXT")
    private String votosJson;

    /** Predicciones individuales de cada modelo como JSON */
    @Column(columnDefinition = "TEXT")
    private String prediccionesJson;

    /** Fecha y hora de la evaluación */
    private LocalDateTime fecha;
}
