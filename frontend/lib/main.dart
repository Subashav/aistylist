import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'models/saved_result_model.dart';
import 'providers/auth_provider.dart';
import 'providers/analysis_provider.dart';
import 'providers/saved_results_provider.dart';
import 'utils/app_theme.dart';
import 'utils/constants.dart';
import 'screens/splash_screen.dart';
import 'screens/auth/sign_in_screen.dart';
import 'screens/auth/sign_up_screen.dart';
import 'screens/auth/forgot_password_screen.dart';
import 'screens/home_screen.dart';
import 'screens/image_preview_screen.dart';
import 'screens/analysis_loading_screen.dart';
import 'screens/result_screen.dart';
import 'screens/saved_results_screen.dart';
import 'screens/saved_result_detail_screen.dart';
import 'screens/profile_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AiStylistApp());
}

class AiStylistApp extends StatelessWidget {
  const AiStylistApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => AnalysisProvider()),
        ChangeNotifierProvider(create: (_) => SavedResultsProvider()),
      ],
      child: MaterialApp(
        title: AppStrings.appName,
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        initialRoute: AppRoutes.splash,
        onGenerateRoute: (settings) {
          switch (settings.name) {
            case AppRoutes.splash:
              return MaterialPageRoute(builder: (_) => const SplashScreen());
            case AppRoutes.signIn:
              return MaterialPageRoute(builder: (_) => const SignInScreen());
            case AppRoutes.signUp:
              return MaterialPageRoute(builder: (_) => const SignUpScreen());
            case AppRoutes.forgotPassword:
              return MaterialPageRoute(builder: (_) => const ForgotPasswordScreen());
            case AppRoutes.home:
              return MaterialPageRoute(builder: (_) => const HomeScreen());
            case AppRoutes.imagePreview:
              return MaterialPageRoute(builder: (_) => const ImagePreviewScreen());
            case AppRoutes.analysisLoading:
              return MaterialPageRoute(builder: (_) => const AnalysisLoadingScreen());
            case AppRoutes.result:
              return MaterialPageRoute(builder: (_) => const ResultScreen());
            case AppRoutes.savedResults:
              return MaterialPageRoute(builder: (_) => const SavedResultsScreen());
            case AppRoutes.savedResultDetail:
              final item = settings.arguments as SavedResultModel;
              return MaterialPageRoute(builder: (_) => SavedResultDetailScreen(item: item));
            case AppRoutes.profile:
              return MaterialPageRoute(builder: (_) => const ProfileScreen());
            default:
              return MaterialPageRoute(builder: (_) => const SplashScreen());
          }
        },
      ),
    );
  }
}
