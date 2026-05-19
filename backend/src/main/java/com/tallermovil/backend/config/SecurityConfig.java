package com.tallermovil.backend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    // Bean para encriptar passwords
    @Bean
    public BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    // Configuración de seguridad
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http)
            throws Exception {

        http
            // Desactivar CSRF
            .csrf(csrf -> csrf.disable())

            // Configurar permisos
            .authorizeHttpRequests(auth -> auth

                // Permitir auth sin token
                .requestMatchers("/auth/**").permitAll()

                // Cualquier otra ruta requiere login
                .anyRequest().authenticated()
            );

        return http.build();
    }
}