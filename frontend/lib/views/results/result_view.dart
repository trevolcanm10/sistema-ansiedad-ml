import 'package:flutter/material.dart';
import '../../models/prediction_response.dart';
import '../home/home_view.dart';

class ResultView extends StatelessWidget {
  final PredictionResponse prediction;

  const ResultView({super.key, required this.prediction});

  Color _getColor() {
    switch (prediction.nivelRiesgo.toUpperCase()) {
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

  IconData _getIcon() {
    switch (prediction.nivelRiesgo.toUpperCase()) {
      case 'BAJO':
        return Icons.check_circle;
      case 'MODERADO':
        return Icons.warning_amber_rounded;
      case 'ALTO':
        return Icons.error;
      default:
        return Icons.help;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _getColor();
    final confianzaStr =
        '${(prediction.confianza * 100).toStringAsFixed(0)}%';
    final probBajoStr = prediction.probabilidadBajoPromedio != null
        ? '${(prediction.probabilidadBajoPromedio! * 100).toStringAsFixed(1)}%'
        : 'N/A';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Resultado'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Badge de nivel de riesgo
            Container(
              padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 24),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: color, width: 2),
              ),
              child: Column(
                children: [
                  Icon(_getIcon(), size: 64, color: color),
                  const SizedBox(height: 16),
                  Text(
                    'Nivel de Riesgo',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    prediction.nivelRiesgo,
                    style: TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Tarjetas de métricas
            Row(
              children: [
                Expanded(
                  child: _MetricCard(
                    label: 'Confianza',
                    value: confianzaStr,
                    color: color,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _MetricCard(
                    label: 'P(BAJO) prom.',
                    value: probBajoStr,
                    color: Colors.teal,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Votos
            if (prediction.votos != null) ...[
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Votos de los modelos',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _VotoBadge(
                            label: 'ALTO',
                            count: prediction.votos!['ALTO'] ?? 0,
                            color: Colors.red,
                          ),
                          _VotoBadge(
                            label: 'BAJO',
                            count: prediction.votos!['BAJO'] ?? 0,
                            color: Colors.green,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
            ],

            // Recomendaciones
            if (prediction.recomendaciones != null &&
                prediction.recomendaciones!.isNotEmpty) ...[
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Recomendaciones',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 12),
                      ...prediction.recomendaciones!.map(
                        (r) => Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('• ', style: TextStyle(fontSize: 16)),
                              Expanded(child: Text(r, style: const TextStyle(fontSize: 14))),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
            ],

            // Botón volver al inicio
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(builder: (_) => const HomeView()),
                    (route) => false,
                  );
                },
                icon: const Icon(Icons.home),
                label: const Text('VOLVER AL INICIO'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _MetricCard({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _VotoBadge extends StatelessWidget {
  final String label;
  final int count;
  final Color color;

  const _VotoBadge({
    required this.label,
    required this.count,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color),
          ),
          child: Text(
            '$count',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(label, style: TextStyle(color: Colors.grey[600])),
      ],
    );
  }
}