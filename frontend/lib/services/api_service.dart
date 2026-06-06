import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants.dart';
import '../models/prediction_response.dart';

class ApiService {
  static const String _tokenKey = 'jwt_token';
  static const String _roleKey = 'user_role';

  // ============================================================
  // TOKEN MANAGEMENT
  // ============================================================

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<void> saveRole(String role) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_roleKey, role);
  }

  Future<String?> getRole() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_roleKey);
  }

  Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_roleKey);
  }

  // ============================================================
  // AUTH
  // ============================================================

  Future<Map<String, dynamic>> login(
      String email, String password) async {
    final response = await http.post(
      Uri.parse(AppConstants.loginUrl),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (data.containsKey('token')) {
        await saveToken(data['token'] as String);
      }
      return data;
    } else {
      final error = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(error['error'] ?? 'Error al iniciar sesión');
    }
  }

  Future<Map<String, dynamic>> register({
    required String nombre,
    required String email,
    required String password,
    required int edad,
    required String carrera,
    required int semestre,
    required String role,
  }) async {
    final response = await http.post(
      Uri.parse(AppConstants.registerUrl),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'nombre': nombre,
        'email': email,
        'password': password,
        'edad': edad,
        'carrera': carrera,
        'semestre': semestre,
        'role': role,
      }),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      final error = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(error['error'] ?? 'Error al registrar');
    }
  }

  // ============================================================
  // EVALUACIÓN
  // ============================================================

  Future<PredictionResponse> enviarEvaluacion(
      Map<String, double> features) async {
    final token = await getToken();
    if (token == null) throw Exception('No autenticado');

    final response = await http.post(
      Uri.parse(AppConstants.evaluacionUrl),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(features),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return PredictionResponse.fromJson(data);
    } else {
      final error = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(error['error'] ?? 'Error al procesar evaluación');
    }
  }

  Future<PredictionResponse?> obtenerUltimaEvaluacion() async {
    final token = await getToken();
    if (token == null) throw Exception('No autenticado');

    final response = await http.get(
      Uri.parse(AppConstants.ultimaEvaluacionUrl),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (data['nivelRiesgo'] == null) return null;
      return PredictionResponse.fromJson({
        'nivel_riesgo': data['nivelRiesgo'],
        'confianza': data['confianza'],
        'votos': data['votos'],
        'predicciones': data['prediccionesModelos'],
        'recomendaciones': null,
      });
    }
    return null;
  }

  // ============================================================
  // ADMIN
  // ============================================================

  Future<List<Map<String, dynamic>>> listarUsuariosAdmin() async {
    final token = await getToken();
    if (token == null) throw Exception('No autenticado');

    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/admin/usuarios'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body) as List);
    }
    throw Exception('Error al listar usuarios');
  }

  Future<List<Map<String, dynamic>>> listarEvaluacionesAdmin() async {
    final token = await getToken();
    if (token == null) throw Exception('No autenticado');

    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/admin/evaluaciones'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body) as List);
    }
    throw Exception('Error al listar evaluaciones');
  }

  Future<Map<String, dynamic>> obtenerStatsAdmin() async {
    final token = await getToken();
    if (token == null) throw Exception('No autenticado');

    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/admin/stats'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    throw Exception('Error al obtener estadísticas');
  }

  // ============================================================
  // MEDICO
  // ============================================================

  Future<List<Map<String, dynamic>>> listarEstudiantesMedico() async {
    final token = await getToken();
    if (token == null) throw Exception('No autenticado');

    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/medico/estudiantes'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body) as List);
    }
    throw Exception('Error al listar estudiantes');
  }

  Future<List<Map<String, dynamic>>> verEvaluacionesEstudiante(int estudianteId) async {
    final token = await getToken();
    if (token == null) throw Exception('No autenticado');

    final response = await http.get(
      Uri.parse('${AppConstants.baseUrl}/medico/estudiantes/$estudianteId/evaluaciones'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body) as List);
    }
    throw Exception('Error al cargar evaluaciones del estudiante');
  }
}