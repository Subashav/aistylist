import 'package:flutter/foundation.dart';
import '../app_config.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class AuthProvider extends ChangeNotifier {
  UserModel? _currentUser;
  String? _token;
  bool _isLoading = false;
  String? _errorMessage;

  UserModel? get currentUser => _currentUser;
  String? get token => _token;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;

  AuthProvider() {
    _initCustomUrl();
  }

  Future<void> _initCustomUrl() async {
    final customUrl = await StorageService.getCustomBackendUrl();
    if (customUrl != null && customUrl.isNotEmpty) {
      AppConfig.setCustomBaseUrl(customUrl);
    }
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  Future<bool> checkAuthSession() async {
    _isLoading = true;
    notifyListeners();

    try {
      final savedToken = await StorageService.getToken();
      if (savedToken == null || savedToken.isEmpty) {
        _isLoading = false;
        notifyListeners();
        return false;
      }

      final response = await ApiService.getMe(savedToken);
      if (response.isSuccess && response.data != null) {
        _token = savedToken;
        _currentUser = response.data;
        await StorageService.saveUser(response.data!);
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        // Token expired or invalid
        await StorageService.clearSession();
        _token = null;
        _currentUser = null;
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (_) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> signUp({
    required String fullName,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final response = await ApiService.signUp(
      fullName: fullName,
      email: email,
      password: password,
      confirmPassword: confirmPassword,
    );

    if (response.isSuccess && response.data != null) {
      final data = response.data!;
      _token = data['access_token'] as String;
      _currentUser = UserModel.fromJson(data['user'] as Map<String, dynamic>);

      await StorageService.saveToken(_token!);
      await StorageService.saveUser(_currentUser!);

      _isLoading = false;
      notifyListeners();
      return true;
    } else {
      _errorMessage = response.errorMessage ?? 'Sign up failed.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> signIn({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final response = await ApiService.signIn(email: email, password: password);

    if (response.isSuccess && response.data != null) {
      final data = response.data!;
      _token = data['access_token'] as String;
      _currentUser = UserModel.fromJson(data['user'] as Map<String, dynamic>);

      await StorageService.saveToken(_token!);
      await StorageService.saveUser(_currentUser!);

      _isLoading = false;
      notifyListeners();
      return true;
    } else {
      _errorMessage = response.errorMessage ?? 'Sign in failed.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<String?> forgotPassword(String email) async {
    _isLoading = true;
    notifyListeners();
    final response = await ApiService.forgotPassword(email);
    _isLoading = false;
    notifyListeners();
    return response.isSuccess ? response.data : response.errorMessage;
  }

  Future<void> logout() async {
    _token = null;
    _currentUser = null;
    _errorMessage = null;
    await StorageService.clearSession();
    notifyListeners();
  }

  Future<void> updateCustomUrl(String newUrl) async {
    AppConfig.setCustomBaseUrl(newUrl);
    await StorageService.saveCustomBackendUrl(newUrl);
    notifyListeners();
  }
}
