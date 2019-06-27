import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Themes {
  static ThemeData blue() {
    return ThemeData(
      primaryColor: Colors.blue,
      primarySwatch: Colors.blue,
      accentColor: Colors.blue,
      brightness: Brightness.light,
      fontFamily: 'Noto',
    );
  }

  static ThemeData green() {
    return ThemeData(
      primaryColor: Colors.green,
      primarySwatch: Colors.green,
      accentColor: Colors.green,
      brightness: Brightness.light,
      fontFamily: 'Noto',
    );
  }

  static ThemeData orange() {
    return ThemeData(
      primaryColor: Colors.orange,
      primarySwatch: Colors.orange,
      accentColor: Colors.orange,
      brightness: Brightness.dark,
      fontFamily: 'Noto',
    );
  }

  // Save the theme to shared preferences
  static save(theme) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('theme', theme);
  }

  // Load the theme from shared preferences
  static Future<ThemeData> load() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String theme = prefs.getString('theme');

    // If theme exists return it, otherwise return default theme
    switch (theme) {
      case 'blue':
        return blue();
        break;

      case 'green':
        return green();
        break;

      case 'orange':
        return orange();
        break;

      default:
        return blue();
        break;
    }
  }
}
