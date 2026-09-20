import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/analysis_provider.dart';
import '../utils/constants.dart';

class AnalysisLoadingScreen extends StatefulWidget {
  const AnalysisLoadingScreen({super.key});

  @override
  State<AnalysisLoadingScreen> createState() => _AnalysisLoadingScreenState();
}

class _AnalysisLoadingScreenState extends State<AnalysisLoadingScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _startAnalysis());
  }

  Future<void> _startAnalysis() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final analysisProvider = Provider.of<AnalysisProvider>(context, listen: false);

    final token = authProvider.token ?? '';
    final success = await analysisProvider.runAnalysis(token);

    if (!mounted) return;
    if (success) {
      Navigator.pushReplacementNamed(context, AppRoutes.result);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(analysisProvider.errorMessage ?? 'Analysis encountered an issue.'),
          backgroundColor: AppColors.error,
        ),
      );
      Navigator.pop(context); // Return to preview screen to adjust
    }
  }

  @override
  Widget build(BuildContext context) {
    final analysisProvider = Provider.of<AnalysisProvider>(context);

    return Scaffold(
      backgroundColor: AppColors.primary,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Pulsing Icon
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.08),
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.accent, width: 2),
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  size: 38,
                  color: AppColors.accent,
                ),
              ),
              const SizedBox(height: 32),
              const Text(
                'AI Stylist at Work',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 12),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                child: Text(
                  analysisProvider.currentStepText,
                  key: ValueKey(analysisProvider.currentStepText),
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.85),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              const SizedBox(height: 36),
              SizedBox(
                width: 180,
                child: LinearProgressIndicator(
                  backgroundColor: Colors.white.withOpacity(0.15),
                  valueColor: const AlwaysStoppedAnimation<Color>(AppColors.accent),
                  minHeight: 4,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
