package com.tallermovil.backend.controller;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
@RestController
public class TestController {
    @GetMapping("/perfil")
    public String perfil(Authentication authentication) {

        return "Usuario autenticado: "
                + authentication.getName();
    }
}
