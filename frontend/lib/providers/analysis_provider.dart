import 'package:flutter/foundation.dart';
import '../models/analysis_result_model.dart';
import '../services/api_service.dart';

class AnalysisProvider extends ChangeNotifier {
  Uint8List? _clothingImageBytes;
  String? _clothingImageName;
  Uint8List? _userImageBytes;
  String? _userImageName;
  String _selectedCategory = 'T-shirt';

  bool _isAnalyzing = false;
  String _currentStepText = 'Preparing image...';
  AnalysisResultModel? _currentResult;
  String? _errorMessage;

  Uint8List? get clothingImageBytes => _clothingImageBytes;
  String? get clothingImageName => _clothingImageName;
  Uint8List? get userImageBytes => _userImageBytes;
  String? get userImageName => _userImageName;
  String get selectedCategory => _selectedCategory;

  bool get isAnalyzing => _isAnalyzing;
  String get currentStepText => _currentStepText;
  AnalysisResultModel? get currentResult => _currentResult;
  String? get errorMessage => _errorMessage;

  bool get hasClothingImage => _clothingImageBytes != null && _clothingImageBytes!.isNotEmpty;
  bool get hasUserImage => _userImageBytes != null && _userImageBytes!.isNotEmpty;

  void setClothingImage(Uint8List bytes, String name) {
    _clothingImageBytes = bytes;
    _clothingImageName = name;
    _errorMessage = null;
    notifyListeners();
  }

  void setUserImage(Uint8List bytes, String name) {
    _userImageBytes = bytes;
    _userImageName = name;
    notifyListeners();
  }

  void setCategory(String category) {
    _selectedCategory = category;
    notifyListeners();
  }

  void clearImages() {
    _clothingImageBytes = null;
    _clothingImageName = null;
    _userImageBytes = null;
    _userImageName = null;
    _currentResult = null;
    _errorMessage = null;
    notifyListeners();
  }

  void clearResult() {
    _currentResult = null;
    _errorMessage = null;
    notifyListeners();
  }

  Future<bool> runAnalysis(String token) async {
    if (_clothingImageBytes == null) {
      _errorMessage = 'Please provide a clothing photo first.';
      notifyListeners();
      return false;
    }

    _isAnalyzing = true;
    _errorMessage = null;
    _currentStepText = 'Analyzing your garment...';
    notifyListeners();

    // Step 2 indicator
    await Future.delayed(const Duration(milliseconds: 600));
    _currentStepText = 'Understanding your style...';
    notifyListeners();

    // Step 3 indicator
    await Future.delayed(const Duration(milliseconds: 600));
    _currentStepText = 'Creating your personalized look...';
    notifyListeners();

    // Step 4 — actual API call
    await Future.delayed(const Duration(milliseconds: 500));
    _currentStepText = hasUserImage
        ? 'Generating your try-on image...'
        : 'Generating your outfit look...';
    notifyListeners();

    final response = await ApiService.analyzeClothing(
      clothingBytes: _clothingImageBytes!,
      clothingFilename: _clothingImageName ?? 'clothing.jpg',
      userBytes: _userImageBytes,
      userFilename: _userImageName,
      categoryHint: _selectedCategory,
      token: token,
    );

    if (response.isSuccess && response.data != null) {
      _currentStepText = 'Finalizing your look...';
      notifyListeners();
      await Future.delayed(const Duration(milliseconds: 300));

      _currentResult = response.data;
      _isAnalyzing = false;
      notifyListeners();
      return true;
    } else {

      _errorMessage = response.errorMessage ?? 'Analysis failed. Please try again with a clearer photo.';
      _isAnalyzing = false;
      notifyListeners();
      return false;
    }
  }
}
