import 'package:flutter/material.dart';

class AppColors {
  // Premium luxury fashion-tech palette (White + Black + Soft Grey)
  static const Color primary = Color(0xFF111111);       // True Obsidian Black
  static const Color primaryLight = Color(0xFF333333);
  static const Color accent = Color(0xFFB79B6C);        // Subdued Luxury Gold / Brass
  static const Color accentLight = Color(0xFFCBB58F);
  static const Color background = Color(0xFFFFFFFF);    // Pure Editorial White
  static const Color surface = Color(0xFFF7F7F5);       // Soft Background / Warm Grey
  static const Color textPrimary = Color(0xFF111111);   // Primary Typography
  static const Color textSecondary = Color(0xFF555555); // Editorial Secondary
  static const Color textMuted = Color(0xFF888888);     // Small Metadata
  static const Color border = Color(0xFFE8E8E8);        // Thin Architectural Border
  static const Color error = Color(0xFFB91C1C);
  static const Color success = Color(0xFF15803D);
  static const Color cardShadow = Color(0x05000000);    // Restrained Subtle Shadow
}

class AppRoutes {
  static const String splash = '/';
  static const String signIn = '/signin';
  static const String signUp = '/signup';
  static const String forgotPassword = '/forgot-password';
  static const String home = '/home';
  static const String imageInput = '/image-input';
  static const String imagePreview = '/image-preview';
  static const String analysisLoading = '/analysis-loading';
  static const String result = '/result';
  static const String savedResults = '/saved-results';
  static const String savedResultDetail = '/saved-result-detail';
  static const String profile = '/profile';
}

class AppStrings {
  static const String appName = 'AI Stylist';
  static const String appTagline = 'Personalised Fashion Harmony';
}
