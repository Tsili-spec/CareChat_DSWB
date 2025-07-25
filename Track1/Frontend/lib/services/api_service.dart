import 'dart:convert';
import 'dart:developer' as developer;
import 'dart:io';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'api_endpoints.dart';

class ApiService {
  final _storage = const FlutterSecureStorage();
  
  void _logRequest(String method, String url, {Map<String, dynamic>? body, Map<String, String>? headers}) {
    print('🚀 API REQUEST: $method $url');
    developer.log('🚀 API REQUEST', name: 'ApiService');
    developer.log('Method: $method', name: 'ApiService');
    developer.log('URL: $url', name: 'ApiService');
    
    if (headers != null) {
      print('Headers: ${json.encode(headers)}');
      developer.log('Headers: ${json.encode(headers)}', name: 'ApiService');
    }
    
    if (body != null) {
      print('Body: ${json.encode(body)}');
      developer.log('Body: ${json.encode(body)}', name: 'ApiService');
    }
  }
  
  void _logResponse(http.Response response) {
    print('📥 API RESPONSE: ${response.statusCode}');
    print('Response Body: ${response.body}');
    developer.log('📥 API RESPONSE', name: 'ApiService');
    developer.log('Status Code: ${response.statusCode}', name: 'ApiService');
    developer.log('Headers: ${response.headers}', name: 'ApiService');
    developer.log('Body: ${response.body}', name: 'ApiService');
    
    if (response.statusCode >= 400) {
      print('⚠️ API ERROR RESPONSE');
      developer.log('⚠️ API ERROR RESPONSE', name: 'ApiService');
    }
  }
  
  void _logError(String operation, dynamic error) {
    print('❌ API ERROR in $operation: $error');
    developer.log('❌ API ERROR in $operation', name: 'ApiService');
    developer.log('Error: $error', name: 'ApiService');
  }

  Future<void> _saveToken(String token) async {
    await _storage.write(key: 'access_token', value: token);
  }

