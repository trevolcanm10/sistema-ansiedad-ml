import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AuthViewModel extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  String? _error;
  String? _token;
  String? _role;
  bool _isLoggedIn = false;

  bool get isLoading => _isLoading;
  String? get error => _error;
  String? get token => _token;
  String? get role => _role;
  bool get isLoggedIn => _isLoggedIn;

  Future<void> checkSession() async {
    final savedToken = await _apiService.getToken();
    final savedRole = await _apiService.getRole();
    if (savedToken != null && savedRole != null) {
      _token = savedToken;
      _role = savedRole;
      _isLoggedIn = true;
      notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _apiService.login(email, password);
      _token = data['token'] as String?;
      _isLoggedIn = true;
      // Extraer role del token o de la respuesta
      // Por ahora lo dejamos vacío, se puede mejorar con JWT decode
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceFirst('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register({
    required String nombre,
    required String email,
    required String password,
    required int edad,
    required String carrera,
    required int semestre,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _apiService.register(
        nombre: nombre,
        email: email,
        password: password,
        edad: edad,
        carrera: carrera,
        semestre: semestre,
        role: 'ESTUDIANTE',
      );
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceFirst('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _apiService.clearSession();
    _token = null;
    _role = null;
    _isLoggedIn = false;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}