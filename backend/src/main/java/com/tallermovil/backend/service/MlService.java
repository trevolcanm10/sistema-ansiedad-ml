package com.tallermovil.backend.service;

import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.tallermovil.backend.dto.PredictionResponse;

import lombok.extern.slf4j.Slf4j;

/**
 * Servicio que se comunica con la API de Machine Learning (Flask).
 * 
 * Envía los features del cuestionario al servicio ML y recibe
 * la predicción del nivel de riesgo de ansiedad.
 */
@Service
@Slf4j
public class MlService {

    /**
     * URL base del servicio ML, configurada en application.properties.
     * Ejemplo: http://localhost:5000 o http://ml:5000 (en Docker)
     */
    @Value("${ml.api.url}")
    private String mlApiUrl;

    /**
     * Cliente HTTP para realizar peticiones al servicio ML.
     */
    private final RestTemplate restTemplate;

    public MlService() {
        this.restTemplate = new RestTemplate();
    }

    /**
     * Envía los datos del cuestionario al servicio ML y retorna la predicción.
     * 
     * @param features Mapa con los 15 features del cuestionario:
     *                 phq9, gad7, sleepHours, exerciseFreq, socialActivity,
     *                 onlineStress, gpa, familySupport, screenTime,
     *                 academicStress, dietQuality, selfEfficacy,
     *                 peerRelationship, financialStress, sleepQuality
     * @return PredictionResponse con la predicción, confianza y recomendaciones
     */
    public PredictionResponse predecir(Map<String, Double> features) {

        String url = mlApiUrl + "/predict";

        try {
            log.info("Enviando predicción al servicio ML: {}", url);

            // Configurar headers HTTP
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // Crear el request con los features
            HttpEntity<Map<String, Double>> request = new HttpEntity<>(features, headers);

            // Realizar la petición POST al servicio ML
            ResponseEntity<PredictionResponse> response = restTemplate.postForEntity(
                    url,
                    request,
                    PredictionResponse.class
            );

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                log.info("Predicción recibida: nivel={}, confianza={}",
                        response.getBody().getNivel_riesgo(),
                        response.getBody().getConfianza());
                return response.getBody();
            } else {
                log.error("Respuesta no exitosa del servicio ML: {}", response.getStatusCode());
                return crearRespuestaDefault();
            }

        } catch (Exception e) {
            log.error("Error al conectar con el servicio ML: {} | URL: {} | Tipo: {}",
                    e.getMessage(), url, e.getClass().getSimpleName());
            log.error("Detalle del error: ", e);
            return crearRespuestaDefault();
        }
    }

    /**
     * Crea una respuesta por defecto cuando el servicio ML no está disponible.
     * Esto permite que el sistema siga funcionando incluso si ML está caído.
     */
    private PredictionResponse crearRespuestaDefault() {
        PredictionResponse defaultResponse = new PredictionResponse();
        defaultResponse.setNivel_riesgo("NO_DISPONIBLE");
        defaultResponse.setConfianza(0.0);
        defaultResponse.setVotos(Map.of());
        defaultResponse.setPredicciones(Map.of());
        defaultResponse.setRecomendaciones(
                java.util.List.of(
                        "⚠️ El servicio de predicción no está disponible en este momento.",
                        "📄 Tu evaluación ha sido guardada. Intenta consultar los resultados más tarde."
                )
        );
        return defaultResponse;
    }

    /**
     * Verifica si el servicio ML está disponible.
     * 
     * @return true si el servicio ML responde correctamente
     */
    public boolean isServiceAvailable() {
        try {
            String url = mlApiUrl + "/health";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            log.warn("Servicio ML no disponible: {}", e.getMessage());
            return false;
        }
    }
}