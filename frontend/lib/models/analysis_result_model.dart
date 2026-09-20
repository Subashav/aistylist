import 'package:flutter/material.dart';

class ColourSwatchModel {
  final String name;
  final String hex;
  final String rgb;
  final String harmonyType;
  final String reason;

  ColourSwatchModel({
    required this.name,
    required this.hex,
    required this.rgb,
    required this.harmonyType,
    required this.reason,
  });

  Color toFlutterColor() {
    try {
      final cleanHex = hex.replaceAll('#', '');
      return Color(int.parse('FF$cleanHex', radix: 16));
    } catch (_) {
      return Colors.grey;
    }
  }

  factory ColourSwatchModel.fromJson(Map<String, dynamic> json) {
    return ColourSwatchModel(
      name: json['name'] as String? ?? 'Harmonious Tone',
      hex: json['hex'] as String? ?? '#FFFFFF',
      rgb: json['rgb'] as String? ?? '255, 255, 255',
      harmonyType: json['harmony_type'] as String? ?? 'Neutral Contrast',
      reason: json['reason'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'hex': hex,
      'rgb': rgb,
      'harmony_type': harmonyType,
      'reason': reason,
    };
  }
}

class LookPaletteModel {
  final String name;
  final String hex;
  final String role;

  LookPaletteModel({
    required this.name,
    required this.hex,
    required this.role,
  });

  Color toFlutterColor() {
    try {
      final cleanHex = hex.replaceAll('#', '');
      return Color(int.parse('FF$cleanHex', radix: 16));
    } catch (_) {
      return Colors.grey;
    }
  }

  factory LookPaletteModel.fromJson(Map<String, dynamic> json) {
    return LookPaletteModel(
      name: json['name'] as String? ?? 'Tone',
      hex: json['hex'] as String? ?? '#888888',
      role: json['role'] as String? ?? 'Accent',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'hex': hex,
      'role': role,
    };
  }
}

class OutfitSuggestionModel {
  final int lookId;
  final String title;
  final String style;
  final String occasion;
  final String top;
  final String topItem;
  final String topColor;
  final String topMaterial;
  final String bottom;
  final String bottomItem;
  final String bottomColor;
  final String bottomMaterial;
  final String shoes;
  final String shoesItem;
  final String shoesColor;
  final String shoesMaterial;
  final String? layerItem;
  final String? layerColor;
  final String? layerMaterial;
  final String accessories;
  final List<String> accessoriesList;
  final String? fabricHarmony;
  final List<LookPaletteModel> palette;
  final String explanation;
  /// Virtual Try-On image URL returned by the backend try-on provider.
  final String? imageUrl;
  final String? tryOnImageUrl;
  /// User-specific reason explaining why this look works for this individual.
  final String? personalizationReason;
  /// Try-On Type: "actual_try_on", "outfit_guide", "outfit_preview", or "unavailable"
  final String tryOnType;
  final String resultType;
  final String provider;

  OutfitSuggestionModel({
    this.lookId = 1,
    required this.title,
    this.style = 'Clean casual',
    required this.occasion,
    required this.top,
    this.topItem = '',
    this.topColor = '',
    this.topMaterial = '',
    required this.bottom,
    this.bottomItem = '',
    this.bottomColor = '',
    this.bottomMaterial = '',
    required this.shoes,
    this.shoesItem = '',
    this.shoesColor = '',
    this.shoesMaterial = '',
    this.layerItem,
    this.layerColor,
    this.layerMaterial,
    required this.accessories,
    this.accessoriesList = const [],
    this.fabricHarmony,
    this.palette = const [],
    required this.explanation,
    this.imageUrl,
    this.tryOnImageUrl,
    this.personalizationReason,
    this.tryOnType = 'actual_try_on',
    this.resultType = 'actual_try_on',
    this.provider = 'fashn_vton_local',
  });

  bool get isActualTryOn =>
      (tryOnType == 'actual_try_on' || resultType == 'actual_try_on') &&
      effectiveImageUrl.isNotEmpty;

  bool get isOutfitGuide =>
      tryOnType == 'outfit_guide' ||
      resultType == 'outfit_guide' ||
      effectiveImageUrl.isEmpty;

  bool get isOutfitPreview =>
      tryOnType == 'outfit_preview' || resultType == 'outfit_preview';

  String get effectiveImageUrl => tryOnImageUrl ?? imageUrl ?? '';

  String get formattedTop {
    if (topMaterial.isNotEmpty) {
      return '$top  ($topMaterial)';
    }
    return top;
  }

  String get formattedBottom {
    if (bottomColor.isNotEmpty && bottomItem.isNotEmpty) {
      return '$bottomColor $bottomItem';
    }
    return bottom;
  }

  String get formattedShoes {
    if (shoesColor.isNotEmpty && shoesItem.isNotEmpty) {
      return '$shoesColor $shoesItem';
    }
    return shoes;
  }

