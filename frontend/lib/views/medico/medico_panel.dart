import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import '../../viewmodels/auth_viewmodel.dart';
import '../auth/login_view.dart';

class MedicoPanel extends StatefulWidget {
  const MedicoPanel({super.key});

  @override
  State<MedicoPanel> createState() => _MedicoPanelState();
}

class _MedicoPanelState extends State<MedicoPanel> {
  final ApiService _api = ApiService();
  List<Map<String, dynamic>> _estudiantes = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _cargarEstudiantes();
  }

  Future<void> _cargarEstudiantes() async {
    try {
      final estudiantes = await _api.listarEstudiantesMedico();
      if (mounted) setState(() { _estudiantes = estudiantes; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Color _colorNivel(String? nivel) {
    switch (nivel) {
      case 'LOW': return Colors.green;
      case 'MODERATE': return Colors.orange;
      case 'HIGH': return Colors.red;
      case 'SIN_EVALUAR': return Colors.grey;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Panel del Médico'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              final navigator = Navigator.of(context);
              context.read<AuthViewModel>().logout().then((_) {
                navigator.pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginView()),
                  (route) => false,
                );
              });
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _estudiantes.isEmpty
              ? const Center(child: Text('No hay estudiantes registrados'))
              : ListView.builder(
                  itemCount: _estudiantes.length,
                  itemBuilder: (_, i) {
                    final e = _estudiantes[i];
                    final nivel = e['ultimoNivel'] as String?;
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: _colorNivel(nivel).withValues(alpha: 0.2),
                          child: Text('${e['nombre']}'[0].toUpperCase()),
                        ),
                        title: Text('${e['nombre']}', style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('${e['carrera']} · Semestre ${e['semestre']}\nÚltimo: $nivel'),
                        isThreeLine: true,
                        trailing: Icon(Icons.chevron_right),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => _DetalleEstudiante(
                                estudiante: e,
                                api: _api,
                              ),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
    );
  }
}

class _DetalleEstudiante extends StatefulWidget {
  final Map<String, dynamic> estudiante;
  final ApiService api;
  const _DetalleEstudiante({required this.estudiante, required this.api});

  @override
  State<_DetalleEstudiante> createState() => _DetalleEstudianteState();
}

class _DetalleEstudianteState extends State<_DetalleEstudiante> {
  List<Map<String, dynamic>> _evaluaciones = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final evs = await widget.api.verEvaluacionesEstudiante(widget.estudiante['id'] as int);
      if (mounted) setState(() { _evaluaciones = evs; _loading = false; });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Color _colorNivel(String? nivel) {
    switch (nivel) {
      case 'LOW': return Colors.green;
      case 'MODERATE': return Colors.orange;
      case 'HIGH': return Colors.red;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.estudiante['nombre']}'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _evaluaciones.isEmpty
              ? const Center(child: Text('Este estudiante no tiene evaluaciones'))
              : ListView.builder(
                  itemCount: _evaluaciones.length,
                  itemBuilder: (_, i) {
                    final ev = _evaluaciones[i];
                    final nivel = ev['nivelRiesgo'] as String?;
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      child: ListTile(
                        leading: Icon(Icons.circle, color: _colorNivel(nivel), size: 20),
                        title: Text('${ev['fecha']}', style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('Nivel: $nivel · Confianza: ${ev['confianza']}'),
                        trailing: Text('PHQ9: ${ev['phq9']}'),
                      ),
                    );
                  },
                ),
    );
  }
}