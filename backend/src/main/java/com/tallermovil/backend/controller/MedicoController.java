package com.tallermovil.backend.controller;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.security.access.prepost.PreAuthorize;
@RestController
@RequestMapping("/medico")
public class MedicoController {
    @PreAuthorize("hasRole('MEDICO')")
    @GetMapping("/dashboard")
    public String dashboard() {
        return "Panel del médico";
    }
}
