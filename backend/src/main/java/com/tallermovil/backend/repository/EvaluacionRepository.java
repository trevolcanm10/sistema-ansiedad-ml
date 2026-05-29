package com.tallermovil.backend.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.tallermovil.backend.model.Evaluacion;

public interface EvaluacionRepository extends JpaRepository<Evaluacion, Long> {

    /**
     * Busca la evaluación más reciente de un usuario por su ID.
     * 
     * @param usuarioId ID del usuario
     * @return Optional con la última evaluación, o vacío si no tiene
     */
    Optional<Evaluacion> findTopByUsuarioIdOrderByFechaDesc(Long usuarioId);
}