  String get formattedLayer {
    if (layerItem == null || layerItem!.isEmpty || layerItem!.toLowerCase() == 'none') {
      return '';
    }
    final col = (layerColor != null && layerColor!.isNotEmpty && layerColor!.toLowerCase() != 'none')
        ? '$layerColor '
        : '';
    final mat = (layerMaterial != null && layerMaterial!.isNotEmpty && layerMaterial!.toLowerCase() != 'none')
        ? '  •  $layerMaterial'
        : '';
    return '$col$layerItem$mat';
  }

  String get formattedAccessories {
    if (accessoriesList.isNotEmpty) {
      return accessoriesList.join(' • ');
    }
    return accessories;
  }

  factory OutfitSuggestionModel.fromJson(Map<String, dynamic> json) {
    final resType = json['result_type'] as String?;
    final tType = json['try_on_type'] as String? ?? resType ?? 'actual_try_on';
    final img = (json['try_on_image_url'] ?? json['image_url']) as String?;

    // Parse top detail
    String tItem = '';
    String tColor = '';
    String tMat = '';
    if (json['top_detail'] is Map) {
      final tMap = json['top_detail'] as Map<String, dynamic>;
      tItem = tMap['item']?.toString() ?? '';
      tColor = tMap['color']?.toString() ?? '';
      tMat = tMap['material']?.toString() ?? '';
    }

    // Parse bottom
    String bStr = '';
    String bItem = '';
    String bColor = '';
    String bMat = '';
    if (json['bottom'] is Map) {
      final bMap = json['bottom'] as Map<String, dynamic>;
      bItem = bMap['item']?.toString() ?? '';
      bColor = bMap['color']?.toString() ?? '';
      bMat = bMap['material']?.toString() ?? '';
      bStr = bColor.isNotEmpty ? '$bColor $bItem' : bItem;
    } else if (json['bottom'] != null) {
      bStr = json['bottom'].toString();
      bItem = bStr;
    }

    // Parse shoes
    String sStr = '';
    String sItem = '';
    String sColor = '';
    String sMat = '';
    if (json['shoes'] is Map) {
      final sMap = json['shoes'] as Map<String, dynamic>;
      sItem = sMap['item']?.toString() ?? '';
      sColor = sMap['color']?.toString() ?? '';
      sMat = sMap['material']?.toString() ?? '';
      sStr = sColor.isNotEmpty ? '$sColor $sItem' : sItem;
    } else if (json['shoes'] != null) {
      sStr = json['shoes'].toString();
      sItem = sStr;
    }

    // Parse layer
    String? lItem;
    String? lColor;
    String? lMat;
    if (json['layer'] is Map) {
      final lMap = json['layer'] as Map<String, dynamic>;
      lItem = lMap['item']?.toString();
      lColor = lMap['color']?.toString();
      lMat = lMap['material']?.toString();
    } else if (json['layer'] != null && json['layer'].toString() != 'None') {
      lItem = json['layer'].toString();
    }

    // Parse accessories
    List<String> accList = [];
    String accStr = '';
    if (json['accessories'] is List) {
      accList = (json['accessories'] as List).map((e) => e.toString()).toList();
      accStr = accList.join(', ');
    } else if (json['accessories'] != null) {
      accStr = json['accessories'].toString();
      accList = accStr.isNotEmpty ? [accStr] : [];
    }

    // Parse palette
    List<LookPaletteModel> palList = [];
    if (json['palette'] is List) {
      palList = (json['palette'] as List)
          .map((p) => LookPaletteModel.fromJson(p as Map<String, dynamic>))
          .toList();
    }

    return OutfitSuggestionModel(
      lookId: json['look_id'] as int? ?? 1,
      title: json['title'] as String? ?? 'Outfit',
      style: json['style'] as String? ?? 'Clean casual',
      occasion: json['occasion'] as String? ?? 'Casual',
      top: json['top'] as String? ?? '',
      topItem: tItem,
      topColor: tColor,
      topMaterial: tMat,
      bottom: bStr,
      bottomItem: bItem,
      bottomColor: bColor,
      bottomMaterial: bMat,
      shoes: sStr,
      shoesItem: sItem,
      shoesColor: sColor,
      shoesMaterial: sMat,
      layerItem: lItem,
      layerColor: lColor,
      layerMaterial: lMat,
      accessories: accStr,
      accessoriesList: accList,
      fabricHarmony: json['fabric_harmony'] as String?,
      palette: palList,
      explanation: json['explanation'] as String? ?? '',
      imageUrl: img,
      tryOnImageUrl: img,
      personalizationReason: json['personalization_reason'] as String?,
      tryOnType: tType,
      resultType: resType ?? tType,
      provider: json['provider'] as String? ?? 'fashn_vton_local',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'look_id': lookId,
      'title': title,
      'style': style,
      'occasion': occasion,
      'top': top,
      'bottom': bottomColor.isNotEmpty
          ? {'item': bottomItem, 'color': bottomColor}
          : bottom,
      'shoes': shoesColor.isNotEmpty
          ? {'item': shoesItem, 'color': shoesColor}
          : shoes,
      'accessories': accessoriesList.isNotEmpty ? accessoriesList : accessories,
      'explanation': explanation,
      'image_url': imageUrl,
      'try_on_image_url': tryOnImageUrl ?? imageUrl,
      'personalization_reason': personalizationReason,
      'try_on_type': tryOnType,
      'result_type': resultType,
      'provider': provider,
    };
  }
}

class PersonalizedStyleAnalysisModel {
  final String garmentSummary;
  final String howItWorksWithYou;
  final String? complexionHarmony;
  final String? silhouetteAdvice;
  final int recommendedLooksCount;
  final String tryOnStatus;
  final String? validationMessage;

