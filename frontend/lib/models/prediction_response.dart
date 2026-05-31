class PredictionResponse {
  final String nivelRiesgo;
  final double confianza;
  final Map<String, int>? votos;
  final Map<String, dynamic>? predicciones;
  final List<String>? recomendaciones;
  final double? probabilidadBajoPromedio;

  PredictionResponse({
    required this.nivelRiesgo,
    required this.confianza,
    this.votos,
    this.predicciones,
    this.recomendaciones,
    this.probabilidadBajoPromedio,
  });

  factory PredictionResponse.fromJson(Map<String, dynamic> json) {
    return PredictionResponse(
      nivelRiesgo: json['nivel_riesgo'] as String? ?? 'NO_DISPONIBLE',
      confianza: (json['confianza'] as num?)?.toDouble() ?? 0.0,
      votos: json['votos'] != null
          ? Map<String, int>.from(json['votos'] as Map)
          : null,
      predicciones: json['predicciones'] != null
          ? Map<String, dynamic>.from(json['predicciones'] as Map)
          : null,
      recomendaciones: json['recomendaciones'] != null
          ? List<String>.from(json['recomendaciones'] as List)
          : null,
      probabilidadBajoPromedio:
          (json['probabilidad_bajo_promedio'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'nivel_riesgo': nivelRiesgo,
        'confianza': confianza,
        'votos': votos,
        'predicciones': predicciones,
        'recomendaciones': recomendaciones,
        'probabilidad_bajo_promedio': probabilidadBajoPromedio,
      };

  int get colorHex {
    switch (nivelRiesgo.toUpperCase()) {
      case 'BAJO':
        return 0xFF4CAF50;
      case 'MODERADO':
        return 0xFFFF9800;
      case 'ALTO':
        return 0xFFF44336;
      default:
        return 0xFF9E9E9E;
    }
  }
}