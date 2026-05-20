package com.tallermovil.backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.tallermovil.backend.model.Evaluacion;
public interface EvaluacionRepository extends JpaRepository<Evaluacion, Long> {
}
