class AppConstants {
  static const String baseUrl = 'http://10.0.2.2:8080';

  // Endpoints
  static const String loginUrl = '$baseUrl/auth/login';
  static const String registerUrl = '$baseUrl/auth/register';
  static const String evaluacionUrl = '$baseUrl/evaluacion';
  static const String ultimaEvaluacionUrl = '$baseUrl/evaluacion/ultima';

  // Colores por nivel de riesgo
  static const int colorBajo = 0xFF4CAF50;
  static const int colorModerado = 0xFFFF9800;
  static const int colorAlto = 0xFFF44336;

  // Textos por nivel
  static const String textoBajo = 'BAJO';
  static const String textoModerado = 'MODERADO';
  static const String textoAlto = 'ALTO';
}