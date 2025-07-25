import 'package:care_chat/models/reminder_model.dart';
import 'package:care_chat/services/reminder_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class CreateReminderScreen extends StatefulWidget {
  final ReminderService reminderService;

  const CreateReminderScreen({Key? key, required this.reminderService}) : super(key: key);

  @override
  _CreateReminderScreenState createState() => _CreateReminderScreenState();
}

class _CreateReminderScreenState extends State<CreateReminderScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _messageController = TextEditingController();
  List<TimeOfDay> _selectedTimes = [TimeOfDay.now()];
  List<String> _selectedDays = [];
  bool _isActive = true;
  bool _isLoading = false;

  final List<String> _daysOfWeek = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
  ];

  final List<String> _dayAbbreviations = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  @override
  void dispose() {
    _titleController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _selectTime(BuildContext context, int index) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _selectedTimes[index],
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: Color(0xFF2E5BBA),
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null && picked != _selectedTimes[index]) {
      setState(() {
        _selectedTimes[index] = picked;
      });
    }
  }

  void _addTime() {
    if (_selectedTimes.length < 5) {
      setState(() {
        _selectedTimes.add(TimeOfDay.now());
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Maximum 5 times allowed'),
          backgroundColor: Colors.orange,
        ),
      );
    }
  }

  void _removeTime(int index) {
    if (_selectedTimes.length > 1) {
      setState(() {
        _selectedTimes.removeAt(index);
      });
    }
  }

  void _createReminder() async {
    print('📝 _createReminder() called');
    
    if (_formKey.currentState!.validate()) {
      print('✅ Form validation passed');
      
      if (_selectedDays.isEmpty) {
        print('❌ No days selected');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please select at least one day'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      print('✅ Days selected: ${_selectedDays.join(', ')}');
      print('✅ Times selected: ${_selectedTimes.map((t) => t.format(context)).join(', ')}');

      setState(() {
        _isLoading = true;
      });

      // Get patient_id from secure storage
      final storage = const FlutterSecureStorage();
      final patientId = await storage.read(key: 'patient_id');
      
      print('👤 Patient ID from storage: $patientId');
      
      if (patientId == null) {
        setState(() {
          _isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('User not authenticated. Please login again.'),
            backgroundColor: Colors.red,
          ),
        );
        return;
      }

      final now = DateTime.now();
      final scheduledTimes = _selectedTimes.map((time) {
        return DateTime(now.year, now.month, now.day, time.hour, time.minute);
      }).toList();

      print('📅 Scheduled times: ${scheduledTimes.map((t) => t.toIso8601String()).join(', ')}');

      final newReminder = Reminder(
        title: _titleController.text,
        message: _messageController.text,
        patientId: patientId,
        days: _selectedDays,
        scheduledTime: scheduledTimes,
        status: _isActive ? 'active' : 'inactive',
      );

      print('🎯 Creating reminder with data:');
      print('  Title: ${newReminder.title}');
      print('  Message: ${newReminder.message}');
      print('  Patient ID: ${newReminder.patientId}');
      print('  Days: ${newReminder.days}');
      print('  Scheduled Times: ${newReminder.scheduledTime}');
      print('  Status: ${newReminder.status}');

      final result = await widget.reminderService.createReminder(newReminder);

      print('📥 Reminder creation result: $result');

      setState(() {
        _isLoading = false;
      });

      if (result['success'] == true) {
        print('✅ Reminder created successfully');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Reminder created successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context);
      } else {
        print('❌ Failed to create reminder: ${result['message']}');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['message'] ?? 'Failed to create reminder'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } else {
      print('❌ Form validation failed');
    }
  }

  Widget _buildSectionCard({required String title, required Widget child, required IconData icon}) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 20),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2E5BBA).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: const Color(0xFF2E5BBA), size: 20),
                ),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2E5BBA),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }

  Widget _buildTimeCard(int index, TimeOfDay time) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FF),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2E5BBA).withOpacity(0.2)),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFF2E5BBA).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(Icons.access_time, color: Color(0xFF2E5BBA), size: 18),
        ),
        title: Text(
          'Time ${index + 1}',
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0xFF2E5BBA),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                time.format(context),
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            if (_selectedTimes.length > 1) ...[
              const SizedBox(width: 8),
              IconButton(
                onPressed: () => _removeTime(index),
                icon: const Icon(Icons.delete_outline, color: Colors.red, size: 20),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
            ],
          ],
        ),
        onTap: () => _selectTime(context, index),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: const Color(0xFF2E5BBA),
        title: const Text(
          'Create Reminder',
          style: TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 20,
          ),
        ),
        centerTitle: true,
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              // Basic Information
              _buildSectionCard(
                title: 'Basic Information',
                icon: Icons.info_outline,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _titleController,
                      decoration: InputDecoration(
                        labelText: 'Reminder Title',
                        hintText: 'e.g., Take morning medication',
                        prefixIcon: const Icon(Icons.title),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey.shade300),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFF2E5BBA)),
                        ),
                      ),
                      validator: (value) => value!.isEmpty ? 'Please enter a title' : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _messageController,
                      maxLines: 3,
                      decoration: InputDecoration(
                        labelText: 'Message',
                        hintText: 'e.g., Take 1 tablet with water after breakfast',
                        prefixIcon: const Icon(Icons.message_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey.shade300),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFF2E5BBA)),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // Time Schedule
              _buildSectionCard(
                title: 'Time Schedule',
                icon: Icons.schedule,
                child: Column(
                  children: [
                    ..._selectedTimes.asMap().entries.map((entry) {
                      return _buildTimeCard(entry.key, entry.value);
                    }),
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: _addTime,
                        icon: const Icon(Icons.add),
                        label: const Text('Add Another Time'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFF2E5BBA),
                          side: const BorderSide(color: Color(0xFF2E5BBA)),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // Days Selection
              _buildSectionCard(
                title: 'Days of the Week',
                icon: Icons.calendar_today,
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _daysOfWeek.asMap().entries.map((entry) {
                    int index = entry.key;
                    String day = entry.value;
                    String abbreviation = _dayAbbreviations[index];
                    bool isSelected = _selectedDays.contains(day);
                    
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          if (isSelected) {
                            _selectedDays.remove(day);
                          } else {
                            _selectedDays.add(day);
                          }
                        });
                      },
                      child: Container(
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(
                          color: isSelected ? const Color(0xFF2E5BBA) : Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isSelected ? const Color(0xFF2E5BBA) : Colors.grey.shade300,
                            width: 2,
                          ),
                        ),
                        child: Center(
                          child: Text(
                            abbreviation,
                            style: TextStyle(
                              color: isSelected ? Colors.white : Colors.grey.shade600,
                              fontWeight: FontWeight.w600,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),

              // Status
              Card(
                elevation: 2,
                margin: const EdgeInsets.only(bottom: 30),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: SwitchListTile(
                  title: const Text(
                    'Active Reminder',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  subtitle: Text(
                    _isActive ? 'This reminder is active' : 'This reminder is inactive',
                    style: TextStyle(color: Colors.grey.shade600),
                  ),
                  value: _isActive,
                  onChanged: (value) {
                    setState(() {
                      _isActive = value;
                    });
                  },
                  secondary: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: (_isActive ? Colors.green : Colors.grey).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      _isActive ? Icons.notifications_active : Icons.notifications_off,
                      color: _isActive ? Colors.green : Colors.grey,
                    ),
                  ),
                  activeColor: const Color(0xFF2E5BBA),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                ),
              ),

              // Create Button
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _createReminder,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2E5BBA),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    elevation: 2,
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
                          'Create Reminder',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 