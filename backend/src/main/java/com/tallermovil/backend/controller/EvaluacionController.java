package com.tallermovil.backend.controller;

import java.time.LocalDateTime;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tallermovil.backend.dto.EvaluacionRequest;
import com.tallermovil.backend.model.Evaluacion;
import com.tallermovil.backend.model.Usuario;
import com.tallermovil.backend.repository.EvaluacionRepository;
import com.tallermovil.backend.repository.UsuarioRepository;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/evaluacion")
@RequiredArgsConstructor
public class EvaluacionController {

    private final EvaluacionRepository evaluacionRepository;
    private final UsuarioRepository usuarioRepository;

    @PostMapping
    public String crearEvaluacion(
            @RequestBody EvaluacionRequest request,
            Authentication auth
    ) {

        // 1. obtener usuario desde JWT
        String email = auth.getName();

        Usuario usuario = usuarioRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado"));

        // 2. construir entidad Evaluacion
        Evaluacion e = new Evaluacion();
        e.setUsuarioId(usuario.getId());

        e.setPhq9(request.getPhq9());
        e.setGad7(request.getGad7());
        e.setSleepHours(request.getSleepHours());
        e.setExerciseFreq(request.getExerciseFreq());
        e.setSocialActivity(request.getSocialActivity());
        e.setOnlineStress(request.getOnlineStress());
        e.setGpa(request.getGpa());
        e.setFamilySupport(request.getFamilySupport());
        e.setScreenTime(request.getScreenTime());
        e.setAcademicStress(request.getAcademicStress());
        e.setDietQuality(request.getDietQuality());
        e.setSelfEfficacy(request.getSelfEfficacy());
        e.setPeerRelationship(request.getPeerRelationship());
        e.setFinancialStress(request.getFinancialStress());
        e.setSleepQuality(request.getSleepQuality());

        e.setFecha(LocalDateTime.now());

        // 3. guardar en BD
        evaluacionRepository.save(e);

        return "Evaluación registrada correctamente";
    }
}