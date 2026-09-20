import 'package:flutter/material.dart';
import '../app_config.dart';
import '../models/analysis_result_model.dart';
import '../utils/constants.dart';

/// Fashion-first Editorial Outfit Card Widget
///
/// Designed with a pure luxury white aesthetic:
/// - Palette: White, Obsidian Black, Soft Grey, Subtle Gold Accent
/// - Minimal architectural radius (4px), thin borders (1px solid #E8E8E8)
/// - Looks 1 & 2: Large dominant authentic FASHN VTON Try-On photography
/// - Looks 3 & 4: Refined editorial moodboard with palette swatches & fabric guidance
/// - All Looks: Structured piece breakdown with fabric materials and tactile harmony
class OutfitCard extends StatelessWidget {
  final OutfitSuggestionModel outfit;

  const OutfitCard({super.key, required this.outfit});

  @override
  Widget build(BuildContext context) {
    final isActualTryOn = outfit.isActualTryOn;

    return Container(
      margin: const EdgeInsets.only(bottom: 36),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: AppColors.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x06000000),
            blurRadius: 12,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header: Look Number, Title & Luxury Badge ──────────────────────
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
            decoration: const BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.border)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Text(
                  'LOOK 0${outfit.lookId}',
                  style: const TextStyle(
                    fontFamily: 'Playfair Display',
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.05,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        outfit.title.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                          letterSpacing: 0.8,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${outfit.style}  •  ${outfit.occasion}',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                // Minimal luxury badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: isActualTryOn
                        ? AppColors.background
                        : AppColors.surface,
                    borderRadius: BorderRadius.circular(2),
                    border: Border.all(
                      color: isActualTryOn
                          ? AppColors.accent
                          : AppColors.border,
                    ),
                  ),
                  child: Text(
                    isActualTryOn ? 'ACTUAL TRY-ON' : 'OUTFIT & MATERIAL GUIDE',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: isActualTryOn
                          ? AppColors.accent
                          : AppColors.textSecondary,
                      letterSpacing: 0.6,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // ── Visual Section: High-res Try-On Photo OR Editorial Moodboard ────
          if (isActualTryOn)
            _OutfitImageSection(outfit: outfit)
          else
            _OutfitMoodboardSection(outfit: outfit),

          // ── Card Body: Garment Breakdown, Materials & Palette ───────────────
          Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 1. Personalization Reason / Styling Rationale
                if (outfit.personalizationReason != null &&
                    outfit.personalizationReason!.isNotEmpty) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(2),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'WHY THIS WORKS FOR YOU',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textMuted,
                            letterSpacing: 0.1,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          outfit.personalizationReason!,
                          style: const TextStyle(
                            fontSize: 13,
                            color: AppColors.textPrimary,
                            height: 1.55,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 22),
                ] else ...[
                  Text(
                    outfit.explanation,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                      height: 1.55,
                    ),
                  ),
                  const SizedBox(height: 22),
                ],

