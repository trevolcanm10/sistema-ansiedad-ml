package com.tallermovil.backend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import com.tallermovil.backend.security.JwtAuthenticationFilter;

import lombok.RequiredArgsConstructor;

@Configuration
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtFilter;
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

            .sessionManagement(session ->
                        session.sessionCreationPolicy(
                                SessionCreationPolicy.STATELESS
                        )
                )

            // Configurar permisos
            .authorizeHttpRequests(auth -> auth

                // Permitir auth sin token
                .requestMatchers(
                                "/auth/login",
                                "/auth/register"
                        ).permitAll()

                // Cualquier otra ruta requiere login
                .anyRequest().authenticated()
            )

            .addFilterBefore(
                        jwtFilter,
                        UsernamePasswordAuthenticationFilter.class
            );

        return http.build();
    }
}