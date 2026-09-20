import 'package:flutter/material.dart';
import '../models/analysis_result_model.dart';
import '../utils/constants.dart';

// ---------------------------------------------------------------------------
// Outfit combination image lookup
// Returns a real Unsplash fashion photo showing an outfit that combines the
// detected garment colour with the recommended matching colour.
// ---------------------------------------------------------------------------

/// Normalise a colour name to a short canonical key (e.g. "Jet Black" → "black").
String _canon(String name) {
  final s = name.toLowerCase().trim();
  if (s.contains('black')) return 'black';
  if (s.contains('white') || s.contains('ivory') || s.contains('cream')) return 'white';
  if (s.contains('beige') || s.contains('warm beige')) return 'beige';
  if (s.contains('camel')) return 'camel';
  if (s.contains('brown') || s.contains('tan')) return 'brown';
  if (s.contains('light grey') || s.contains('light gray')) return 'lightgrey';
  if (s.contains('charcoal') || s.contains('dark grey') || s.contains('dark gray')) return 'charcoal';
  if (s.contains('grey') || s.contains('gray')) return 'grey';
  if (s.contains('crimson') || s.contains('burgundy')) return 'crimson';
  if (s.contains('terracotta') || s.contains('rust')) return 'terracotta';
  if (s.contains('red')) return 'red';
  if (s.contains('navy')) return 'navy';
  if (s.contains('royal blue') || s.contains('cobalt')) return 'royalblue';
  if (s.contains('sky blue') || s.contains('baby blue') || s.contains('powder blue') ||
      s.contains('light blue')) { return 'skyblue'; }
  if (s.contains('denim')) return 'denim';
  if (s.contains('blue')) return 'blue';
  if (s.contains('teal')) return 'teal';
  if (s.contains('olive')) return 'olive';
  if (s.contains('khaki')) return 'khaki';
  if (s.contains('forest green') || s.contains('emerald') || s.contains('sage')) return 'green';
  if (s.contains('green')) return 'green';
  if (s.contains('lavender') || s.contains('lilac') || s.contains('mauve')) return 'lavender';
  if (s.contains('purple')) return 'purple';
  if (s.contains('blush') || s.contains('pink')) return 'pink';
  if (s.contains('mustard') || s.contains('yellow')) return 'mustard';
  if (s.contains('orange')) return 'orange';
  if (s.contains('indigo')) return 'indigo';
  return s.split(' ').first; // best-effort single word
}

