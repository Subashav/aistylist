import 'package:flutter/foundation.dart';

class AppConfig {
  /// Default API base URL for Web, Desktop, and production deployments.
  /// Can be overridden at build/runtime using `--dart-define=API_BASE_URL=...`
  /// or by changing this single configuration value.
  static const String defaultApiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  /// API base URL used exclusively for Android emulator local networking.
  static const String androidEmulatorBaseUrl = 'http://10.0.2.2:8000';

  static String _customBaseUrl = "";

  static void setCustomBaseUrl(String url) {
    _customBaseUrl = url.trim();
  }

  static String get baseUrl {
    if (_customBaseUrl.isNotEmpty) {
      return _customBaseUrl;
    }
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      return androidEmulatorBaseUrl;
    }
    return defaultApiBaseUrl;
  }

  static String buildImageUrl(String relativeOrAbsoluteUrl) {
    if (relativeOrAbsoluteUrl.isEmpty) return "";
    if (relativeOrAbsoluteUrl.startsWith("http://") || relativeOrAbsoluteUrl.startsWith("https://")) {
      return relativeOrAbsoluteUrl;
    }
    final cleanPath = relativeOrAbsoluteUrl.startsWith("/") ? relativeOrAbsoluteUrl : "/$relativeOrAbsoluteUrl";
    return "$baseUrl$cleanPath";
  }
}
