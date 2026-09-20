import 'package:flutter/foundation.dart';
import '../models/analysis_result_model.dart';
import '../models/saved_result_model.dart';
import '../services/api_service.dart';

class SavedResultsProvider extends ChangeNotifier {
  List<SavedResultModel> _savedItems = [];
  bool _isLoading = false;
  String? _errorMessage;
  bool _isSaving = false;

  List<SavedResultModel> get savedItems => _savedItems;
  bool get isLoading => _isLoading;
  bool get isSaving => _isSaving;
  String? get errorMessage => _errorMessage;

  Future<void> fetchSavedResults(String token) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final response = await ApiService.getSavedResults(token);
    if (response.isSuccess && response.data != null) {
      _savedItems = response.data!;
      _isLoading = false;
      notifyListeners();
    } else {
      _errorMessage = response.errorMessage;
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> saveAnalysis(AnalysisResultModel analysis, String token) async {
    _isSaving = true;
    _errorMessage = null;
    notifyListeners();

    final response = await ApiService.saveResult(analysis: analysis, token: token);
    _isSaving = false;

    if (response.isSuccess && response.data != null) {
      // Prepend newly saved item to list
      _savedItems.insert(0, response.data!);
      notifyListeners();
      return true;
    } else {
      _errorMessage = response.errorMessage ?? 'Failed to save.';
      notifyListeners();
      return false;
    }
  }

  Future<bool> deleteResult(int id, String token) async {
    final response = await ApiService.deleteSavedResult(id, token);
    if (response.isSuccess) {
      _savedItems.removeWhere((item) => item.id == id);
      notifyListeners();
      return true;
    } else {
      _errorMessage = response.errorMessage ?? 'Failed to delete.';
      notifyListeners();
      return false;
    }
  }
}
