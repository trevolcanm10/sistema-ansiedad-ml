package com.tallermovil.backend.security;

import java.security.Key;
import java.util.Date;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;

/**
 * Clase utilitaria para la generación, validación y extracción de tokens JWT.
 * 
 * JWT (JSON Web Token) es un estándar abierto (RFC 7519) que define una forma compacta
 * y autónoma de transmitir información de forma segura entre partes como un objeto JSON.
 * 
 * Este componente es usado por el filtro de seguridad de Spring para autenticar
 * las peticiones HTTP entrantes mediante tokens.
 */
@Component
public class JwtUtil {

    // ============================================================
    // INYECCIÓN DE CONFIGURACIÓN DESDE application.properties / .env
    // ============================================================

    /**
     * Clave secreta utilizada para firmar y verificar los tokens JWT.
     * Se inyecta desde la propiedad 'JWT_SECRET' definida en application.properties
     * o en variables de entorno.
     * 
     * ⚠️ IMPORTANTE: En producción, esta clave debe ser una cadena larga y
     *    compleja (al menos 256 bits para HS256). Nunca debe estar hardcodeada
     *    ni expuesta en el código fuente.
     */
    @Value("${JWT_SECRET}")
    private String secretKey;

    /**
     * Tiempo de expiración del token en milisegundos.
     * Se inyecta desde la propiedad 'JWT_EXPIRATION'.
     * 
     * Actualmente configurado para 30 minutos (1800000 ms).
     * Después de este tiempo, el token se considera inválido y el cliente
     * debe obtener uno nuevo (generalmente volviendo a iniciar sesión).
     */
    @Value("${JWT_EXPIRATION}")
    private long expirationTime;

    // ============================================================
    // MÉTODOS PRIVADOS
    // ============================================================

    /**
     * Genera una clave HMAC (Hash-based Message Authentication Code) segura
     * a partir de la cadena 'secretKey' utilizando el algoritmo SHA.
     * 
     * HMAC-SHA256 requiere una clave de al menos 256 bits (32 bytes).
     * Si la clave proporcionada es más corta, 'hmacShaKeyFor()' la rellenará
     * automáticamente para cumplir con el tamaño mínimo requerido.
     * 
     * @return Key una clave HMAC segura para firmar/verificar tokens JWT
     */
    private Key getSigningKey() {
        // Convierte la cadena secreta en bytes y crea una clave HMAC-SHA
        return Keys.hmacShaKeyFor(secretKey.getBytes());
    }

    // ============================================================
    // MÉTODOS PÚBLICOS
    // ============================================================

    /**
     * Genera un token JWT para un usuario autenticado.
     * 
     * El token contiene:
     *   - 'subject' (sub): El email del usuario (identificador único)
     *   - 'issuedAt' (iat): Fecha y hora de emisión del token
     *   - 'expiration' (exp): Fecha y hora de expiración del token
     * 
     * Luego se firma con la clave secreta usando el algoritmo HS256
     * (HMAC con SHA-256), que garantiza que el token no ha sido alterado.
     * 
     * @param email El correo electrónico del usuario autenticado
     * @return String El token JWT generado (cadena de texto compacta)
     */
    public String generateToken(String email, String role) {

        // Construye el token JWT usando el builder fluido de JJWT
        return Jwts.builder()
                // Establece el 'subject' (asunto) como el email del usuario
                .setSubject(email)
                // Establece el 'role' (rol) del usuario
                .claim("role", role)
                // Marca la fecha/hora actual como momento de emisión
                .setIssuedAt(new Date())
                // Calcula y establece la fecha de expiración:
                // momento actual + tiempo de expiración configurado
                .setExpiration(
                        new Date(System.currentTimeMillis() + expirationTime)
                )
                // Firma el token con la clave secreta usando algoritmo HS256
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                // Convierte el token a su representación compacta (cadena JWT)
                .compact();
    }

    /**
     * Extrae el email del usuario (subject) contenido dentro de un token JWT.
     * 
     * Este método analiza (parsea) el token, verifica su firma y extrae
     * el payload (cuerpo) del token para obtener el 'subject'.
     * 
     * ⚠️ NOTA: Este método NO valida la expiración del token.
     *    Si el token está expirado, lanzará una excepción.
     *    Se recomienda usar 'validateToken()' antes de llamar a este método.
     * 
     * @param token El token JWT del cual extraer el email
     * @return String El email del usuario contenido en el token
     */
    public String extractEmail(String token) {

        // Analiza el token JWT:
        // 1. Crea un parser con la clave de verificación
        // 2. Construye el parser
        // 3. Parsea el token JWS (JSON Web Signature)
        // 4. Obtiene el cuerpo (claims) del token
        // 5. Extrae el 'subject' (que es el email del usuario)
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }

    /**
     * Valida si un token JWT es válido y no ha sido manipulado.
     * 
     * Realiza las siguientes verificaciones:
     *   1. Integridad de la firma → verifica que el token fue firmado
     *      con nuestra clave secreta y no ha sido alterado.
     *   2. Expiración → verifica que el token no haya expirado
     *      comparando con la fecha actual.
     * 
     * @param token El token JWT a validar
     * @return boolean true si el token es válido, false en caso contrario
     *         (incluyendo token expirado, firma inválida o formato incorrecto)
     */
    public boolean validateToken(String token) {

        try {
            // Intenta analizar el token con la clave de verificación
            // Si el token es inválido (firma incorrecta, expirado, malformado),
            // se lanzará una excepción
            Jwts.parserBuilder()
                    .setSigningKey(getSigningKey())
                    .build()
                    .parseClaimsJws(token);

            // Si no hay excepción, el token es válido
            return true;

        } catch (JwtException | IllegalArgumentException e) {
            // JwtException: Token inválido (expirado, firma incorrecta, etc.)
            // IllegalArgumentException: Token es null o está vacío
            return false;
        }
    }

    // Obtiene el rol (role) del usuario contenido en el token
    public String extractRole(String token) {

        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody()
                .get("role", String.class);
    }
}