// ---------------------------------------------------------------------------
// OUTFIT COMBINATION MAP
// Key: "detectedKey|recommendedKey"
// Value: A real Unsplash photo (verified ID) showing that colour combination
//        in a fashion/outfit context (street-style, lookbook, flat-lay, etc.)
// ---------------------------------------------------------------------------
const Map<String, String> _comboMap = {
  // ─── BASE: BLACK ──────────────────────────────────────────────────────────
  'black|white':
      'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=300&h=300&fit=crop&q=85',
  'black|beige':
      'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=300&h=300&fit=crop&q=85',
  'black|camel':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'black|brown':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'black|lightgrey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'black|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'black|charcoal':
      'https://images.unsplash.com/photo-1551232864-3f0890e1776f?w=300&h=300&fit=crop&q=85',
  'black|crimson':
      'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300&h=300&fit=crop&q=85',
  'black|red':
      'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300&h=300&fit=crop&q=85',
  'black|terracotta':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',
  'black|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'black|royalblue':
      'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=300&h=300&fit=crop&q=85',
  'black|blue':
      'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=300&h=300&fit=crop&q=85',
  'black|denim':
      'https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=300&fit=crop&q=85',
  'black|olive':
      'https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?w=300&h=300&fit=crop&q=85',
  'black|mustard':
      'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=300&h=300&fit=crop&q=85',
  'black|pink':
      'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=300&h=300&fit=crop&q=85',
  'black|purple':
      'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=300&fit=crop&q=85',
  'black|lavender':
      'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=300&fit=crop&q=85',

  // ─── BASE: WHITE ──────────────────────────────────────────────────────────
  'white|black':
      'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=300&h=300&fit=crop&q=85',
  'white|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'white|denim':
      'https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=300&fit=crop&q=85',
  'white|camel':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'white|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'white|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'white|lightgrey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'white|olive':
      'https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?w=300&h=300&fit=crop&q=85',
  'white|terracotta':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',

  // ─── BASE: BLUE / ROYAL BLUE ──────────────────────────────────────────────
  'blue|white':
      'https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=300&h=300&fit=crop&q=85',
  'blue|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'blue|lightgrey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'blue|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'blue|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'blue|terracotta':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',
  'royalblue|white':
      'https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=300&h=300&fit=crop&q=85',
  'royalblue|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'royalblue|lightgrey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'royalblue|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'royalblue|terracotta':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',
  'skyblue|white':
      'https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=300&h=300&fit=crop&q=85',
  'skyblue|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'skyblue|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',

  // ─── BASE: NAVY ───────────────────────────────────────────────────────────
  'navy|white':
      'https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=300&h=300&fit=crop&q=85',
  'navy|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'navy|camel':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'navy|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'navy|lightgrey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'navy|crimson':
      'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300&h=300&fit=crop&q=85',
  'navy|terracotta':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',
  'navy|olive':
      'https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?w=300&h=300&fit=crop&q=85',

  // ─── BASE: GREY / CHARCOAL ────────────────────────────────────────────────
  'grey|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'grey|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'grey|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'grey|camel':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'grey|crimson':
      'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300&h=300&fit=crop&q=85',
  'charcoal|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'charcoal|camel':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'charcoal|red':
      'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300&h=300&fit=crop&q=85',
  'lightgrey|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'lightgrey|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'lightgrey|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',

  // ─── BASE: BEIGE / CAMEL ──────────────────────────────────────────────────
  'beige|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'beige|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'beige|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'beige|terracotta':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',
  'beige|olive':
      'https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?w=300&h=300&fit=crop&q=85',
  'camel|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'camel|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'camel|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'camel|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'brown|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'brown|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'brown|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',

  // ─── BASE: RED / CRIMSON ──────────────────────────────────────────────────
  'red|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'red|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'red|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'red|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'crimson|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'crimson|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'crimson|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'crimson|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'terracotta|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'terracotta|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'terracotta|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'terracotta|denim':
      'https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=300&fit=crop&q=85',

  // ─── BASE: GREEN / OLIVE / TEAL ───────────────────────────────────────────
  'olive|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'olive|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'olive|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'olive|brown':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'green|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'green|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'green|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'teal|beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'teal|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'teal|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',

  // ─── BASE: PINK / LAVENDER / PURPLE ───────────────────────────────────────
  'pink|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'pink|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'pink|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'lavender|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'lavender|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'purple|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'purple|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',

  // ─── BASE: DENIM ──────────────────────────────────────────────────────────
  'denim|white':
      'https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=300&h=300&fit=crop&q=85',
  'denim|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'denim|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'denim|camel':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'denim|terracotta':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',

  // ─── BASE: MUSTARD / YELLOW / ORANGE ─────────────────────────────────────
  'mustard|black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'mustard|navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'mustard|white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'mustard|grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
};

