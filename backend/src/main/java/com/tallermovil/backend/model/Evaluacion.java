package com.tallermovil.backend.model;

import java.time.LocalDateTime;

import jakarta.persistence.Entity;
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

    private LocalDateTime fecha;
}
