import 'package:care_chat/services/api_service.dart';
import 'package:flutter/material.dart';
import 'main_screen.dart';

class CreateAccountScreen extends StatefulWidget {
  const CreateAccountScreen({Key? key}) : super(key: key);

  @override
  State<CreateAccountScreen> createState() => _CreateAccountScreenState();
}

class _CreateAccountScreenState extends State<CreateAccountScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final ApiService _apiService = ApiService();
  bool _isPasswordVisible = false;
  bool _isLoading = false;
  bool _isFullNameFocused = false;
  bool _showDebugConsole = false;
  List<String> _debugLogs = [];

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _addDebugLog(String message) {
    setState(() {
      _debugLogs.add('${DateTime.now().toString().substring(11, 19)}: $message');
      if (_debugLogs.length > 10) {
        _debugLogs.removeAt(0);
      }
    });
  }

  void _createAccount() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
      });

      _addDebugLog('🚀 Starting signup process...');
      _addDebugLog('👤 Name: ${_fullNameController.text}');
      _addDebugLog('📧 Email: ${_emailController.text}');
      _addDebugLog('📱 Phone: ${_phoneController.text}');
      _addDebugLog('🌐 Base URL: https://carechat-dswb-v8ex.onrender.com/api/');
      _addDebugLog('🎯 Endpoint: signup');

      try {
        final fullName = _fullNameController.text.split(' ');
        final firstName = fullName.isNotEmpty ? fullName[0] : '';
        final lastName = fullName.length > 1 ? fullName.sublist(1).join(' ') : '';

        _addDebugLog('📤 Calling API service...');
        final result = await _apiService.signUp(
          firstName: firstName,
          lastName: lastName,
          phoneNumber: _phoneController.text,
          email: _emailController.text,
          password: _passwordController.text,
        );

        _addDebugLog('📥 Response received');
        _addDebugLog('✅ Success: ${result['success']}');

        if (result['success'] == true) {
          _addDebugLog('🎉 Signup successful - navigating...');
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const MainScreen()),
          );
        } else {
          _addDebugLog('❌ Signup failed: ${result['message']}');
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message'] ?? 'Signup failed'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } catch (e) {
        _addDebugLog('💥 Exception: $e');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Network error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      } finally {
        setState(() {
          _isLoading = false;
        });
        _addDebugLog('🏁 Signup process completed');
      }
    }
  }

  String? _validateFullName(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Please enter your full name';
    }
    if (value.trim().length < 2) {
      return 'Full name must be at least 2 characters';
    }
    return null;
  }

  String? _validateEmail(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Please enter your email address';
    }
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value.trim())) {
      return 'Please enter a valid email address';
    }
    return null;
  }

  String? _validatePhone(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Please enter your phone number';
    }
    final phoneRegex = RegExp(r'^[+]?[1-9][\d\s\-\(\)]{7,15}$');
    if (!phoneRegex.hasMatch(value.trim().replaceAll(RegExp(r'[\s\-\(\)]'), ''))) {
      return 'Please enter a valid phone number';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter a password';
    }
    if (value.length < 8) {
      return 'Password must be at least 8 characters';
    }
    if (!RegExp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)').hasMatch(value)) {
      return 'Password must contain uppercase, lowercase, and number';
    }
    return null;
  }

  Widget _buildInputField({
    required TextEditingController controller,
    required String hintText,
    required IconData icon,
    bool isPassword = false,
    bool isFocused = false,
    VoidCallback? onTap,
    Function(String)? onChanged,
    String? Function(String?)? validator,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isFocused ? const Color(0xFF2E5BBA) : const Color(0xFFE0E0E0),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        obscureText: isPassword && !_isPasswordVisible,
        onTap: onTap,
        onChanged: onChanged,
        validator: validator,
        style: const TextStyle(
          color: Color(0xFF2D3748),
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: const TextStyle(
            color: Color(0xFF9CA3AF),
            fontSize: 16,
            fontWeight: FontWeight.w400,
          ),
          prefixIcon: Icon(
            icon,
            color: isFocused ? const Color(0xFF2E5BBA) : const Color(0xFF9CA3AF),
            size: 22,
          ),
          suffixIcon: isPassword
              ? IconButton(
                  icon: Icon(
                    _isPasswordVisible ? Icons.visibility_off : Icons.visibility,
                    color: const Color(0xFF9CA3AF),
                    size: 22,
                  ),
                  onPressed: () {
                    setState(() {
                      _isPasswordVisible = !_isPasswordVisible;
                    });
                  },
                )
              : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 20,
            vertical: 20,
          ),
        ),
      ),
    );
  }

  Widget _buildDebugConsole() {
    return Container(
      height: 200,
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.bug_report, color: Colors.green, size: 16),
              const SizedBox(width: 8),
              const Text(
                'Debug Console',
                style: TextStyle(
                  color: Colors.green,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: () {
                  setState(() {
                    _debugLogs.clear();
                  });
                },
                icon: const Icon(Icons.clear, color: Colors.orange, size: 16),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
            ],
          ),
          const Divider(color: Colors.green, height: 8),
          Expanded(
            child: ListView.builder(
              itemCount: _debugLogs.length,
              itemBuilder: (context, index) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 1),
                  child: Text(
                    _debugLogs[index],
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontFamily: 'monospace',
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Back Button
                  GestureDetector(
                    onTap: () {
                      Navigator.pop(context);
                    },
                    child: Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: const Color(0xFFE0E0E0),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Icon(
                        Icons.arrow_back_ios_new,
                        color: Color(0xFF757575),
                        size: 20,
                      ),
                    ),
                  ),
                  
                  // Language Selector
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.transparent,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      children: const [
                        Icon(
                          Icons.language,
                          color: Color(0xFF757575),
                          size: 20,
                        ),
                        SizedBox(width: 8),
                        Text(
                          'English',
                          style: TextStyle(
                            color: Color(0xFF757575),
                            fontSize: 16,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        SizedBox(width: 4),
                        Icon(
                          Icons.keyboard_arrow_down,
                          color: Color(0xFF757575),
                          size: 20,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 20),
                      
                      // Title
                      const Text(
                        'Create Your\nAccount',
                        style: TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF2E5BBA),
                          height: 1.1,
                        ),
                      ),
                      
                      const SizedBox(height: 40),
                      
                      // Full Name Field
                      _buildInputField(
                        controller: _fullNameController,
                        hintText: 'Full Name',
                        icon: Icons.person_outline,
                        isFocused: _isFullNameFocused,
                        validator: _validateFullName,
                        onTap: () {
                          setState(() {
                            _isFullNameFocused = true;
                          });
                        },
                        onChanged: (value) {
                          if (value.isEmpty) {
                            setState(() {
                              _isFullNameFocused = false;
                            });
                          }
                        },
                      ),
                      
                      // Email Field
                      _buildInputField(
                        controller: _emailController,
                        hintText: 'Email Address',
                        icon: Icons.email_outlined,
                        validator: _validateEmail,
                      ),
                      
                      // Phone Field
                      _buildInputField(
                        controller: _phoneController,
                        hintText: 'Enter your phone number',
                        icon: Icons.phone_outlined,
                        validator: _validatePhone,
                      ),
                      
                      // Password Field
                      _buildInputField(
                        controller: _passwordController,
                        hintText: 'Password',
                        icon: Icons.lock_outline,
                        isPassword: true,
                        validator: _validatePassword,
                      ),
                      
                      // Password Requirements
                      Container(
                        margin: const EdgeInsets.only(bottom: 20),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF0F9FF),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFFBFDBFE)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Password must contain:',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF1E40AF),
                              ),
                            ),
                            const SizedBox(height: 4),
                            const Text(
                              '• At least 8 characters\n• One uppercase letter\n• One lowercase letter\n• One number',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF3B82F6),
                                height: 1.3,
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // Register Button
                      Container(
                        width: double.infinity,
                        height: 56,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(16),
                          gradient: const LinearGradient(
                            colors: [
                              Color(0xFF2E5BBA),
                              Color(0xFF1E40AF),
                            ],
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF2E5BBA).withOpacity(0.3),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: ElevatedButton(
                          onPressed: _isLoading ? null : _createAccount,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.transparent,
                            shadowColor: Colors.transparent,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  width: 24,
                                  height: 24,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2.5,
                                  ),
                                )
                              : const Text(
                                  'Create Account',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.white,
                                    letterSpacing: 0.5,
                                  ),
                                ),
                        ),
                      ),
                      
                      const SizedBox(height: 40),
                      
                      // Sign In Link
                      Center(
                        child: GestureDetector(
                          onTap: () {
                            // Navigate to sign in
                            Navigator.pop(context);
                          },
                          child: const Text(
                            'Already Have An Account? Sign In',
                            style: TextStyle(
                              fontSize: 16,
                              color: Color(0xFF757575),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // Or Login With
                      const Center(
                        child: Text(
                          'Or continue with',
                          style: TextStyle(
                            fontSize: 16,
                            color: Color(0xFF6B7280),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Google Sign In Button
                      Container(
                        width: double.infinity,
                        height: 56,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: const Color(0xFFE5E7EB),
                            width: 1.5,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.05),
                              blurRadius: 10,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: ElevatedButton(
                          onPressed: () {
                            // Handle Google sign in
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.transparent,
                            shadowColor: Colors.transparent,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: const [
                              Icon(
                                Icons.g_mobiledata,
                                color: Color(0xFF4285F4),
                                size: 28,
                              ),
                              SizedBox(width: 12),
                              Text(
                                'Continue with Google',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF374151),
                                  letterSpacing: 0.25,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 40),
                      
                      // Debug Console Toggle
                      GestureDetector(
                        onDoubleTap: () {
                          setState(() {
                            _showDebugConsole = !_showDebugConsole;
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.developer_mode,
                                size: 16,
                                color: _showDebugConsole ? Colors.green : Colors.grey,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                'Debug Mode ${_showDebugConsole ? 'ON' : 'OFF'} (Double tap to toggle)',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: _showDebugConsole ? Colors.green : Colors.grey,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      
                      // Debug Console
                      if (_showDebugConsole) _buildDebugConsole(),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}