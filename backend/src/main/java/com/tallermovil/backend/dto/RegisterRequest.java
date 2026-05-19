package com.tallermovil.backend.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class RegisterRequest {
    private String nombre;
    private String email;
    private String password;
    private Integer edad;
    private String carrera;
    private Integer semestre;
}