  PersonalizedStyleAnalysisModel({
    required this.garmentSummary,
    required this.howItWorksWithYou,
    this.complexionHarmony,
    this.silhouetteAdvice,
    this.recommendedLooksCount = 4,
    this.tryOnStatus = 'actual_try_on',
    this.validationMessage,
  });

  bool get isActualTryOn => tryOnStatus == 'actual_try_on';

  bool get isPersonalized =>
      tryOnStatus == 'actual_try_on' ||
      tryOnStatus == 'personalized' ||
      tryOnStatus == 'gemini_personalized_try_on';

  factory PersonalizedStyleAnalysisModel.fromJson(Map<String, dynamic> json) {
    return PersonalizedStyleAnalysisModel(
      garmentSummary: json['garment_summary'] as String? ?? '',
      howItWorksWithYou: json['how_it_works_with_you'] as String? ?? '',
      complexionHarmony: json['complexion_harmony'] as String?,
      silhouetteAdvice: json['silhouette_advice'] as String?,
      recommendedLooksCount: json['recommended_looks_count'] as int? ?? 4,
      tryOnStatus: json['try_on_status'] as String? ?? 'actual_try_on',
      validationMessage: json['validation_message'] as String?,
    );
  }


  Map<String, dynamic> toJson() {
    return {
      'garment_summary': garmentSummary,
      'how_it_works_with_you': howItWorksWithYou,
      'complexion_harmony': complexionHarmony,
      'silhouette_advice': silhouetteAdvice,
      'recommended_looks_count': recommendedLooksCount,
      'try_on_status': tryOnStatus,
      'validation_message': validationMessage,
    };
  }
}

class AnalysisResultModel {
  final String clothingType;
  final String detectedColour;
  final String colourShade;
  final String hexValue;
  final String rgbValue;
  final double confidence;
  final bool isLowConfidence;
  final String clothingImageUrl;
  final String? userImageUrl;
  final List<ColourSwatchModel> recommendedColours;
  final List<OutfitSuggestionModel> outfitSuggestions;
  final String overallAdvice;
  final PersonalizedStyleAnalysisModel? personalizedAnalysis;
  final bool tryOnAvailable;

  AnalysisResultModel({
    required this.clothingType,
    required this.detectedColour,
    required this.colourShade,
    required this.hexValue,
    required this.rgbValue,
    required this.confidence,
    required this.isLowConfidence,
    required this.clothingImageUrl,
    this.userImageUrl,
    required this.recommendedColours,
    required this.outfitSuggestions,
    required this.overallAdvice,
    this.personalizedAnalysis,
    this.tryOnAvailable = true,
  });

  Color toFlutterColor() {
    try {
      final cleanHex = hexValue.replaceAll('#', '');
      return Color(int.parse('FF$cleanHex', radix: 16));
    } catch (_) {
      return Colors.blue;
    }
  }

  factory AnalysisResultModel.fromJson(Map<String, dynamic> json) {
    var rawSwatches = json['recommended_colours'] as List? ?? [];
    List<ColourSwatchModel> swatches =
        rawSwatches.map((s) => ColourSwatchModel.fromJson(s as Map<String, dynamic>)).toList();

    var rawOutfits = json['outfit_suggestions'] as List? ?? [];
    List<OutfitSuggestionModel> outfits =
        rawOutfits.map((o) => OutfitSuggestionModel.fromJson(o as Map<String, dynamic>)).toList();

    PersonalizedStyleAnalysisModel? persAnalysis;
    if (json['personalized_analysis'] != null && json['personalized_analysis'] is Map<String, dynamic>) {
      persAnalysis = PersonalizedStyleAnalysisModel.fromJson(json['personalized_analysis'] as Map<String, dynamic>);
    }

    return AnalysisResultModel(
      clothingType: json['clothing_type'] as String? ?? 'Garment',
      detectedColour: json['detected_colour'] as String? ?? 'Unknown',
      colourShade: json['colour_shade'] as String? ?? 'Unknown Shade',
      hexValue: json['hex_value'] as String? ?? '#000000',
      rgbValue: json['rgb_value'] as String? ?? '0, 0, 0',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      isLowConfidence: json['is_low_confidence'] as bool? ?? false,
      clothingImageUrl: json['clothing_image_url'] as String? ?? '',
      userImageUrl: json['user_image_url'] as String?,
      recommendedColours: swatches,
      outfitSuggestions: outfits,
      overallAdvice: json['overall_advice'] as String? ?? '',
      personalizedAnalysis: persAnalysis,
      tryOnAvailable: json['try_on_available'] as bool? ?? true,
    );
  }
}
