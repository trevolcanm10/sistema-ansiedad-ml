package com.tallermovil.backend.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.security.access.prepost.PreAuthorize;
@RestController
@RequestMapping("/estudiante")
public class EstudianteController {
    @PreAuthorize("hasRole('ESTUDIANTE')")
    @GetMapping("/perfil")
    public String perfil() {
        return "Perfil del estudiante";
    }
}
