package com.tallermovil.backend;

import java.util.List;

import org.springframework.stereotype.Service;

import com.tallermovil.backend.model.Evaluacion;
import com.tallermovil.backend.repository.EvaluacionRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class EvaluacionService {

    private final EvaluacionRepository evaluacionRepository;

    public List<Evaluacion> listarTodas() {
        return evaluacionRepository.findAll();
    }

    public Evaluacion guardar(Evaluacion evaluacion) {
        return evaluacionRepository.save(evaluacion);
    }
}