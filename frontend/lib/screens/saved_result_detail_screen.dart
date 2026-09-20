import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/saved_result_model.dart';
import '../providers/auth_provider.dart';
import '../providers/saved_results_provider.dart';
import '../utils/constants.dart';
import '../utils/responsive_builder.dart';
import '../widgets/colour_swatch_card.dart';
import '../widgets/outfit_card.dart';

class SavedResultDetailScreen extends StatelessWidget {
  final SavedResultModel item;

  const SavedResultDetailScreen({super.key, required this.item});

  @override
  Widget build(BuildContext context) {
    final color = item.toFlutterColor();
    final confidencePercent = (item.confidence * 100).toInt();

    return Scaffold(
      appBar: AppBar(
        title: Text('${item.colourShade} ${item.clothingType}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline, color: AppColors.error),
            tooltip: 'Delete Saved Look',
            onPressed: () async {
              final authProvider = Provider.of<AuthProvider>(context, listen: false);
              final savedProvider = Provider.of<SavedResultsProvider>(context, listen: false);

              final confirmed = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Delete Saved Look?'),
                  content: const Text('Are you sure you want to permanently delete this look?'),
                  actions: [
                    TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
                      onPressed: () => Navigator.pop(ctx, true),
                      child: const Text('Delete'),
                    ),
                  ],
                ),
              );

              if (confirmed == true && context.mounted) {
                await savedProvider.deleteResult(item.id, authProvider.token ?? '');
                if (context.mounted) {
                  Navigator.pop(context);
                }
              }
            },
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
                // Color banner
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 70,
                        height: 70,
                        decoration: BoxDecoration(
                          color: color,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: Colors.black12, width: 2),
                        ),
                      ),
                      const SizedBox(width: 18),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  item.clothingType.toUpperCase(),
                                  style: const TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    color: AppColors.textSecondary,
                                  ),
                                ),
                                Text(
                                  '$confidencePercent% Confidence',
                                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppColors.success),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              item.colourShade,
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'HEX: ${item.hexValue.toUpperCase()}  •  RGB: (${item.rgbValue})',
                              style: const TextStyle(fontSize: 13, fontFamily: 'monospace', color: AppColors.textSecondary),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Personalized Style Analysis Banner if present
                if (item.personalizedAnalysis != null) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.auto_awesome, color: AppColors.accent, size: 20),
                            const SizedBox(width: 8),
                            const Text(
                              'PERSONALIZED STYLE ANALYSIS',
                              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppColors.accent, letterSpacing: 0.8),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          item.personalizedAnalysis!.howItWorksWithYou,
                          style: const TextStyle(fontSize: 13, color: Colors.white, height: 1.5),
                        ),
                        if (item.personalizedAnalysis!.complexionHarmony != null) ...[
                          const SizedBox(height: 10),
                          Text(
                            item.personalizedAnalysis!.complexionHarmony!,
                            style: const TextStyle(fontSize: 12, color: Colors.white70, height: 1.4),
                          ),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // Hero Try-On Outfits
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
                    const Text(
                      'SAVED PERSONALIZED LOOKS',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppColors.textPrimary, letterSpacing: -0.3),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                ...item.outfitSuggestions.map((o) => OutfitCard(outfit: o)),
                const SizedBox(height: 24),

                // Matching Colors
                const Text(
                  'Recommended Harmonious Colours',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 12),
                ...item.recommendations.map((s) => ColourSwatchCard(swatch: s, detectedColour: item.detectedColour)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
