import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import '../../viewmodels/auth_viewmodel.dart';
import '../auth/login_view.dart';

class AdminPanel extends StatefulWidget {
  const AdminPanel({super.key});

  @override
  State<AdminPanel> createState() => _AdminPanelState();
}

class _AdminPanelState extends State<AdminPanel> {
  final ApiService _api = ApiService();
  Map<String, dynamic>? _stats;
  List<Map<String, dynamic>> _usuarios = [];
  List<Map<String, dynamic>> _evaluaciones = [];
  bool _loading = true;
  int _tabIndex = 0;

  @override
  void initState() {
    super.initState();
    _cargarDatos();
  }

  Future<void> _cargarDatos() async {
    try {
      final stats = await _api.obtenerStatsAdmin();
      final usuarios = await _api.listarUsuariosAdmin();
      final evaluaciones = await _api.listarEvaluacionesAdmin();
      if (mounted) {
        setState(() {
          _stats = stats;
          _usuarios = usuarios;
          _evaluaciones = evaluaciones;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Color _colorNivel(String? nivel) {
    if (nivel == null) return Colors.grey;
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
        title: const Text('Panel de Administración'),
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
          : Column(
              children: [
                // Tabs
                Row(
                  children: [
                    _TabBtn(label: 'Dashboard', index: 0, current: _tabIndex, onTap: () => setState(() => _tabIndex = 0)),
                    _TabBtn(label: 'Usuarios', index: 1, current: _tabIndex, onTap: () => setState(() => _tabIndex = 1)),
                    _TabBtn(label: 'Evaluaciones', index: 2, current: _tabIndex, onTap: () => setState(() => _tabIndex = 2)),
                  ],
                ),
                const Divider(height: 1),
                Expanded(child: _buildContent()),
              ],
            ),
    );
  }

  Widget _buildContent() {
    switch (_tabIndex) {
      case 0: return _buildDashboard();
      case 1: return _buildUsuarios();
      case 2: return _buildEvaluaciones();
      default: return const SizedBox.shrink();
    }
  }

  Widget _buildDashboard() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Estadísticas', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          if (_stats != null) ...[
            Row(
              children: [
                Expanded(child: _StatCard(title: 'Usuarios', value: '${_stats!['totalUsuarios']}', color: Colors.blue)),
                const SizedBox(width: 8),
                Expanded(child: _StatCard(title: 'Evaluaciones', value: '${_stats!['totalEvaluaciones']}', color: Colors.teal)),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(child: _StatCard(title: 'Riesgo Bajo', value: '${_stats!['riesgoBajo']}', color: Colors.green)),
                const SizedBox(width: 8),
                Expanded(child: _StatCard(title: 'Riesgo Moderado', value: '${_stats!['riesgoModerado']}', color: Colors.orange)),
                const SizedBox(width: 8),
                Expanded(child: _StatCard(title: 'Riesgo Alto', value: '${_stats!['riesgoAlto']}', color: Colors.red)),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildUsuarios() {
    return ListView.builder(
      itemCount: _usuarios.length,
      itemBuilder: (_, i) {
        final u = _usuarios[i];
        return ListTile(
          leading: CircleAvatar(child: Text('${u['nombre']}'[0].toUpperCase())),
          title: Text('${u['nombre']}'),
          subtitle: Text('${u['email']} · ${u['role']}'),
          trailing: Text('${u['carrera']}'),
        );
      },
    );
  }

  Widget _buildEvaluaciones() {
    return ListView.builder(
      itemCount: _evaluaciones.length,
      itemBuilder: (_, i) {
        final e = _evaluaciones[i];
        return ListTile(
          leading: Icon(Icons.circle, color: _colorNivel(e['nivelRiesgo'] as String?), size: 16),
          title: Text('Evaluación #${e['id']}'),
          subtitle: Text('Usuario ID: ${e['usuarioId']} · ${e['fecha']}'),
          trailing: Text('${e['nivelRiesgo']}'),
        );
      },
    );
  }
}

class _TabBtn extends StatelessWidget {
  final String label;
  final int index, current;
  final VoidCallback onTap;
  const _TabBtn({required this.label, required this.index, required this.current, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final selected = index == current;
    return Expanded(
      child: InkWell(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            border: Border(bottom: BorderSide(color: selected ? Colors.teal : Colors.transparent, width: 2)),
          ),
          child: Text(label, textAlign: TextAlign.center, style: TextStyle(fontWeight: selected ? FontWeight.bold : FontWeight.normal)),
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title, value;
  final Color color;
  const _StatCard({required this.title, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(value, style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: color)),
            Text(title, style: const TextStyle(fontSize: 12)),
          ],
        ),
      ),
    );
  }
}