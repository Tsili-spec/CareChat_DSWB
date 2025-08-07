import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final _storage = const FlutterSecureStorage();

  Future<bool> isAuthenticated() async {
    final token = await _storage.read(key: 'access_token');
    return token != null && token.isNotEmpty;
  }

  Future<String?> getToken() async {
    return await _storage.read(key: 'access_token');
  }

  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    await _storage.delete(key: 'patient_id');
    await _storage.delete(key: 'first_name');
    await _storage.delete(key: 'last_name');
    await _storage.delete(key: 'email');
    await _storage.delete(key: 'phone_number');
    await _storage.delete(key: 'preferred_language');
  }

  static void handleAuthError(BuildContext context) {
    AuthService().logout();
    Navigator.of(context).pushNamedAndRemoveUntil(
      '/login',
      (route) => false,
    );
  }
}