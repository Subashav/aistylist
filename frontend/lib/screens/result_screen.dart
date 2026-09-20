import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/analysis_provider.dart';
import '../providers/saved_results_provider.dart';
import '../utils/constants.dart';
import '../utils/responsive_builder.dart';
import '../widgets/app_button.dart';
import '../widgets/colour_swatch_card.dart';
import '../widgets/outfit_card.dart';

class ResultScreen extends StatefulWidget {
  const ResultScreen({super.key});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool _isSaved = false;

  Future<void> _handleSave() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final analysisProvider = Provider.of<AnalysisProvider>(context, listen: false);
    final savedProvider = Provider.of<SavedResultsProvider>(context, listen: false);

    final result = analysisProvider.currentResult;
    final token = authProvider.token;

    if (result == null || token == null) return;

    final success = await savedProvider.saveAnalysis(result, token);
    if (!mounted) return;

    if (success) {
      setState(() {
        _isSaved = true;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Look saved to your wardrobe!'),
          backgroundColor: AppColors.success,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(savedProvider.errorMessage ?? 'Failed to save look.'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final analysisProvider = Provider.of<AnalysisProvider>(context);
    final savedProvider = Provider.of<SavedResultsProvider>(context);
    final result = analysisProvider.currentResult;

    if (result == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Analysis Results')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('No analysis available.'),
              const SizedBox(height: 16),
              AppButton(
                text: 'Go to Home',
                onPressed: () => Navigator.pushReplacementNamed(context, AppRoutes.home),
              ),
            ],
          ),
        ),
      );
    }

    final detectedColor = result.toFlutterColor();
    final confidencePercent = (result.confidence * 100).toInt();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Fashion Harmony Results'),
        actions: [
          IconButton(
            icon: Icon(
              _isSaved ? Icons.bookmark : Icons.bookmark_border,
              color: _isSaved ? AppColors.accent : AppColors.textPrimary,
            ),
            tooltip: 'Save to Wardrobe',
            onPressed: _isSaved ? null : _handleSave,
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
          child: ConstrainedContent(
            maxWidth: 880,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 1. Personalized Style Analysis Header Card
                if (result.personalizedAnalysis != null) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(22),
                      boxShadow: const [
                        BoxShadow(
                          color: Colors.black26,
                          blurRadius: 16,
                          offset: Offset(0, 6),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: AppColors.accent.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Icon(
                                Icons.face_retouching_natural,
                                color: AppColors.accent,
                                size: 22,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'YOUR PERSONALIZED STYLE ANALYSIS',
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w800,
                                      color: AppColors.accent,
                                      letterSpacing: 1.0,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    result.personalizedAnalysis!.garmentSummary,
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.w700,
                                      color: Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        const Divider(color: Colors.white12, height: 1),
                        const SizedBox(height: 16),
                        const Text(
                          'HOW THIS GARMENT WORKS WITH YOU',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: Colors.white60,
                            letterSpacing: 0.8,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          result.personalizedAnalysis!.howItWorksWithYou,
                          style: const TextStyle(
                            fontSize: 14,
                            color: Colors.white,
                            height: 1.55,
                            fontWeight: FontWeight.w400,
                          ),
                        ),
                        if (result.personalizedAnalysis!.complexionHarmony != null) ...[
                          const SizedBox(height: 12),
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(Icons.palette_outlined, size: 16, color: AppColors.accent),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  result.personalizedAnalysis!.complexionHarmony!,
                                  style: const TextStyle(
                                    fontSize: 13,
                                    color: Colors.white70,
                                    height: 1.45,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.08),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.white10),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                result.personalizedAnalysis!.isPersonalized
                                    ? Icons.check_circle_outline
                                    : Icons.info_outline,
                                size: 16,
                                color: result.personalizedAnalysis!.isPersonalized
                                    ? const Color(0xFF4ADE80)
                                    : const Color(0xFFFBBF24),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  result.personalizedAnalysis!.isPersonalized
                                      ? 'AI Personalized Try-On Active • ${result.outfitSuggestions.length} looks styled for you'
                                      : (result.personalizedAnalysis!.validationMessage ??
                                          'Virtual Try-On unavailable: Your personalized outfit recommendation is still available with AI Outfit Preview.'),
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: result.personalizedAnalysis!.isPersonalized
                                        ? const Color(0xFF4ADE80)
                                        : const Color(0xFFFBBF24),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),

                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // 2. Detected Garment Color Card (Clean & Compact)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: AppColors.border),
                    boxShadow: const [
                      BoxShadow(
                        color: AppColors.cardShadow,
                        blurRadius: 10,
                        offset: Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                          color: detectedColor,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: Colors.black12, width: 1.5),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              result.clothingType.toUpperCase(),
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.8,
                                color: AppColors.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              result.colourShade,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'HEX: ${result.hexValue.toUpperCase()}  •  Confidence: $confidencePercent%',
                              style: const TextStyle(
                                fontSize: 12,
                                fontFamily: 'monospace',
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 28),

                // 3. Dominant Section: YOUR PERSONALIZED LOOKS
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.checkroom, color: AppColors.primary, size: 22),
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'YOUR 4 WAYS TO WEAR IT',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w900,
                            color: AppColors.textPrimary,
                            letterSpacing: -0.4,
                          ),
                        ),
                        Text(
                          '4 Distinct Styling Combinations for Your Uploaded Garment',
                          style: const TextStyle(
                            fontSize: 13,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Outfits as the Hero Element
                ...result.outfitSuggestions.map((outfit) => OutfitCard(outfit: outfit)),
                const SizedBox(height: 24),

                // 4. Harmonious Colour Swatches
                Row(
                  children: [
                    const Icon(Icons.palette_outlined, color: AppColors.accent, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Harmonious Palettes for ${result.detectedColour}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                ...result.recommendedColours.map((swatch) => ColourSwatchCard(swatch: swatch, detectedColour: result.detectedColour)),
                const SizedBox(height: 24),

                AppButton(
                  text: _isSaved ? 'Saved to Wardrobe' : 'Save Look to Wardrobe',
                  icon: _isSaved ? Icons.check : Icons.bookmark_add_outlined,
                  backgroundColor: _isSaved ? AppColors.success : AppColors.primary,
                  isLoading: savedProvider.isSaving,
                  onPressed: _isSaved ? null : _handleSave,
                ),
                const SizedBox(height: 12),
                AppButton(
                  text: 'Analyze Another Item',
                  isOutlined: true,
                  icon: Icons.photo_camera_outlined,
                  onPressed: () {
                    analysisProvider.clearImages();
                    Navigator.pushReplacementNamed(context, AppRoutes.home);
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

