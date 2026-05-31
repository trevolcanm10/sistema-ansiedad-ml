import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../viewmodels/evaluation_viewmodel.dart';
import '../results/result_view.dart';

class EvaluationView extends StatelessWidget {
  const EvaluationView({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => EvaluationViewModel(),
      child: const _EvaluationBody(),
    );
  }
}

class _EvaluationBody extends StatefulWidget {
  const _EvaluationBody();

  @override
  State<_EvaluationBody> createState() => _EvaluationBodyState();
}

class _EvaluationBodyState extends State<_EvaluationBody> {
  final _pageController = PageController();
  int _currentPage = 0;

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    final ev = context.read<EvaluationViewModel>();
    final success = await ev.enviarEvaluacion();

    if (success && mounted && ev.prediction != null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => ResultView(prediction: ev.prediction!),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Pregunta ${_currentPage + 1} de 15'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Barra de progreso
          LinearProgressIndicator(
            value: (_currentPage + 1) / 15,
            backgroundColor: Colors.grey[200],
            valueColor: const AlwaysStoppedAnimation(Colors.teal),
          ),
          Expanded(
            child: PageView(
              controller: _pageController,
              onPageChanged: (p) => setState(() => _currentPage = p),
              children: [
                _SliderQuestion(
                  label: 'PHQ-9: ¿Con qué frecuencia has tenido poco interés o placer al hacer cosas?',
                  min: 0, max: 27, divisions: 27,
                  value: context.watch<EvaluationViewModel>().phq9,
                  onChanged: (v) => context.read<EvaluationViewModel>().setPhq9(v),
                ),
                _SliderQuestion(
                  label: 'GAD-7: ¿Con qué frecuencia te has sentido nervioso/a, ansioso/a o al límite?',
                  min: 0, max: 21, divisions: 21,
                  value: context.watch<EvaluationViewModel>().gad7,
                  onChanged: (v) => context.read<EvaluationViewModel>().setGad7(v),
                ),
                _SliderQuestion(
                  label: 'Horas de sueño por noche',
                  min: 0, max: 12, divisions: 12,
                  value: context.watch<EvaluationViewModel>().sleepHours,
                  onChanged: (v) => context.read<EvaluationViewModel>().setSleepHours(v),
                ),
                _SliderQuestion(
                  label: 'Frecuencia de ejercicio (días por semana)',
                  min: 0, max: 7, divisions: 7,
                  value: context.watch<EvaluationViewModel>().exerciseFreq,
                  onChanged: (v) => context.read<EvaluationViewModel>().setExerciseFreq(v),
                ),
                _SliderQuestion(
                  label: 'Actividad social (0=mínima, 10=máxima)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().socialActivity,
                  onChanged: (v) => context.read<EvaluationViewModel>().setSocialActivity(v),
                ),
                _SliderQuestion(
                  label: 'Estrés por redes sociales/online (0=nada, 10=mucho)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().onlineStress,
                  onChanged: (v) => context.read<EvaluationViewModel>().setOnlineStress(v),
                ),
                _SliderQuestion(
                  label: 'Promedio ponderado (GPA)',
                  min: 0, max: 5, divisions: 50,
                  value: context.watch<EvaluationViewModel>().gpa,
                  onChanged: (v) => context.read<EvaluationViewModel>().setGpa(v),
                ),
                _SliderQuestion(
                  label: 'Apoyo familiar (0=nada, 10=mucho)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().familySupport,
                  onChanged: (v) => context.read<EvaluationViewModel>().setFamilySupport(v),
                ),
                _SliderQuestion(
                  label: 'Tiempo de pantalla diario (horas)',
                  min: 0, max: 16, divisions: 16,
                  value: context.watch<EvaluationViewModel>().screenTime,
                  onChanged: (v) => context.read<EvaluationViewModel>().setScreenTime(v),
                ),
                _SliderQuestion(
                  label: 'Estrés académico (0=nada, 10=mucho)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().academicStress,
                  onChanged: (v) => context.read<EvaluationViewModel>().setAcademicStress(v),
                ),
                _SliderQuestion(
                  label: 'Calidad de dieta (0=mala, 10=excelente)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().dietQuality,
                  onChanged: (v) => context.read<EvaluationViewModel>().setDietQuality(v),
                ),
                _SliderQuestion(
                  label: 'Autoeficacia (0=nada capaz, 10=muy capaz)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().selfEfficacy,
                  onChanged: (v) => context.read<EvaluationViewModel>().setSelfEfficacy(v),
                ),
                _SliderQuestion(
                  label: 'Relaciones con pares (0=malas, 10=excelentes)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().peerRelationship,
                  onChanged: (v) => context.read<EvaluationViewModel>().setPeerRelationship(v),
                ),
                _SliderQuestion(
                  label: 'Estrés financiero (0=nada, 10=mucho)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().financialStress,
                  onChanged: (v) => context.read<EvaluationViewModel>().setFinancialStress(v),
                ),
                _SliderQuestion(
                  label: 'Calidad del sueño (0=mala, 10=excelente)',
                  min: 0, max: 10, divisions: 10,
                  value: context.watch<EvaluationViewModel>().sleepQuality,
                  onChanged: (v) => context.read<EvaluationViewModel>().setSleepQuality(v),
                ),
              ],
            ),
          ),
          // Botones de navegación
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (_currentPage > 0)
                  TextButton(
                    onPressed: () => _pageController.previousPage(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeInOut,
                    ),
                    child: const Text('Anterior'),
                  )
                else
                  const SizedBox.shrink(),
                Consumer<EvaluationViewModel>(
                  builder: (_, ev, _) {
                    if (_currentPage == 14) {
                      return ElevatedButton(
                        onPressed: ev.isLoading ? null : _enviar,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.teal,
                          foregroundColor: Colors.white,
                        ),
                        child: ev.isLoading
                            ? const SizedBox(
                                height: 24,
                                width: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Text('ENVIAR EVALUACIÓN'),
                      );
                    }
                    return ElevatedButton(
                      onPressed: () => _pageController.nextPage(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut,
                      ),
                      child: const Text('Siguiente'),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SliderQuestion extends StatelessWidget {
  final String label;
  final double min, max;
  final int divisions;
  final double value;
  final ValueChanged<double> onChanged;

  const _SliderQuestion({
    required this.label,
    required this.min,
    required this.max,
    required this.divisions,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            label: value.toStringAsFixed(0),
            onChanged: onChanged,
            activeColor: Colors.teal,
          ),
          const SizedBox(height: 8),
          Text(
            'Valor: ${value.toStringAsFixed(0)}',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
}