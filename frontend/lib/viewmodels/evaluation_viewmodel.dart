import 'package:flutter/material.dart';
import '../models/prediction_response.dart';
import '../services/api_service.dart';

class EvaluationViewModel extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  String? _error;
  PredictionResponse? _prediction;

  // Valores del cuestionario (valores por defecto neutrales)
  double _phq9 = 0;
  double _gad7 = 0;
  double _sleepHours = 7;
  double _exerciseFreq = 3;
  double _socialActivity = 5;
  double _onlineStress = 5;
  double _gpa = 3;
  double _familySupport = 5;
  double _screenTime = 5;
  double _academicStress = 5;
  double _dietQuality = 5;
  double _selfEfficacy = 5;
  double _peerRelationship = 5;
  double _financialStress = 5;
  double _sleepQuality = 5;

  bool get isLoading => _isLoading;
  String? get error => _error;
  PredictionResponse? get prediction => _prediction;

  // Getters
  double get phq9 => _phq9;
  double get gad7 => _gad7;
  double get sleepHours => _sleepHours;
  double get exerciseFreq => _exerciseFreq;
  double get socialActivity => _socialActivity;
  double get onlineStress => _onlineStress;
  double get gpa => _gpa;
  double get familySupport => _familySupport;
  double get screenTime => _screenTime;
  double get academicStress => _academicStress;
  double get dietQuality => _dietQuality;
  double get selfEfficacy => _selfEfficacy;
  double get peerRelationship => _peerRelationship;
  double get financialStress => _financialStress;
  double get sleepQuality => _sleepQuality;

  // Setters
  void setPhq9(double v) { _phq9 = v; notifyListeners(); }
  void setGad7(double v) { _gad7 = v; notifyListeners(); }
  void setSleepHours(double v) { _sleepHours = v; notifyListeners(); }
  void setExerciseFreq(double v) { _exerciseFreq = v; notifyListeners(); }
  void setSocialActivity(double v) { _socialActivity = v; notifyListeners(); }
  void setOnlineStress(double v) { _onlineStress = v; notifyListeners(); }
  void setGpa(double v) { _gpa = v; notifyListeners(); }
  void setFamilySupport(double v) { _familySupport = v; notifyListeners(); }
  void setScreenTime(double v) { _screenTime = v; notifyListeners(); }
  void setAcademicStress(double v) { _academicStress = v; notifyListeners(); }
  void setDietQuality(double v) { _dietQuality = v; notifyListeners(); }
  void setSelfEfficacy(double v) { _selfEfficacy = v; notifyListeners(); }
  void setPeerRelationship(double v) { _peerRelationship = v; notifyListeners(); }
  void setFinancialStress(double v) { _financialStress = v; notifyListeners(); }
  void setSleepQuality(double v) { _sleepQuality = v; notifyListeners(); }

  Map<String, double> get features => {
    'phq9': _phq9,
    'gad7': _gad7,
    'sleepHours': _sleepHours,
    'exerciseFreq': _exerciseFreq,
    'socialActivity': _socialActivity,
    'onlineStress': _onlineStress,
    'gpa': _gpa,
    'familySupport': _familySupport,
    'screenTime': _screenTime,
    'academicStress': _academicStress,
    'dietQuality': _dietQuality,
    'selfEfficacy': _selfEfficacy,
    'peerRelationship': _peerRelationship,
    'financialStress': _financialStress,
    'sleepQuality': _sleepQuality,
  };

  Future<bool> enviarEvaluacion() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _prediction = await _apiService.enviarEvaluacion(features);
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

  void clear() {
    _prediction = null;
    _error = null;
    _phq9 = 0;
    _gad7 = 0;
    _sleepHours = 7;
    _exerciseFreq = 3;
    _socialActivity = 5;
    _onlineStress = 5;
    _gpa = 3;
    _familySupport = 5;
    _screenTime = 5;
    _academicStress = 5;
    _dietQuality = 5;
    _selfEfficacy = 5;
    _peerRelationship = 5;
    _financialStress = 5;
    _sleepQuality = 5;
    notifyListeners();
  }
}