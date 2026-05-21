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

/**
 * Controlador REST para gestionar las evaluaciones de ansiedad.
 * Expone endpoints bajo la ruta base "/evaluacion".
 * 
 * Este controlador recibe las respuestas del cuestionario que el estudiante
 * llena desde la app Flutter, y las guarda en la base de datos asociándolas
 * al usuario autenticado.
 */
@RestController                     // Indica que esta clase es un controlador REST (devuelve JSON/texto, no vistas HTML)
@RequestMapping("/evaluacion")      // Todas las rutas de este controlador comenzarán con /evaluacion (ej: /evaluacion)
@RequiredArgsConstructor            // Lombok: genera un constructor con los campos final (inyección de dependencias)
public class EvaluacionController {

    // === INYECCIÓN DE DEPENDENCIAS (Spring los asigna automáticamente) ===

    /** Repositorio para acceder a la tabla "evaluaciones" en la BD (CRUD) */
    private final EvaluacionRepository evaluacionRepository;

    /** Repositorio para acceder a la tabla "usuarios" en la BD */
    private final UsuarioRepository usuarioRepository;

    /**
     * Endpoint: POST /evaluacion
     * 
     * Recibe los datos del cuestionario que el estudiante respondió desde la app
     * y los guarda en la base de datos.
     * 
     * @param request  Datos enviados desde Flutter en el cuerpo de la petición (formato JSON)
     * @param auth     Objeto que contiene la información del usuario autenticado (extraído del JWT)
     * @return         Mensaje de confirmación
     */
    @PostMapping    // Responde solo a peticiones HTTP POST
    public String crearEvaluacion(
            @RequestBody EvaluacionRequest request,  // Los datos del formulario vienen en el cuerpo (JSON)
            Authentication auth                      // Spring Security inyecta aquí los datos del token JWT
    ) {

        // ================================================================
        //  PASO 1: OBTENER EL USUARIO AUTENTICADO DESDE EL TOKEN JWT
        // ================================================================

        // auth.getName() devuelve el email del usuario porque así lo configuramos
        // en el JWT. Este email fue extraído del token que el frontend envió.
        String email = auth.getName();

        // Buscamos al usuario en la base de datos usando su email.
        // Si no existe, lanzamos una excepción que detiene el proceso.
        Usuario usuario = usuarioRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado"));

        // ================================================================
        //  PASO 2: CONSTRUIR LA ENTIDAD "Evaluacion" CON LOS DATOS RECIBIDOS
        // ================================================================

        // Creamos un nuevo objeto Evaluacion (aún no está en la BD)
        Evaluacion e = new Evaluacion();

        // Asociamos esta evaluación al usuario que la está creando
        e.setUsuarioId(usuario.getId());

        // Copiamos cada campo del DTO (request) a la entidad (e)
        // Estos son los puntajes/valores que el estudiante respondió en el cuestionario:

        e.setPhq9(request.getPhq9());                 // Puntaje del cuestionario PHQ-9 (depresión)
        e.setGad7(request.getGad7());                 // Puntaje del cuestionario GAD-7 (ansiedad)
        e.setSleepHours(request.getSleepHours());     // Horas de sueño promedio
        e.setExerciseFreq(request.getExerciseFreq()); // Frecuencia de ejercicio (días por semana)
        e.setSocialActivity(request.getSocialActivity()); // Nivel de actividad social
        e.setOnlineStress(request.getOnlineStress()); // Estrés por redes sociales / vida online
        e.setGpa(request.getGpa());                   // Promedio de calificaciones (GPA)
        e.setFamilySupport(request.getFamilySupport()); // Percepción de apoyo familiar
        e.setScreenTime(request.getScreenTime());     // Tiempo de pantalla diario (horas)
        e.setAcademicStress(request.getAcademicStress()); // Estrés académico percibido
        e.setDietQuality(request.getDietQuality());   // Calidad de la alimentación
        e.setSelfEfficacy(request.getSelfEfficacy()); // Autoeficacia (confianza en uno mismo)
        e.setPeerRelationship(request.getPeerRelationship()); // Relaciones con compañeros
        e.setFinancialStress(request.getFinancialStress()); // Estrés financiero
        e.setSleepQuality(request.getSleepQuality()); // Calidad del sueño

        // Registramos la fecha y hora exacta en que se guardó la evaluación
        e.setFecha(LocalDateTime.now());

        // ================================================================
        //  PASO 3: GUARDAR LA EVALUACIÓN EN LA BASE DE DATOS
        // ================================================================

        // El repositorio ejecuta automáticamente un INSERT en la tabla "evaluaciones"
        evaluacionRepository.save(e);

        // Devolvemos un mensaje de éxito al frontend (Flutter lo mostrará al usuario)
        return "Evaluación registrada correctamente";
    }
}