                // 2. Complete Head-to-Toe Outfit & Fabric Breakdown
                const Text(
                  'COMPLETE ENSEMBLE PIECES',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textMuted,
                    letterSpacing: 0.12,
                  ),
                ),
                const SizedBox(height: 12),

                // Anchor Piece
                _buildPieceRow(
                  category: 'Original Piece',
                  value: outfit.top,
                  material: outfit.topMaterial.isNotEmpty ? outfit.topMaterial : null,
                  isAnchor: true,
                ),

                // Bottom
                _buildPieceRow(
                  category: 'Bottom',
                  value: outfit.formattedBottom,
                  material: outfit.bottomMaterial.isNotEmpty ? outfit.bottomMaterial : null,
                ),

                // Footwear
                _buildPieceRow(
                  category: 'Footwear',
                  value: outfit.formattedShoes,
                  material: outfit.shoesMaterial.isNotEmpty ? outfit.shoesMaterial : null,
                ),

                // Optional Layer
                if (outfit.formattedLayer.isNotEmpty)
                  _buildPieceRow(
                    category: 'Layer / Jacket',
                    value: outfit.formattedLayer,
                    material: outfit.layerMaterial,
                  ),

                // Accessories
                if (outfit.formattedAccessories.isNotEmpty &&
                    outfit.formattedAccessories.toLowerCase() != 'none')
                  _buildPieceRow(
                    category: 'Accessories',
                    value: outfit.formattedAccessories,
                  ),

                // 3. Fabric Harmony Callout
                if (outfit.fabricHarmony != null &&
                    outfit.fabricHarmony!.isNotEmpty) ...[
                  const SizedBox(height: 18),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(2),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'FABRIC HARMONY & DRAPE',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary,
                            letterSpacing: 0.08,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          outfit.fabricHarmony!,
                          style: const TextStyle(
                            fontSize: 12.5,
                            color: AppColors.textSecondary,
                            height: 1.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],

                // 4. Look Color Palette
                if (outfit.palette.isNotEmpty) ...[
                  const SizedBox(height: 20),
                  const Text(
                    'COLOR PALETTE COORDINATION',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textMuted,
                      letterSpacing: 0.12,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 10,
                    runSpacing: 8,
                    children: outfit.palette.map((p) => _buildPaletteChip(p)).toList(),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPieceRow({
    required String category,
    required String value,
    String? material,
    bool isAnchor = false,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 10),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.baseline,
        textBaseline: TextBaseline.alphabetic,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              category.toUpperCase(),
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: AppColors.textMuted,
                letterSpacing: 0.06,
              ),
            ),
          ),
          Expanded(
            child: RichText(
              text: TextSpan(
                text: value,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
                children: [
                  if (material != null &&
                      material.isNotEmpty &&
                      material.toLowerCase() != 'none')
                    TextSpan(
                      text: '  •  $material',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w400,
                        color: AppColors.textMuted,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPaletteChip(LookPaletteModel swatch) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(2),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 14,
            height: 14,
            decoration: BoxDecoration(
              color: swatch.toFlutterColor(),
              border: Border.all(color: Colors.black12),
            ),
          ),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                swatch.name,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
              Text(
                '${swatch.hex} • ${swatch.role}',
                style: const TextStyle(
                  fontSize: 10,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Dominant Photorealistic Try-On Image Section (Looks 1 & 2)
// ---------------------------------------------------------------------------

class _OutfitImageSection extends StatelessWidget {
  final OutfitSuggestionModel outfit;

  const _OutfitImageSection({required this.outfit});

  @override
  Widget build(BuildContext context) {
    final imageUrl = outfit.effectiveImageUrl;

    if (imageUrl.isEmpty) {
      return _OutfitMoodboardSection(outfit: outfit);
    }

    final fullUrl = AppConfig.buildImageUrl(imageUrl);

    return Stack(
      children: [
        GestureDetector(
          onTap: () => _showEnlargedImage(context, fullUrl, outfit.title),
          child: Image.network(
            fullUrl,
            width: double.infinity,
            height: 460,
            fit: BoxFit.cover,
            alignment: Alignment.topCenter,
            loadingBuilder: (context, child, loadingProgress) {
              if (loadingProgress == null) return child;
              return Container(
                width: double.infinity,
                height: 460,
                color: AppColors.surface,
                child: const Center(
                  child: Text(
                    'Loading high-resolution photograph...',
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.textMuted,
                      letterSpacing: 0.4,
                    ),
                  ),
                ),
              );
            },
            errorBuilder: (context, error, stackTrace) =>
                _OutfitMoodboardSection(outfit: outfit),
          ),
        ),

        // Understated "View Look" cue
        Positioned(
          bottom: 16,
          right: 16,
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () => _showEnlargedImage(context, fullUrl, outfit.title),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xDD111111),
                  borderRadius: BorderRadius.circular(2),
                ),
                child: const Text(
                  'VIEW LOOK →',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.1,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  void _showEnlargedImage(BuildContext context, String fullUrl, String title) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.all(24),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 800),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(2),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      title.toUpperCase(),
                      style: const TextStyle(
                        fontFamily: 'Playfair Display',
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.5,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 20),
                      onPressed: () => Navigator.pop(ctx),
                    ),
                  ],
                ),
              ),
              Image.network(
                fullUrl,
                fit: BoxFit.contain,
                height: MediaQuery.of(context).size.height * 0.72,
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Complete Outfit Moodboard Section (Looks 3 & 4)
// ---------------------------------------------------------------------------

class _OutfitMoodboardSection extends StatelessWidget {
  final OutfitSuggestionModel outfit;

  const _OutfitMoodboardSection({required this.outfit});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: const BoxDecoration(
        color: AppColors.surface,
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'OUTFIT & FABRIC DIRECTION',
            style: TextStyle(
              fontFamily: 'Playfair Display',
              fontSize: 18,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.05,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Calibrated color blocking and tactile material textures',
            style: TextStyle(
              fontSize: 12,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 24),

          // Palette Swatches Bar
          if (outfit.palette.isNotEmpty) ...[
            Row(
              children: outfit.palette.map((p) {
                return Expanded(
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    child: Column(
                      children: [
                        Container(
                          height: 44,
                          decoration: BoxDecoration(
                            color: p.toFlutterColor(),
                            borderRadius: BorderRadius.circular(2),
                            border: Border.all(color: AppColors.border),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          p.name,
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.center,
                        ),
                        Text(
                          p.role,
                          style: const TextStyle(
                            fontSize: 10,
                            color: AppColors.textMuted,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),
          ],

          // Fabric Texture Specs
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: [
              if (outfit.topMaterial.isNotEmpty)
                _buildFabricTag('TOP: ${outfit.topMaterial.toUpperCase()}'),
              if (outfit.bottomMaterial.isNotEmpty)
                _buildFabricTag('BOTTOM: ${outfit.bottomMaterial.toUpperCase()}'),
              if (outfit.shoesMaterial.isNotEmpty)
                _buildFabricTag('FOOTWEAR: ${outfit.shoesMaterial.toUpperCase()}'),
              if (outfit.layerMaterial != null &&
                  outfit.layerMaterial!.isNotEmpty &&
                  outfit.layerMaterial!.toLowerCase() != 'none')
                _buildFabricTag('LAYER: ${outfit.layerMaterial!.toUpperCase()}'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFabricTag(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(2),
        border: Border.all(color: AppColors.border),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.05,
          color: AppColors.textSecondary,
        ),
      ),
    );
  }
}
