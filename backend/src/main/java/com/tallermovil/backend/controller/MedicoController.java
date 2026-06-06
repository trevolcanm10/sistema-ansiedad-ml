package com.tallermovil.backend.controller;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tallermovil.backend.model.Usuario;
import com.tallermovil.backend.repository.EvaluacionRepository;
import com.tallermovil.backend.repository.UsuarioRepository;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/medico")
@RequiredArgsConstructor
@PreAuthorize("hasAuthority('ROLE_MEDICO')")
public class MedicoController {

    private final EvaluacionRepository evaluacionRepository;
    private final UsuarioRepository usuarioRepository;

    /** Listar todos los estudiantes con su última evaluación */
    @GetMapping("/estudiantes")
    public List<Map<String, Object>> listarEstudiantes() {
        List<Usuario> estudiantes = usuarioRepository.findAll().stream()
                .filter(u -> u.getRole() == com.tallermovil.backend.model.Role.ROLE_ESTUDIANTE)
                .collect(Collectors.toList());

        return estudiantes.stream().map(est -> {
            Map<String, Object> map = new java.util.HashMap<>();
            map.put("id", est.getId());
            map.put("nombre", est.getNombre());
            map.put("email", est.getEmail());
            map.put("carrera", est.getCarrera());
            map.put("semestre", est.getSemestre());

            // Buscar última evaluación
            evaluacionRepository.findTopByUsuarioIdOrderByFechaDesc(est.getId())
                    .ifPresent(e -> {
                        map.put("ultimoNivel", e.getMentalHealthStatus() != null
                                ? e.getMentalHealthStatus().name() : "SIN_EVALUAR");
                        map.put("ultimaFecha", e.getFecha() != null ? e.getFecha().toString() : "");
                        map.put("confianza", e.getConfianza());
                    });

            if (!map.containsKey("ultimoNivel")) {
                map.put("ultimoNivel", "SIN_EVALUAR");
                map.put("ultimaFecha", "");
                map.put("confianza", 0.0);
            }

            return map;
        }).collect(Collectors.toList());
    }

    /** Ver evaluaciones de un estudiante específico */
    @GetMapping("/estudiantes/{estudianteId}/evaluaciones")
    public List<Map<String, Object>> verEvaluacionesEstudiante(@PathVariable Long estudianteId) {
        return evaluacionRepository.findAll().stream()
                .filter(e -> e.getUsuarioId().equals(estudianteId))
                .sorted((a, b) -> b.getFecha().compareTo(a.getFecha()))
                .map(e -> {
                    Map<String, Object> map = new java.util.HashMap<>();
                    map.put("id", e.getId());
                    map.put("nivelRiesgo", e.getMentalHealthStatus() != null
                            ? e.getMentalHealthStatus().name() : "NO_DISPONIBLE");
                    map.put("confianza", e.getConfianza());
                    map.put("fecha", e.getFecha() != null ? e.getFecha().toString() : "");
                    map.put("phq9", e.getPhq9());
                    map.put("gad7", e.getGad7());
                    map.put("sleepHours", e.getSleepHours());
                    return map;
                })
                .collect(Collectors.toList());
    }
}