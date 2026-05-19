package com.tallermovil.backend.controller;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tallermovil.backend.dto.LoginRequest;
import com.tallermovil.backend.dto.LoginResponse;
import com.tallermovil.backend.dto.RegisterRequest;
import com.tallermovil.backend.model.Usuario;
import com.tallermovil.backend.repository.UsuarioRepository;
import com.tallermovil.backend.security.JwtUtil;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final UsuarioRepository usuarioRepository;
    private final BCryptPasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    // REGISTER
    @PostMapping("/register")
    public ResponseEntity<?> register(
            @RequestBody RegisterRequest request
    ) {

        Optional<Usuario> usuarioExistente =
                usuarioRepository.findByEmail(request.getEmail());

        if (usuarioExistente.isPresent()) {

            return ResponseEntity
                    .badRequest()
                    .body(Map.of(
                            "error",
                            "El email ya está registrado"
                    ));
        }

        Usuario usuario = Usuario.builder()
                .nombre(request.getNombre())
                .email(request.getEmail())
                .password(
                        passwordEncoder.encode(request.getPassword())
                )
                .edad(request.getEdad())
                .carrera(request.getCarrera())
                .semestre(request.getSemestre())
                .role(request.getRole())
                .fechaRegistro(LocalDateTime.now())
                .build();

        usuarioRepository.save(usuario);

        return ResponseEntity.status(HttpStatus.CREATED)
                .body(Map.of(
                        "message",
                        "Usuario registrado correctamente"
                ));
    }

    // LOGIN
    @PostMapping("/login")
    public ResponseEntity<?> login(
            @RequestBody LoginRequest request
    ) {

        Optional<Usuario> usuarioOptional =
                usuarioRepository.findByEmail(request.getEmail());

        if (usuarioOptional.isEmpty()) {

            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of(
                            "error",
                            "Credenciales inválidas"
                    ));
        }

        Usuario usuario = usuarioOptional.get();

        boolean passwordCorrecto =
                passwordEncoder.matches(
                        request.getPassword(),
                        usuario.getPassword()
                );

        if (!passwordCorrecto) {

            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of(
                            "error",
                            "Credenciales inválidas"
                    ));
        }

        String token = jwtUtil.generateToken(usuario.getEmail());

        return ResponseEntity.ok(
                new LoginResponse(token)
        );
    }
}