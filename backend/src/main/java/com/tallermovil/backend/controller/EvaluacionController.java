package com.tallermovil.backend.controller;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tallermovil.backend.dto.EvaluacionRequest;
import com.tallermovil.backend.dto.EvaluacionResponse;
import com.tallermovil.backend.dto.PredictionResponse;
import com.tallermovil.backend.model.Evaluacion;
import com.tallermovil.backend.model.MentalHealthStatus;
import com.tallermovil.backend.model.Usuario;
import com.tallermovil.backend.repository.EvaluacionRepository;
import com.tallermovil.backend.repository.UsuarioRepository;
import com.tallermovil.backend.service.MlService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Controlador REST para gestionar las evaluaciones de ansiedad.
 * Expone endpoints bajo la ruta base "/evaluacion".
 * 
 * Este controlador recibe las respuestas del cuestionario que el estudiante
 * llena desde la app Flutter, las envía al servicio ML para obtener la
 * predicción del nivel de riesgo, y guarda todo en la base de datos.
 */
@RestController
@RequestMapping("/evaluacion")
@RequiredArgsConstructor
@Slf4j
public class EvaluacionController {

    private final EvaluacionRepository evaluacionRepository;
    private final UsuarioRepository usuarioRepository;
    private final MlService mlService;
    private final ObjectMapper objectMapper;

    /**
     * Endpoint: POST /evaluacion
     * 
     * Recibe los datos del cuestionario, envía al servicio ML para predecir
     * el nivel de riesgo, guarda la evaluación con el resultado, y retorna
     * la predicción + recomendaciones al frontend.
     * 
     * @param request  Datos del cuestionario (JSON)
     * @param auth     Usuario autenticado (extraído del JWT)
     * @return         EvaluacionResponse con predicción y recomendaciones
     */
    @PostMapping
    public EvaluacionResponse crearEvaluacion(
            @RequestBody EvaluacionRequest request,
            Authentication auth
    ) {

        log.info("=== NUEVA EVALUACIÓN RECIBIDA ===");

        // ================================================================
        //  PASO 1: OBTENER EL USUARIO AUTENTICADO DESDE EL TOKEN JWT
        // ================================================================

        String email = auth.getName();

        Usuario usuario = usuarioRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado"));

        log.info("Usuario: {} ({})", usuario.getNombre(), email);

        // ================================================================
        //  PASO 2: CONSTRUIR LA ENTIDAD "Evaluacion" CON LOS DATOS RECIBIDOS
        // ================================================================

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

        // ================================================================
        //  PASO 3: ENVIAR FEATURES AL SERVICIO ML PARA PREDECIR
        // ================================================================

        Map<String, Double> features = new LinkedHashMap<>();
        features.put("phq9", request.getPhq9());
        features.put("gad7", request.getGad7());
        features.put("sleepHours", request.getSleepHours());
        features.put("exerciseFreq", request.getExerciseFreq());
        features.put("socialActivity", request.getSocialActivity());
        features.put("onlineStress", request.getOnlineStress());
        features.put("gpa", request.getGpa());
        features.put("familySupport", request.getFamilySupport());
        features.put("screenTime", request.getScreenTime());
        features.put("academicStress", request.getAcademicStress());
        features.put("dietQuality", request.getDietQuality());
        features.put("selfEfficacy", request.getSelfEfficacy());
        features.put("peerRelationship", request.getPeerRelationship());
        features.put("financialStress", request.getFinancialStress());
        features.put("sleepQuality", request.getSleepQuality());

        PredictionResponse prediction = mlService.predecir(features);

        // ================================================================
        //  PASO 4: GUARDAR EL RESULTADO EN LA EVALUACIÓN
        // ================================================================

        // Mapear el nivel de riesgo del ML al enum MentalHealthStatus
        MentalHealthStatus status = mapearNivelRiesgo(prediction.getNivel_riesgo());
        e.setMentalHealthStatus(status);
        e.setConfianza(prediction.getConfianza());

        // Guardar votos y predicciones como JSON
        try {
            if (prediction.getVotos() != null) {
                e.setVotosJson(objectMapper.writeValueAsString(prediction.getVotos()));
            }
            if (prediction.getPredicciones() != null) {
                e.setPrediccionesJson(objectMapper.writeValueAsString(prediction.getPredicciones()));
            }
        } catch (Exception ex) {
            log.error("Error al serializar JSON: {}", ex.getMessage());
        }

        // ================================================================
        //  PASO 5: GUARDAR LA EVALUACIÓN EN LA BASE DE DATOS
        // ================================================================

        evaluacionRepository.save(e);
        log.info("Evaluación guardada. ID: {}, Predicción: {} (confianza: {})",
                e.getId(), prediction.getNivel_riesgo(), prediction.getConfianza());

        // ================================================================
        //  PASO 6: CONSTRUIR Y RETORNAR LA RESPUESTA
        // ================================================================

        EvaluacionResponse response = new EvaluacionResponse();
        response.setMensaje("Evaluación registrada correctamente");
        response.setNivelRiesgo(prediction.getNivel_riesgo());
        response.setConfianza(prediction.getConfianza());
        response.setVotos(prediction.getVotos());
        response.setPrediccionesModelos(prediction.getPredicciones());
        response.setRecomendaciones(prediction.getRecomendaciones());

        return response;
    }

