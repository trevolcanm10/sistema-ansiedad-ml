package com.tallermovil.backend.controller;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tallermovil.backend.model.MentalHealthStatus;
import com.tallermovil.backend.repository.EvaluacionRepository;
import com.tallermovil.backend.repository.UsuarioRepository;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/admin")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ROLE_ADMIN')")
public class AdminController {

    private final UsuarioRepository usuarioRepository;
    private final EvaluacionRepository evaluacionRepository;

    /** Listar todos los usuarios */
    @GetMapping("/usuarios")
    public List<Map<String, Object>> listarUsuarios() {
        return usuarioRepository.findAll().stream().map(u -> {
            Map<String, Object> map = new java.util.HashMap<>();
            map.put("id", u.getId());
            map.put("nombre", u.getNombre());
            map.put("email", u.getEmail());
            map.put("role", u.getRole().name());
            map.put("edad", u.getEdad());
            map.put("carrera", u.getCarrera());
            map.put("semestre", u.getSemestre());
            return map;
        }).collect(Collectors.toList());
    }

    /** Listar todas las evaluaciones */
    @GetMapping("/evaluaciones")
    public List<Map<String, Object>> listarEvaluaciones() {
        return evaluacionRepository.findAll().stream().map(e -> {
            Map<String, Object> map = new java.util.HashMap<>();
            map.put("id", e.getId());
            map.put("usuarioId", e.getUsuarioId());
            map.put("nivelRiesgo", e.getMentalHealthStatus() != null
                    ? e.getMentalHealthStatus().name() : "NO_DISPONIBLE");
            map.put("confianza", e.getConfianza());
            map.put("fecha", e.getFecha() != null ? e.getFecha().toString() : "");
            return map;
        }).collect(Collectors.toList());
    }

    /** Estadísticas generales */
    @GetMapping("/stats")
    public Map<String, Object> estadisticas() {
        long totalUsuarios = usuarioRepository.count();
        long totalEvaluaciones = evaluacionRepository.count();
        long riesgoAlto = evaluacionRepository.findAll().stream()
                .filter(e -> e.getMentalHealthStatus() == MentalHealthStatus.HIGH)
                .count();
        long riesgoBajo = evaluacionRepository.findAll().stream()
                .filter(e -> e.getMentalHealthStatus() == MentalHealthStatus.LOW)
                .count();
        long riesgoModerado = evaluacionRepository.findAll().stream()
                .filter(e -> e.getMentalHealthStatus() == MentalHealthStatus.MODERATE)
                .count();

        return Map.of(
                "totalUsuarios", totalUsuarios,
                "totalEvaluaciones", totalEvaluaciones,
                "riesgoAlto", riesgoAlto,
                "riesgoModerado", riesgoModerado,
                "riesgoBajo", riesgoBajo
        );
    }
}