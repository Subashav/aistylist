import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/analysis_provider.dart';
import '../utils/constants.dart';
import '../utils/responsive_builder.dart';
import '../widgets/responsive_scaffold.dart';
import '../widgets/custom_image_picker.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final userName = authProvider.currentUser?.fullName ?? 'Fashion Explorer';

    return ResponsiveScaffold(
      currentIndex: 0,
      title: AppStrings.appName,
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.primary, Color(0xFF0F172A)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withValues(alpha: 0.15),
                    blurRadius: 15,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.accent.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.auto_awesome, size: 14, color: AppColors.accentLight),
                            SizedBox(width: 6),
                            Text(
                              'AI COLOR HARMONY ENGINE',
                              style: TextStyle(
                                color: AppColors.accentLight,
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 1.0,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Text(
                    'Hello, $userName ✨',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Upload or capture any clothing item. Our computer vision analyzes its actual fabric color to generate scientifically harmonized fashion pairings.',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withValues(alpha: 0.85),
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            // Main Action Cards
            const Text(
              'Analyze Clothing Garment',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 14),

            ResponsiveBuilder(
              mobile: (ctx) => Column(
                children: [
                  _buildActionCard(
                    context,
                    title: 'Take Clothing Photo',
                    subtitle: 'Opens live camera viewfinder to snap your garment',
                    icon: Icons.photo_camera_outlined,
                    color: AppColors.primary,
                    onTap: () {
                      CustomImagePicker.openCamera(
                        context: context,
                        title: 'Snap Clothing Item',
                        onImageSelected: (bytes, name) {
                          final analysisProvider = Provider.of<AnalysisProvider>(context, listen: false);
                          analysisProvider.setClothingImage(bytes, name);
                          Navigator.pushNamed(context, AppRoutes.imagePreview);
                        },
                      );
                    },
                  ),
                  const SizedBox(height: 12),
                  _buildActionCard(
                    context,
                    title: 'Upload Clothing Photo',
                    subtitle: 'Select an image from device gallery or files',
                    icon: Icons.photo_library_outlined,
                    color: AppColors.accent,
                    onTap: () {
                      CustomImagePicker.openGallery(
                        onImageSelected: (bytes, name) {
                          final analysisProvider = Provider.of<AnalysisProvider>(context, listen: false);
                          analysisProvider.setClothingImage(bytes, name);
                          Navigator.pushNamed(context, AppRoutes.imagePreview);
                        },
                      );
                    },
                  ),
                ],
              ),
              desktop: (ctx) => Row(
                children: [
                  Expanded(
                    child: _buildActionCard(
                      context,
                      title: 'Take Clothing Photo',
                      subtitle: 'Opens live camera / webcam to snap garment',
                      icon: Icons.photo_camera_outlined,
                      color: AppColors.primary,
                      onTap: () {
                        CustomImagePicker.openCamera(
                          context: context,
                          title: 'Snap Clothing Item',
                          onImageSelected: (bytes, name) {
                            final analysisProvider = Provider.of<AnalysisProvider>(context, listen: false);
                            analysisProvider.setClothingImage(bytes, name);
                            Navigator.pushNamed(context, AppRoutes.imagePreview);
                          },
                        );
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildActionCard(
                      context,
                      title: 'Upload Clothing Photo',
                      subtitle: 'Select an image from device files or album',
                      icon: Icons.photo_library_outlined,
                      color: AppColors.accent,
                      onTap: () {
                        CustomImagePicker.openGallery(
                          onImageSelected: (bytes, name) {
                            final analysisProvider = Provider.of<AnalysisProvider>(context, listen: false);
                            analysisProvider.setClothingImage(bytes, name);
                            Navigator.pushNamed(context, AppRoutes.imagePreview);
                          },
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            // Step Guide / Pipeline Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.palette_outlined, color: AppColors.accent, size: 22),
                      SizedBox(width: 10),
                      Text(
                        'Actual Colour Detection Guarantee',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'When you upload or snap a Blue T-shirt, our AI automatically separates the fabric from skin, hair, and backgrounds. It extracts the real RGB & LAB coordinates to identify Royal Blue, Sky Blue, or Navy, ensuring matching recommendations are 100% genuine.',
                    style: TextStyle(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                      height: 1.45,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _buildChip('T-shirt'),
                      _buildChip('Shirt'),
                      _buildChip('Jeans / Pants'),
                      _buildChip('Dress'),
                      _buildChip('Jacket'),
                      _buildChip('Sweater'),
                      _buildChip('Kurta / Saree'),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.border),
          boxShadow: const [
            BoxShadow(
              color: AppColors.cardShadow,
              blurRadius: 8,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios, size: 16, color: AppColors.textSecondary),
          ],
        ),
      ),
    );
  }

  Widget _buildChip(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.border),
      ),
      child: Text(
        label,
        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: AppColors.textPrimary),
      ),
    );
  }
}
