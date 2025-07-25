import 'package:flutter/material.dart';
import 'package:care_chat/services/api_service.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:io';

class ReviewFeedbackScreen extends StatefulWidget {
  const ReviewFeedbackScreen({Key? key}) : super(key: key);

  @override
  State<ReviewFeedbackScreen> createState() => _ReviewFeedbackScreenState();
}

class _ReviewFeedbackScreenState extends State<ReviewFeedbackScreen>
    with TickerProviderStateMixin {
  int _selectedRating = 3; // 3 stars selected by default
  int _selectedIndex = 0;
  final TextEditingController _feedbackController = TextEditingController();
  bool _allowFollowUp = true;
  bool _isRecording = false;
  bool _isSubmitting = false;
  String _selectedLanguage = 'English';
  late AnimationController _micAnimationController;
  late Animation<double> _micAnimation;
  
  final ApiService _apiService = ApiService();
  FlutterSoundRecorder? _recorder;
  String? _audioPath;

  @override
  void initState() {
    super.initState();
    _feedbackController.text = "Value";
    
    _micAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _micAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _micAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _initializeAudioRecorder();
  }
  
  void _initializeAudioRecorder() async {
    try {
      print('🎤 Initializing audio recorder...');
      _recorder = FlutterSoundRecorder();
      await _recorder!.openRecorder();
      print('✅ Audio recorder initialized successfully');
    } catch (e) {
      print('❌ Failed to initialize audio recorder: $e');
    }
  }

  @override
  void dispose() {
    _feedbackController.dispose();
    _micAnimationController.dispose();
    _recorder?.closeRecorder();
    super.dispose();
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }
  
  void _toggleRecording() async {
    if (_isRecording) {
      // Stop recording
      try {
        print('🛑 Stopping recording...');
        _audioPath = await _recorder!.stopRecorder();
        _micAnimationController.stop();
        _micAnimationController.reset();
        print('✅ Recording stopped successfully');
        print('📁 Audio file saved at: $_audioPath');
        
        // Check if file exists
        if (_audioPath != null && File(_audioPath!).existsSync()) {
          final fileSize = await File(_audioPath!).length();
          print('📊 Audio file size: $fileSize bytes');
        } else {
          print('❌ Audio file not found or empty');
        }
      } catch (e) {
        print('❌ Error stopping recording: $e');
        _audioPath = null;
      }
    } else {
      // Check microphone permission first
      print('🔐 Checking microphone permission...');
      final permission = await Permission.microphone.request();
      
      if (permission != PermissionStatus.granted) {
        print('❌ Microphone permission denied');
        _showErrorDialog('Microphone permission is required for voice feedback. Please enable it in your device settings.');
        return;
      }
      
      print('✅ Microphone permission granted');
      
      // Start recording
      try {
        print('🎤 Starting recording...');
        await _recorder!.startRecorder(
          toFile: 'audio_feedback.wav',
        );
        _micAnimationController.repeat(reverse: true);
        print('✅ Recording started successfully');
      } catch (e) {
        print('❌ Error starting recording: $e');
        _showErrorDialog('Failed to start recording. Please check your microphone permissions.');
        return;
      }
    }
    
    setState(() {
      _isRecording = !_isRecording;
    });
  }
  
  void _submitFeedback() async {
    if (_isSubmitting) return;
    
    setState(() {
      _isSubmitting = true;
    });
    
    try {
      final patientId = await _apiService.getPatientId();
      
      if (patientId == null) {
        _showErrorDialog('Please login again to submit feedback.');
        return;
      }
      
      Map<String, dynamic> result;
      
      // Check if we have audio recording
      if (_audioPath != null && File(_audioPath!).existsSync()) {
        print('📤 Submitting audio feedback...');
        result = await _apiService.createAudioFeedback(
          patientId: patientId,
          rating: _selectedRating,
          language: _selectedLanguage,
          audioFile: File(_audioPath!),
        );
      } else {
        print('📤 Submitting text feedback...');
        result = await _apiService.createFeedback(
          patientId: patientId,
          rating: _selectedRating,
          feedbackText: _feedbackController.text,
          language: _selectedLanguage,
        );
      }
      
      if (result['success'] == true) {
        _showSuccessDialog('Thank you for your feedback!');
      } else {
        _showErrorDialog(result['message'] ?? 'Failed to submit feedback.');
      }
      
    } catch (e) {
      print('💥 Error submitting feedback: $e');
      _showErrorDialog('An error occurred while submitting your feedback.');
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }
  
  void _showSuccessDialog(String message) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Success'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                Navigator.of(context).pop(); // Go back to previous screen
              },
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }
  
  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Error'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildStarRating() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(5, (index) {
        return GestureDetector(
          onTap: () {
            setState(() {
              _selectedRating = index + 1;
            });
          },
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 4),
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: index < _selectedRating 
                  ? const Color(0xFFFF4500)
                  : const Color(0xFFE0E0E0),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.star,
              color: Colors.white,
              size: 24,
            ),
          ),
        );
      }),
    );
  }

  Widget _buildEmojiCard() {
    // Different emoji based on rating
    String emoji;
    if (_selectedRating <= 2) {
      emoji = "😞"; // Sad face for 1-2 stars
    } else if (_selectedRating == 3) {
      emoji = "😐"; // Neutral face for 3 stars
    } else {
      emoji = "😊"; // Happy face for 4-5 stars
    }

    return Container(
      width: double.infinity,
      height: 200,
      margin: const EdgeInsets.symmetric(vertical: 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Center(
        child: Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.black,
              width: 3,
            ),
          ),
          child: Center(
            child: Text(
              emoji,
              style: const TextStyle(fontSize: 40),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F0F5),
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Close Button
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
                        Icons.close,
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
                child: Column(
                  children: [
                    const SizedBox(height: 20),
                    
                    // Title
                    const Text(
                      'Review',
                      style: TextStyle(
                        fontSize: 36,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF2E5BBA),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Subtitle
                    const Text(
                      'How Would You Rate Your Experience?',
                      style: TextStyle(
                        fontSize: 16,
                        color: Color(0xFF424242),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    
                    const SizedBox(height: 32),
                    
                    // Star Rating
                    _buildStarRating(),
                    
                    // Emoji Card
                    _buildEmojiCard(),
                    
                    // Feedback Question
                    const Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        'We\'d Love To Know The Reason For Your Rating?',
                        style: TextStyle(
                          fontSize: 16,
                          color: Color(0xFF424242),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Feedback Text Field
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.05),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: TextField(
                        controller: _feedbackController,
                        maxLines: 4,
                        decoration: const InputDecoration(
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.all(16),
                          hintText: 'Share your thoughts...',
                          hintStyle: TextStyle(
                            color: Color(0xFF9E9E9E),
                            fontSize: 16,
                          ),
                        ),
                        style: const TextStyle(
                          fontSize: 16,
                          color: Color(0xFF424242),
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 32),
                    
                    // Voice Feedback Question
                    const Text(
                      'Do Prefer Submitting Vocal Feedback?',
                      style: TextStyle(
                        fontSize: 16,
                        color: Color(0xFF424242),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Voice Recording Button
                    GestureDetector(
                      onTap: _toggleRecording,
                      child: AnimatedBuilder(
                        animation: _micAnimation,
                        builder: (context, child) {
                          return Transform.scale(
                            scale: _isRecording ? _micAnimation.value : 1.0,
                            child: Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                color: _isRecording 
                                    ? const Color(0xFFFF4500) 
                                    : const Color(0xFF2E5BBA),
                                shape: BoxShape.circle,
                                boxShadow: _isRecording ? [
                                  BoxShadow(
                                    color: const Color(0xFF2E5BBA).withOpacity(0.3),
                                    blurRadius: 20,
                                    spreadRadius: 5,
                                  ),
                                ] : [],
                              ),
                              child: const Icon(
                                Icons.mic,
                                color: Colors.white,
                                size: 32,
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                    
                    const SizedBox(height: 32),
                    
                    // Follow Up Checkbox
                    Row(
                      children: [
                        GestureDetector(
                          onTap: () {
                            setState(() {
                              _allowFollowUp = !_allowFollowUp;
                            });
                          },
                          child: Container(
                            width: 24,
                            height: 24,
                            decoration: BoxDecoration(
                              color: _allowFollowUp 
                                  ? const Color(0xFF2E5BBA) 
                                  : Colors.transparent,
                              border: Border.all(
                                color: const Color(0xFF2E5BBA),
                                width: 2,
                              ),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: _allowFollowUp
                                ? const Icon(
                                    Icons.check,
                                    color: Colors.white,
                                    size: 16,
                                  )
                                : null,
                          ),
                        ),
                        const SizedBox(width: 12),
                        const Text(
                          'May we follow you up on your feedback?',
                          style: TextStyle(
                            fontSize: 16,
                            color: Color(0xFF424242),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 40),
                    
                    // Submit Button
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: _isSubmitting ? null : _submitFeedback,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2E5BBA),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(28),
                          ),
                          elevation: 0,
                        ),
                        child: _isSubmitting
                            ? const SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  color: Colors.white,
                                  strokeWidth: 2.5,
                                ),
                              )
                            : const Text(
                                'Submit Feedback',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                      ),
                    ),
                    
                    const SizedBox(height: 40),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF1E3A8A),
              Color(0xFF1E40AF),
            ],
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _selectedIndex,
          onTap: _onItemTapped,
          backgroundColor: Colors.transparent,
          elevation: 0,
          type: BottomNavigationBarType.fixed,
          selectedItemColor: Colors.white,
          unselectedItemColor: Colors.white70,
          showSelectedLabels: false,
          showUnselectedLabels: false,
          items: [
            BottomNavigationBarItem(
              icon: Stack(
                children: [
                  const Icon(Icons.home_outlined, size: 24),
                  if (_selectedIndex == 0)
                    Positioned(
                      bottom: -8,
                      left: 0,
                      right: 0,
                      child: Container(
                        height: 4,
                        width: 4,
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                ],
              ),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Stack(
                children: [
                  const Icon(Icons.access_time_outlined, size: 24),
                  if (_selectedIndex == 1)
                    Positioned(
                      bottom: -8,
                      left: 0,
                      right: 0,
                      child: Container(
                        height: 4,
                        width: 4,
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                ],
              ),
              label: 'Time',
            ),
            BottomNavigationBarItem(
              icon: Stack(
                children: [
                  const Icon(Icons.person_outline, size: 24),
                  if (_selectedIndex == 2)
                    Positioned(
                      bottom: -8,
                      left: 0,
                      right: 0,
                      child: Container(
                        height: 4,
                        width: 4,
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                ],
              ),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}