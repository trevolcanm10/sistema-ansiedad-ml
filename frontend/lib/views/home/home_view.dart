import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../viewmodels/auth_viewmodel.dart';
import '../auth/login_view.dart';
import '../evaluation/evaluation_view.dart';
import '../results/result_view.dart';
import '../../services/api_service.dart';
import '../../models/prediction_response.dart';

class HomeView extends StatefulWidget {
  const HomeView({super.key});

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  final ApiService _apiService = ApiService();
  PredictionResponse? _ultimaEvaluacion;
  bool _cargandoUltima = true;

  @override
  void initState() {
    super.initState();
    _cargarUltimaEvaluacion();
  }

  Future<void> _cargarUltimaEvaluacion() async {
    try {
      final ultima = await _apiService.obtenerUltimaEvaluacion();
      if (mounted) {
        setState(() {
          _ultimaEvaluacion = ultima;
          _cargandoUltima = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _cargandoUltima = false);
    }
  }

  Color _colorNivel(String nivel) {
    switch (nivel.toUpperCase()) {
      case 'BAJO':
        return Colors.green;
      case 'MODERADO':
        return Colors.orange;
      case 'ALTO':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bienestar Estudiantil'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              final navigator = Navigator.of(context);
              context.read<AuthViewModel>().logout().then((_) {
                navigator.pushReplacement(
                  MaterialPageRoute(builder: (_) => const LoginView()),
                );
              });
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Card de bienvenida
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    const Icon(Icons.favorite_rounded,
                        size: 48, color: Colors.teal),
                    const SizedBox(height: 8),
                    const Text(
                      'Evalúa tu bienestar emocional',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Responde el cuestionario para conocer tu nivel de riesgo de ansiedad.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Botón Nueva Evaluación
            SizedBox(
              height: 56,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (_) => const EvaluationView()),
                  );
                },
                icon: const Icon(Icons.assignment_rounded, size: 28),
                label: const Text(
                  'NUEVA EVALUACIÓN',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Última evaluación
            const Text(
              'Última evaluación',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),

            if (_cargandoUltima)
              const Center(child: CircularProgressIndicator())
            else if (_ultimaEvaluacion != null)
              Card(
                elevation: 2,
                child: ListTile(
                  leading: Icon(
                    Icons.circle,
                    color: _colorNivel(_ultimaEvaluacion!.nivelRiesgo),
                    size: 20,
                  ),
                  title: Text(
                    'Riesgo: ${_ultimaEvaluacion!.nivelRiesgo}',
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: _colorNivel(_ultimaEvaluacion!.nivelRiesgo),
                    ),
                  ),
                  subtitle: Text(
                      'Confianza: ${(_ultimaEvaluacion!.confianza * 100).toStringAsFixed(0)}%'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) =>
                            ResultView(prediction: _ultimaEvaluacion!),
                      ),
                    );
                  },
                ),
              )
            else
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Aún no has realizado ninguna evaluación.',
                    style: TextStyle(color: Colors.grey),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}