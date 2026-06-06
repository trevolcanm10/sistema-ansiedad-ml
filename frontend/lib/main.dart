import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'viewmodels/auth_viewmodel.dart';
import 'views/auth/login_view.dart';
import 'views/home/home_view.dart';
import 'views/admin/admin_panel.dart';
import 'views/medico/medico_panel.dart';

void main() async {
  // Leer SharedPreferences ANTES de montar la app
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final savedRole = prefs.getString('user_role');
  final savedToken = prefs.getString('jwt_token');

  runApp(
    MyApp(
      initialRole: savedToken != null ? savedRole : null,
    ),
  );
}

class MyApp extends StatelessWidget {
  final String? initialRole;
  const MyApp({super.key, this.initialRole});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AuthViewModel(),
      child: MaterialApp(
        title: 'Bienestar Estudiantil',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorSchemeSeed: Colors.teal,
          useMaterial3: true,
          brightness: Brightness.light,
        ),
        home: AuthGate(initialRole: initialRole),
      ),
    );
  }
}

/// AuthGate recibe el rol desde SharedPreferences al arrancar.
/// Si no hay sesión, redirige al LoginView.
/// Si hay sesión, redirige según el rol.
class AuthGate extends StatefulWidget {
  final String? initialRole;
  const AuthGate({super.key, this.initialRole});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  @override
  void initState() {
    super.initState();
    // Al arrancar, inicializar el AuthViewModel si hay sesión guardada
    if (widget.initialRole != null) {
      context.read<AuthViewModel>().setLoggedIn(widget.initialRole!);
    }
  }

  @override
  Widget build(BuildContext context) {
    // Escuchar cambios en AuthViewModel
    return Consumer<AuthViewModel>(
      builder: (_, auth, _) {
        // Si no está logueado, mostrar login
        if (!auth.isLoggedIn) {
          return const LoginView();
        }

        // Usar el role del ViewModel (se actualiza al hacer login/logout)
        final role = auth.role;

        if (role == 'ROLE_ADMIN') {
          return const AdminPanel();
        } else if (role == 'ROLE_MEDICO') {
          return const MedicoPanel();
        }

        // Por defecto: Estudiante o cualquiera
        return const HomeView();
      },
    );
  }
}