  Future<void> _saveRefreshToken(String refreshToken) async {
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<void> _savePatientInfo(Map<String, dynamic> patient) async {
    await _storage.write(key: 'patient_id', value: patient['patient_id']);
    await _storage.write(key: 'first_name', value: patient['first_name']);
    await _storage.write(key: 'last_name', value: patient['last_name']);
    await _storage.write(key: 'email', value: patient['email']);
    await _storage.write(key: 'phone_number', value: patient['phone_number']);
    await _storage.write(key: 'preferred_language', value: patient['preferred_language']);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: 'access_token');
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: 'refresh_token');
  }

  Future<String?> getPatientId() async {
    return await _storage.read(key: 'patient_id');
  }

  Future<Map<String, String?>> getPatientInfo() async {
    return {
      'patient_id': await _storage.read(key: 'patient_id'),
      'first_name': await _storage.read(key: 'first_name'),
      'last_name': await _storage.read(key: 'last_name'),
      'email': await _storage.read(key: 'email'),
      'phone_number': await _storage.read(key: 'phone_number'),
      'preferred_language': await _storage.read(key: 'preferred_language'),
    };
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final token = await getToken();
      
      if (token == null) {
        return {
          'success': false,
          'message': 'User not authenticated. Please login again.',
        };
      }

      final url = Uri.parse('${ApiEndPoints.baseUrl}me');
      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };
      
      _logRequest('GET', url.toString(), headers: headers);
      
      final response = await http.get(
        url,
        headers: headers,
      );

      _logResponse(response);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'user': data};
      } else {
        final data = json.decode(response.body);
        return {
          'success': false,
          'message': data['message'] ?? data['detail'] ?? 'Failed to fetch user profile',
          'statusCode': response.statusCode,
        };
      }
    } catch (e) {
      _logError('getCurrentUser', e);
      return {
        'success': false,
        'message': 'Network error. Please check your connection and try again.',
        'error': e.toString(),
      };
    }
  }

  Future<void> clearUserData() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    await _storage.delete(key: 'patient_id');
    await _storage.delete(key: 'first_name');
    await _storage.delete(key: 'last_name');
    await _storage.delete(key: 'email');
    await _storage.delete(key: 'phone_number');
    await _storage.delete(key: 'preferred_language');
  }

  Future<Map<String, dynamic>> signUp({
    required String firstName,
    required String lastName,
    required String phoneNumber,
    required String email,
    required String password,
    String preferredLanguage = 'English',
  }) async {
    try {
      final url = Uri.parse(ApiEndPoints.baseUrl + ApiEndPoints.signup);
      final requestBody = {
        'first_name': firstName,
        'last_name': lastName,
        'phone_number': phoneNumber,
        'email': email,
        'preferred_language': preferredLanguage,
        'password': password,
      };
      final headers = {'Content-Type': 'application/json'};
      
      _logRequest('POST', url.toString(), body: requestBody, headers: headers);
      
      final response = await http.post(
        url,
        headers: headers,
        body: json.encode(requestBody),
      );

      _logResponse(response);
      final data = json.decode(response.body);
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        if (data['token'] != null) {
          await _saveToken(data['token']);
        }
        return {'success': true, ...data};
      } else {
        return {
          'success': false,
          'message': data['message'] ?? data['error'] ?? 'Registration failed',
          'statusCode': response.statusCode,
        };
      }
    } catch (e) {
      _logError('signUp', e);
      return {
        'success': false,
        'message': 'Network error. Please check your connection and try again.',
        'error': e.toString(),
      };
    }
  }

  Future<Map<String, dynamic>> login({
    required String mobileNumber,
    required String password,
  }) async {
    print('🚀 ApiService.login() method called');
    print('Mobile Number: $mobileNumber');
    developer.log('ApiService.login() method called', name: 'ApiService');
    try {
      final url = Uri.parse(ApiEndPoints.baseUrl + ApiEndPoints.login);
      final requestBody = {
        'phone_number': mobileNumber,
        'password': password,
      };
      final headers = {'Content-Type': 'application/json'};
      
      _logRequest('POST', url.toString(), body: requestBody, headers: headers);
      
      final response = await http.post(
        url,
        headers: headers,
        body: json.encode(requestBody),
      );
      
      _logResponse(response);
      final data = json.decode(response.body);
      
      if (response.statusCode == 200) {
        // Save access token
        if (data['access_token'] != null) {
          await _saveToken(data['access_token']);
        }
        
        // Save refresh token
        if (data['refresh_token'] != null) {
          await _saveRefreshToken(data['refresh_token']);
        }
        
        // Save patient information
        if (data['patient'] != null) {
          await _savePatientInfo(data['patient']);
        }
        
        return {'success': true, ...data};
      } else {
        return {
          'success': false,
          'message': data['message'] ?? data['error'] ?? 'Login failed',
          'statusCode': response.statusCode,
        };
      }
    } catch (e) {
      _logError('login', e);
      return {
        'success': false,
        'message': 'Network error. Please check your connection and try again.',
        'error': e.toString(),
      };
    }
  }

  Future<Map<String, dynamic>> createReminder({
    required String title,
    required String message,
    required List<String> days,
    required List<DateTime> scheduledTime,
    String status = 'active',
    String? type,
  }) async {
    print('🏥 ApiService.createReminder() method called');
    print('Title: $title');
    print('Message: $message');
    print('Days: $days');
    print('Scheduled Times: $scheduledTime');
    print('Status: $status');
    print('Type: $type');
    
    try {
      final token = await getToken();
      final patientId = await getPatientId();
      
      print('🔑 Token retrieved: ${token != null ? 'Yes' : 'No'}');
      print('👤 Patient ID: $patientId');
      
      if (token == null || patientId == null) {
        print('❌ Authentication failed - missing token or patient ID');
        return {
          'success': false,
          'message': 'User not authenticated. Please login again.',
        };
      }

      final url = Uri.parse(ApiEndPoints.baseUrl + ApiEndPoints.createReminder);
      final requestBody = {
        'patient_id': patientId,
        'title': title,
        'message': message,
        'days': days,
        'scheduled_time': scheduledTime.map((time) => time.toIso8601String()).toList(),
        'status': status,
      };
      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };
      
      _logRequest('POST', url.toString(), body: requestBody, headers: headers);
      
      final response = await http.post(
        url,
        headers: headers,
        body: json.encode(requestBody),
      );

      _logResponse(response);
      final data = json.decode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, ...data};
      } else {
        return {
          'success': false,
          'message': data['message'] ?? data['error'] ?? 'Failed to create reminder',
          'statusCode': response.statusCode,
        };
      }
    } catch (e) {
      _logError('createReminder', e);
      return {
        'success': false,
        'message': 'Network error. Please check your connection and try again.',
        'error': e.toString(),
      };
    }
  }

  Future<Map<String, dynamic>> getUserReminders() async {
    try {
      final token = await getToken();
      final patientId = await getPatientId();
      
      if (token == null || patientId == null) {
        return {
          'success': false,
          'message': 'User not authenticated. Please login again.',
        };
      }

      final url = Uri.parse('${ApiEndPoints.baseUrl}${ApiEndPoints.getReminders}$patientId');
      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };
      
      _logRequest('GET', url.toString(), headers: headers);
      
      final response = await http.get(
        url,
        headers: headers,
      );

      _logResponse(response);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'reminders': data};
      } else {
        final data = json.decode(response.body);
        return {
          'success': false,
          'message': data['message'] ?? data['detail'] ?? 'Failed to fetch reminders',
          'statusCode': response.statusCode,
        };
      }
    } catch (e) {
      _logError('getUserReminders', e);
      return {
        'success': false,
        'message': 'Network error. Please check your connection and try again.',
        'error': e.toString(),
      };
    }
  }

  Future<Map<String, dynamic>> createFeedback({
    required String patientId,
    required int rating,
    required String feedbackText,
    required String language,
  }) async {
    print('🗣️ ApiService.createFeedback() method called');
    print('Patient ID: $patientId');
    print('Rating: $rating');
    print('Language: $language');
    developer.log('ApiService.createFeedback() method called', name: 'ApiService');
    
    try {
      final token = await getToken();
      
      if (token == null) {
        return {
          'success': false,
          'message': 'User not authenticated. Please login again.',
        };
      }

      final url = Uri.parse(ApiEndPoints.baseUrl + ApiEndPoints.createFeedback);
      final requestBody = {
        'patient_id': patientId,
        'rating': rating.toString(),
        'feedback_text': feedbackText,
        'language': language,
      };
      final headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer $token',
      };
      
      _logRequest('POST', url.toString(), body: requestBody, headers: headers);
      
      final response = await http.post(
        url,
        headers: headers,
        body: requestBody,
      );

      _logResponse(response);
      final data = json.decode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, ...data};
      } else {
        return {
          'success': false,
          'message': data['message'] ?? data['error'] ?? 'Failed to create feedback',
          'statusCode': response.statusCode,
        };
      }
    } catch (e) {
      _logError('createFeedback', e);
      return {
        'success': false,
        'message': 'Network error. Please check your connection and try again.',
        'error': e.toString(),
      };
    }
  }

  Future<Map<String, dynamic>> createAudioFeedback({
    required String patientId,
    required int rating,
    required String language,
    required File audioFile,
  }) async {
    print('🎤 ApiService.createAudioFeedback() method called');
    print('Patient ID: $patientId');
    print('Rating: $rating');
    print('Language: $language');
    print('Audio file path: ${audioFile.path}');
    developer.log('ApiService.createAudioFeedback() method called', name: 'ApiService');
    
    try {
      final token = await getToken();
      
      if (token == null) {
        return {
          'success': false,
          'message': 'User not authenticated. Please login again.',
        };
      }

      final url = Uri.parse(ApiEndPoints.baseUrl + ApiEndPoints.createAudioFeedback);
      
      print('🚀 MULTIPART REQUEST: POST $url');
      developer.log('🚀 MULTIPART REQUEST: POST $url', name: 'ApiService');
      
      var request = http.MultipartRequest('POST', url);
      
      // Add headers
      request.headers['Authorization'] = 'Bearer $token';
      
      // Add form fields
      request.fields['patient_id'] = patientId;
      request.fields['rating'] = rating.toString();
      request.fields['language'] = language;
      
      // Add audio file
      var audioMultipart = await http.MultipartFile.fromPath(
        'audio',
        audioFile.path,
        filename: 'audio_feedback.wav',
      );
      request.files.add(audioMultipart);
      
      print('📤 Sending multipart request...');
      developer.log('📤 Sending multipart request...', name: 'ApiService');
      
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      _logResponse(response);
      final data = json.decode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, ...data};
      } else {
        return {
          'success': false,
          'message': data['message'] ?? data['error'] ?? 'Failed to create audio feedback',
          'statusCode': response.statusCode,
        };
      }
    } catch (e) {
      _logError('createAudioFeedback', e);
      return {
        'success': false,
        'message': 'Network error. Please check your connection and try again.',
        'error': e.toString(),
      };
    }
  }
} 