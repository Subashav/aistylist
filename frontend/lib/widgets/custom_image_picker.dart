import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../screens/camera_capture_screen.dart';
import '../utils/constants.dart';

class CustomImagePicker {
  static final ImagePicker _picker = ImagePicker();

  static Future<void> openCamera({
    required BuildContext context,
    String title = 'Take Clothing Photo',
    required void Function(Uint8List bytes, String filename) onImageSelected,
  }) async {
    final result = await Navigator.push<Map<String, dynamic>>(
      context,
      MaterialPageRoute(
        builder: (_) => CameraCaptureScreen(title: title),
      ),
    );

    if (result != null && result['bytes'] != null) {
      onImageSelected(result['bytes'] as Uint8List, result['name'] as String? ?? 'camera_photo.jpg');
    }
  }

  static Future<void> openGallery({
    required void Function(Uint8List bytes, String filename) onImageSelected,
  }) async {
    try {
      final XFile? file = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1600,
        maxHeight: 1600,
        imageQuality: 88,
      );
      if (file != null) {
        final bytes = await file.readAsBytes();
        onImageSelected(bytes, file.name);
      }
    } catch (e) {
      debugPrint('Error picking from gallery: $e');
    }
  }

  static Future<void> showPickerSheet({
    required BuildContext context,
    required String title,
    required void Function(Uint8List bytes, String filename) onImageSelected,
  }) async {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 20),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.camera_alt_outlined, color: AppColors.primary),
                ),
                title: const Text(
                  'Take Photo (Open Live Camera)',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                subtitle: const Text('Open camera viewfinder to snap photo'),
                onTap: () async {
                  Navigator.pop(ctx);
                  await openCamera(context: context, title: title, onImageSelected: onImageSelected);
                },
              ),
              const SizedBox(height: 8),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.accent.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.photo_library_outlined, color: AppColors.accent),
                ),
                title: const Text(
                  'Upload from Gallery / Files',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                subtitle: const Text('Choose an existing photo from device'),
                onTap: () async {
                  Navigator.pop(ctx);
                  await openGallery(onImageSelected: onImageSelected);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