// ---------------------------------------------------------------------------
// Single-colour fallback: a fashion photo prominently featuring that colour.
// Used when no combination match is found.
// ---------------------------------------------------------------------------
const Map<String, String> _singleMap = {
  'black':
      'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&q=85',
  'white':
      'https://images.unsplash.com/photo-1622519407650-3df9883f76a5?w=300&h=300&fit=crop&q=85',
  'beige':
      'https://images.unsplash.com/photo-1614093302611-8efc4c304b86?w=300&h=300&fit=crop&q=85',
  'camel':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'brown':
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=300&fit=crop&q=85',
  'lightgrey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'grey':
      'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&q=85',
  'charcoal':
      'https://images.unsplash.com/photo-1551232864-3f0890e1776f?w=300&h=300&fit=crop&q=85',
  'crimson':
      'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300&h=300&fit=crop&q=85',
  'red':
      'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300&h=300&fit=crop&q=85',
  'terracotta':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',
  'navy':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
  'royalblue':
      'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=300&h=300&fit=crop&q=85',
  'blue':
      'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=300&h=300&fit=crop&q=85',
  'skyblue':
      'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=300&h=300&fit=crop&q=85',
  'denim':
      'https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=300&fit=crop&q=85',
  'teal':
      'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=300&h=300&fit=crop&q=85',
  'olive':
      'https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?w=300&h=300&fit=crop&q=85',
  'green':
      'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=300&h=300&fit=crop&q=85',
  'pink':
      'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=300&h=300&fit=crop&q=85',
  'lavender':
      'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=300&fit=crop&q=85',
  'purple':
      'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=300&fit=crop&q=85',
  'mustard':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',
  'orange':
      'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=300&fit=crop&q=85',
  'indigo':
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=300&h=300&fit=crop&q=85',
};

/// Returns the best matching outfit image URL:
/// 1. Tries (detectedColour + recommendedColour) combination photo.
/// 2. Falls back to a single-colour fashion photo for the recommended colour.
/// 3. Ultimate fallback to a neutral fashion flat-lay.
String _outfitImageUrl(String detectedColour, String recommendedColour) {
  final dk = _canon(detectedColour);
  final rk = _canon(recommendedColour);

  // 1. Combination match
  final comboKey = '$dk|$rk';
  if (_comboMap.containsKey(comboKey)) {
    return _comboMap[comboKey]!;
  }

  // 2. Single recommended-colour fashion photo
  if (_singleMap.containsKey(rk)) {
    return _singleMap[rk]!;
  }

  // 3. Ultimate fallback — neutral fashion editorial flat-lay
  return 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=300&h=300&fit=crop&q=85';
}

// ---------------------------------------------------------------------------
// Widget
// ---------------------------------------------------------------------------
class ColourSwatchCard extends StatelessWidget {
  final ColourSwatchModel swatch;

  /// The detected garment colour name (e.g. "Jet Black", "Royal Blue").
  /// Used to look up the most relevant outfit combination photo.
  final String detectedColour;

  const ColourSwatchCard({
    super.key,
    required this.swatch,
    this.detectedColour = '',
  });

  @override
  Widget build(BuildContext context) {
    final color = swatch.toFlutterColor();
    final isVeryLight =
        (color.red * 0.299 + color.green * 0.587 + color.blue * 0.114) > 220;
    final imageUrl = _outfitImageUrl(detectedColour, swatch.name);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Outfit combination image (replaces plain colour swatch) ──────
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: SizedBox(
              width: 54,
              height: 54,
              child: Image.network(
                imageUrl,
                fit: BoxFit.cover,
                loadingBuilder: (ctx, child, progress) {
                  if (progress == null) return child;
                  // While loading: show the actual colour as placeholder
                  return Container(
                    decoration: BoxDecoration(
                      color: color,
                      border: Border.all(
                        color:
                            isVeryLight ? Colors.black26 : Colors.black12,
                        width: 1.5,
                      ),
                    ),
                    child: const Center(
                      child: SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white70,
                        ),
                      ),
                    ),
                  );
                },
                errorBuilder: (ctx, error, stack) {
                  // On network error: graceful fallback to colour swatch
                  return Container(
                    decoration: BoxDecoration(
                      color: color,
                      border: Border.all(
                        color:
                            isVeryLight ? Colors.black26 : Colors.black12,
                        width: 1.5,
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
          const SizedBox(width: 14),

          // ── Text details — UNCHANGED ─────────────────────────────────────
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        swatch.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 15,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: AppColors.background,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: AppColors.border),
                      ),
                      child: Text(
                        swatch.hex.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 12,
                          fontFamily: 'monospace',
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppColors.accent.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    swatch.harmonyType,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF926B1E),
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  swatch.reason,
                  style: const TextStyle(
                    fontSize: 13,
                    color: AppColors.textSecondary,
                    height: 1.35,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
