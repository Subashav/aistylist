import 'package:flutter/material.dart';
import 'analysis_result_model.dart';

class SavedResultModel {
  final int id;
  final int userId;
  final String clothingImage;
  final String? userImage;
  final String clothingType;
  final String detectedColour;
  final String colourShade;
  final String hexValue;
  final String rgbValue;
  final double confidence;
  final List<ColourSwatchModel> recommendations;
  final List<OutfitSuggestionModel> outfitSuggestions;
  final String explanations;
  final PersonalizedStyleAnalysisModel? personalizedAnalysis;
  final String createdAt;

  SavedResultModel({
    required this.id,
    required this.userId,
    required this.clothingImage,
    this.userImage,
    required this.clothingType,
    required this.detectedColour,
    required this.colourShade,
    required this.hexValue,
    required this.rgbValue,
    required this.confidence,
    required this.recommendations,
    required this.outfitSuggestions,
    required this.explanations,
    this.personalizedAnalysis,
    required this.createdAt,
  });

  Color toFlutterColor() {
    try {
      final cleanHex = hexValue.replaceAll('#', '');
      return Color(int.parse('FF$cleanHex', radix: 16));
    } catch (_) {
      return Colors.blue;
    }
  }

  factory SavedResultModel.fromJson(Map<String, dynamic> json) {
    var rawSwatches = json['recommendations'] as List? ?? [];
    List<ColourSwatchModel> swatches =
        rawSwatches.map((s) => ColourSwatchModel.fromJson(s as Map<String, dynamic>)).toList();

    var rawOutfits = json['outfit_suggestions'] as List? ?? [];
    List<OutfitSuggestionModel> outfits =
        rawOutfits.map((o) => OutfitSuggestionModel.fromJson(o as Map<String, dynamic>)).toList();

    PersonalizedStyleAnalysisModel? persAnalysis;
    if (json['personalized_analysis'] != null && json['personalized_analysis'] is Map<String, dynamic>) {
      persAnalysis = PersonalizedStyleAnalysisModel.fromJson(json['personalized_analysis'] as Map<String, dynamic>);
    }

    return SavedResultModel(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      clothingImage: json['clothing_image'] as String? ?? '',
      userImage: json['user_image'] as String?,
      clothingType: json['clothing_type'] as String? ?? 'Garment',
      detectedColour: json['detected_colour'] as String? ?? '',
      colourShade: json['colour_shade'] as String? ?? '',
      hexValue: json['hex_value'] as String? ?? '#000000',
      rgbValue: json['rgb_value'] as String? ?? '',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      recommendations: swatches,
      outfitSuggestions: outfits,
      explanations: json['explanations'] as String? ?? '',
      personalizedAnalysis: persAnalysis,
      createdAt: json['created_at'] as String? ?? '',
    );
  }
}