    /**
     * Endpoint: GET /evaluacion/ultima
     * 
     * Retorna la última evaluación del usuario autenticado
     * con su resultado de predicción.
     */
    @GetMapping("/ultima")
    public EvaluacionResponse obtenerUltimaEvaluacion(Authentication auth) {
        String email = auth.getName();
        Usuario usuario = usuarioRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado"));

        Evaluacion ultima = evaluacionRepository
                .findTopByUsuarioIdOrderByFechaDesc(usuario.getId())
                .orElse(null);

        if (ultima == null) {
            EvaluacionResponse response = new EvaluacionResponse();
            response.setMensaje("No tienes evaluaciones registradas");
            return response;
        }

        EvaluacionResponse response = new EvaluacionResponse();
        response.setMensaje("Última evaluación");
        response.setNivelRiesgo(ultima.getMentalHealthStatus() != null
                ? ultima.getMentalHealthStatus().name() : "NO_DISPONIBLE");
        response.setConfianza(ultima.getConfianza());

        // Deserializar JSON de votos
        try {
            if (ultima.getVotosJson() != null) {
                response.setVotos(objectMapper.readValue(
                        ultima.getVotosJson(),
                        objectMapper.getTypeFactory().constructMapType(Map.class, String.class, Integer.class)
                ));
            }
            if (ultima.getPrediccionesJson() != null) {
                response.setPrediccionesModelos(objectMapper.readValue(
                        ultima.getPrediccionesJson(),
                        objectMapper.getTypeFactory().constructMapType(Map.class, String.class, String.class)
                ));
            }
        } catch (Exception ex) {
            log.error("Error al deserializar JSON: {}", ex.getMessage());
        }

        response.setRecomendaciones(null); // Las recomendaciones no se almacenan
        return response;
    }

    /**
     * Mapea el nivel de riesgo retornado por el ML al enum MentalHealthStatus.
     * 
     * @param nivelRiesgo String del ML: "BAJO", "ALTO", "NO_DISPONIBLE"
     * @return MentalHealthStatus correspondiente
     */
    private MentalHealthStatus mapearNivelRiesgo(String nivelRiesgo) {
        if (nivelRiesgo == null) return MentalHealthStatus.NO_DISPONIBLE;

        return switch (nivelRiesgo.toUpperCase()) {
            case "BAJO" -> MentalHealthStatus.LOW;
            case "ALTO" -> MentalHealthStatus.HIGH;
            default -> MentalHealthStatus.NO_DISPONIBLE;
        };
    }
}