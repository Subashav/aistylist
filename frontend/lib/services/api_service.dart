import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../app_config.dart';
import '../models/user_model.dart';
import '../models/analysis_result_model.dart';
import '../models/saved_result_model.dart';

class ApiResponse<T> {
  final bool isSuccess;
  final T? data;
  final String? errorMessage;

  ApiResponse.success(this.data)
      : isSuccess = true,
        errorMessage = null;

  ApiResponse.error(this.errorMessage)
      : isSuccess = false,
        data = null;
}

class ApiService {
  static Map<String, String> _headers({String? token, bool isJson = true}) {
    final map = <String, String>{};
    if (isJson) {
      map['Content-Type'] = 'application/json';
      map['Accept'] = 'application/json';
    }
    if (token != null && token.isNotEmpty) {
      map['Authorization'] = 'Bearer $token';
    }
    return map;
  }

  static String _extractError(http.Response response) {
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map && decoded.containsKey('detail')) {
        return decoded['detail'].toString();
      }
      return 'Request failed with status ${response.statusCode}';
    } catch (_) {
      return 'Network error (${response.statusCode}): ${response.reasonPhrase}';
    }
  }

  // --- AUTHENTICATION ---
  static Future<ApiResponse<Map<String, dynamic>>> signUp({
    required String fullName,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    try {
      final url = Uri.parse('${AppConfig.baseUrl}/auth/signup');
      final response = await http.post(
        url,
        headers: _headers(),
        body: jsonEncode({
          'full_name': fullName,
          'email': email,
          'password': password,
          'confirm_password': confirmPassword,
        }),
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse.success(data);
      } else {
        return ApiResponse.error(_extractError(response));
      }
    } catch (e) {
      return ApiResponse.error('Unable to connect to AI Stylist server. Please ensure backend is running at ${AppConfig.baseUrl}');
    }
  }

  static Future<ApiResponse<Map<String, dynamic>>> signIn({
    required String email,
    required String password,
  }) async {
    try {
      final url = Uri.parse('${AppConfig.baseUrl}/auth/signin');
      final response = await http.post(
        url,
        headers: _headers(),
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse.success(data);
      } else {
        return ApiResponse.error(_extractError(response));
      }
    } catch (e) {
      return ApiResponse.error('Unable to connect to AI Stylist server. Please ensure backend is running at ${AppConfig.baseUrl}');
    }
  }

  static Future<ApiResponse<UserModel>> getMe(String token) async {
    try {
      final url = Uri.parse('${AppConfig.baseUrl}/auth/me');
      final response = await http.get(url, headers: _headers(token: token));

      if (response.statusCode == 200) {
        final user = UserModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
        return ApiResponse.success(user);
      } else {
        return ApiResponse.error(_extractError(response));
      }
    } catch (e) {
      return ApiResponse.error('Connection error: $e');
    }
  }

  static Future<ApiResponse<String>> forgotPassword(String email) async {
    try {
      final url = Uri.parse('${AppConfig.baseUrl}/auth/forgot-password');
      final response = await http.post(
        url,
        headers: _headers(),
        body: jsonEncode({'email': email}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ApiResponse.success(data['message']?.toString() ?? 'Reset email dispatched.');
      } else {
        return ApiResponse.error(_extractError(response));
      }
    } catch (e) {
      return ApiResponse.error('Connection error: $e');
    }
  }

  // --- AI ANALYSIS (MULTIPART BYTES UPLOAD) ---
  static Future<ApiResponse<AnalysisResultModel>> analyzeClothing({
    required Uint8List clothingBytes,
    required String clothingFilename,
    Uint8List? userBytes,
    String? userFilename,
    String? categoryHint,
    required String token,
  }) async {
    try {
      final url = Uri.parse('${AppConfig.baseUrl}/analyze');
      final request = http.MultipartRequest('POST', url);

      request.headers['Authorization'] = 'Bearer $token';

      // Attach clothing image
      request.files.add(http.MultipartFile.fromBytes(
        'clothing_image',
        clothingBytes,
        filename: clothingFilename.isNotEmpty ? clothingFilename : 'clothing.jpg',
      ));

      // Attach user photo if present
      if (userBytes != null && userBytes.isNotEmpty) {
        request.files.add(http.MultipartFile.fromBytes(
          'user_image',
          userBytes,
          filename: (userFilename != null && userFilename.isNotEmpty) ? userFilename : 'user_photo.jpg',
        ));
      }

      // Attach clothing category hint
      if (categoryHint != null && categoryHint.isNotEmpty) {
        request.fields['clothing_category_hint'] = categoryHint;
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final result = AnalysisResultModel.fromJson(data);
        return ApiResponse.success(result);
      } else {
        return ApiResponse.error(_extractError(response));
      }
    } catch (e) {
      return ApiResponse.error('Analysis failed: $e');
    }
  }

  // --- SAVED RESULTS ---
  static Future<ApiResponse<SavedResultModel>> saveResult({
    required AnalysisResultModel analysis,
    required String token,
  }) async {
    try {
      final url = Uri.parse('${AppConfig.baseUrl}/saved-results');
      final payload = {
        'clothing_image': analysis.clothingImageUrl,
        'user_image': analysis.userImageUrl,
        'clothing_type': analysis.clothingType,
        'detected_colour': analysis.detectedColour,
        'colour_shade': analysis.colourShade,
        'hex_value': analysis.hexValue,
        'rgb_value': analysis.rgbValue,
        'confidence': analysis.confidence,
        'recommendations': analysis.recommendedColours.map((c) => c.toJson()).toList(),
        'outfit_suggestions': analysis.outfitSuggestions.map((o) => o.toJson()).toList(),
        'explanations': analysis.overallAdvice,
        'personalized_analysis': analysis.personalizedAnalysis?.toJson(),
      };

      final response = await http.post(
        url,
        headers: _headers(token: token),
        body: jsonEncode(payload),
      );

      if (response.statusCode == 201) {
        final item = SavedResultModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
        return ApiResponse.success(item);
      } else {
        return ApiResponse.error(_extractError(response));
      }
    } catch (e) {
      return ApiResponse.error('Failed to save result: $e');
    }
  }

  static Future<ApiResponse<List<SavedResultModel>>> getSavedResults(String token) async {
    try {
      final url = Uri.parse('${AppConfig.baseUrl}/saved-results');
      final response = await http.get(url, headers: _headers(token: token));

      if (response.statusCode == 200) {
        final List list = jsonDecode(response.body) as List;
        final items = list.map((e) => SavedResultModel.fromJson(e as Map<String, dynamic>)).toList();
        return ApiResponse.success(items);
      } else {
        return ApiResponse.error(_extractError(response));
      }
    } catch (e) {
      return ApiResponse.error('Failed to fetch saved results: $e');
    }
  }

  static Future<ApiResponse<bool>> deleteSavedResult(int id, String token) async {
    try {
      final url = Uri.parse('${AppConfig.baseUrl}/saved-results/$id');
      final response = await http.delete(url, headers: _headers(token: token));

      if (response.statusCode == 200) {
        return ApiResponse.success(true);
      } else {
        return ApiResponse.error(_extractError(response));
      }
    } catch (e) {
      return ApiResponse.error('Failed to delete: $e');
    }
  }
}
