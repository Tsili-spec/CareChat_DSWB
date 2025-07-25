import 'package:care_chat/models/reminder_model.dart';
import 'package:care_chat/services/api_service.dart';

class ReminderService {
  final List<Reminder> _reminders = [];
  final ApiService _apiService = ApiService();

  List<Reminder> get reminders => _reminders;

  Future<Map<String, dynamic>> loadReminders() async {
    try {
      final result = await _apiService.getUserReminders();
      
      if (result['success'] == true && result['reminders'] != null) {
        _reminders.clear();
        for (var reminderData in result['reminders']) {
          _reminders.add(Reminder.fromJson(reminderData));
        }
        return {'success': true, 'message': 'Reminders loaded successfully'};
      } else {
        return result;
      }
    } catch (e) {
      return {'success': false, 'message': 'An error occurred: $e'};
    }
  }

  Future<Map<String, dynamic>> createReminder(Reminder reminder) async {
    try {
      final result = await _apiService.createReminder(
        title: reminder.title,
        message: reminder.message,
        days: reminder.days,
        scheduledTime: reminder.scheduledTime,
        status: reminder.status,
      );
      
      if (result['success'] == true) {
        // Add to local list if API call succeeds
        _reminders.add(reminder);
      }
      
      return result;
    } catch (e) {
      return {'success': false, 'message': 'An error occurred: $e'};
    }
  }

  void addReminder(Reminder reminder) {
    _reminders.add(reminder);
  }

  void updateReminder(int index, Reminder reminder) {
    _reminders[index] = reminder;
  }
} 