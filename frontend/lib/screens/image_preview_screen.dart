import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/analysis_provider.dart';
import '../utils/constants.dart';
import '../utils/responsive_builder.dart';
import '../widgets/app_button.dart';
import '../widgets/custom_image_picker.dart';

class ImagePreviewScreen extends StatelessWidget {
  const ImagePreviewScreen({super.key});

  final List<String> _categories = const [
    'T-shirt', 'Shirt', 'Top', 'Pants', 'Jeans', 'Trousers',
    'Dress', 'Skirt', 'Jacket', 'Coat', 'Hoodie', 'Sweater',
    'Kurta', 'Saree', 'Other'
  ];

  @override
  Widget build(BuildContext context) {
    final analysisProvider = Provider.of<AnalysisProvider>(context);

    if (!analysisProvider.hasClothingImage) {
      return Scaffold(
        appBar: AppBar(title: const Text('Image Preview')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.image_not_supported_outlined, size: 64, color: AppColors.textSecondary),
              const SizedBox(height: 16),
              const Text('No clothing photo selected'),
              const SizedBox(height: 20),
              AppButton(
                text: 'Go Back to Home',
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Review & Prepare Analysis'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
          child: ConstrainedContent(
            maxWidth: 800,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Clothing Image Box
                const Text(
                  '1. Selected Clothing Garment',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 10),
                Center(
                  child: Stack(
                    children: [
                      Container(
                        height: 280,
                        width: double.infinity,
                        constraints: const BoxConstraints(maxWidth: 450),
                        decoration: BoxDecoration(
                          color: Colors.black,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: const [
                            BoxShadow(
                              color: AppColors.cardShadow,
                              blurRadius: 10,
                              offset: Offset(0, 4),
                            ),
                          ],
                        ),
                        clipBehavior: Clip.antiAlias,
                        child: Image.memory(
                          analysisProvider.clothingImageBytes!,
                          fit: BoxFit.contain,
                        ),
                      ),
                      Positioned(
                        bottom: 12,
                        right: 12,
                        child: ElevatedButton.icon(
                          onPressed: () {
                            CustomImagePicker.showPickerSheet(
                              context: context,
                              title: 'Replace Clothing Photo',
                              onImageSelected: (bytes, name) {
                                analysisProvider.setClothingImage(bytes, name);
                              },
                            );
                          },
                          icon: const Icon(Icons.refresh, size: 16),
                          label: const Text('Retake / Replace', style: TextStyle(fontSize: 12)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.black87,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            minimumSize: Size.zero,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Clothing Category Hint
                const Text(
                  'Garment Type',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  height: 38,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: _categories.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 8),
                    itemBuilder: (ctx, idx) {
                      final cat = _categories[idx];
                      final isSelected = analysisProvider.selectedCategory == cat;
                      return ChoiceChip(
                        label: Text(cat),
                        selected: isSelected,
                        selectedColor: AppColors.primary,
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.white : AppColors.textPrimary,
                          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                          fontSize: 13,
                        ),
                        onSelected: (val) {
                          if (val) analysisProvider.setCategory(cat);
                        },
                      );
                    },
                  ),
                ),
                const SizedBox(height: 28),

                // User Portrait Photo for Virtual Try-On
                Row(
                  children: [
                    const Text(
                      '2. Your Portrait Photo',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        'Virtual Try-On',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text(
                  'Upload your portrait or a full-body photo so AI Stylist can generate personalized virtual try-on looks showing these outfits directly on YOU.',
                  style: TextStyle(fontSize: 13, color: AppColors.textSecondary, height: 1.4),
                ),
                const SizedBox(height: 12),

                if (analysisProvider.hasUserImage) ...[
                  Center(
                    child: Stack(
                      children: [
                        Container(
                          height: 200,
                          width: double.infinity,
                          constraints: const BoxConstraints(maxWidth: 360),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: AppColors.primary, width: 2),
                            boxShadow: [
                              BoxShadow(
                                color: AppColors.primary.withOpacity(0.15),
                                blurRadius: 12,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          clipBehavior: Clip.antiAlias,
                          child: Image.memory(
                            analysisProvider.userImageBytes!,
                            fit: BoxFit.cover,
                          ),
                        ),
                        Positioned(
                          top: 8,
                          right: 8,
                          child: CircleAvatar(
                            backgroundColor: Colors.black54,
                            radius: 16,
                            child: IconButton(
                              icon: const Icon(Icons.close, size: 16, color: Colors.white),
                              onPressed: () => analysisProvider.setUserImage(Uint8List(0), ''),
                            ),
                          ),
                        ),
                        Positioned(
                          bottom: 8,
                          left: 8,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.black.withOpacity(0.7),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: const [
                                Icon(Icons.check_circle, size: 13, color: Color(0xFF4ADE80)),
                                SizedBox(width: 5),
                                Text(
                                  'Try-On Reference Active',
                                  style: TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ] else ...[
                  OutlinedButton.icon(
                    onPressed: () {
                      CustomImagePicker.showPickerSheet(
                        context: context,
                        title: 'Add Your Portrait Photo',
                        onImageSelected: (bytes, name) {
                          analysisProvider.setUserImage(bytes, name);
                        },
                      );
                    },
                    icon: const Icon(Icons.face_retouching_natural, color: AppColors.primary),
                    label: const Text('Add My Portrait Photo (For Virtual Try-On)'),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: AppColors.primary, width: 1.5),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      minimumSize: const Size.fromHeight(52),
                    ),
                  ),
                ],
                const SizedBox(height: 36),

                // Analyze CTA
                AppButton(
                  text: 'Generate Personalized Virtual Try-On',
                  icon: Icons.auto_awesome,
                  onPressed: () {
                    Navigator.pushNamed(context, AppRoutes.analysisLoading);
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

