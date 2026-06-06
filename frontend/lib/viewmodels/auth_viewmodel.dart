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

  /// Inicializa la sesión desde SharedPreferences al arrancar la app
  void setLoggedIn(String role) {
    _role = role;
    _isLoggedIn = true;
    notifyListeners();
  }

  Future<void> checkSession() async {
    final savedToken = await _apiService.getToken();
    final savedRole = await _apiService.getRole();
    // Si hay token pero role es null/vacío, forzar logout (datos corruptos)
    if (savedToken != null && (savedRole == null || savedRole.isEmpty)) {
      await logout();
      return;
    }
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
      _role = data['role'] as String?;
      
      // Si el backend no devuelve role, usar default
      if (_role == null || _role!.isEmpty) {
        _error = 'El servidor no devolvió el rol del usuario. Reconstruye el backend.';
        _isLoading = false;
        notifyListeners();
        return false;
      }
      
      _isLoggedIn = true;
      await _apiService.saveRole(_role!);
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