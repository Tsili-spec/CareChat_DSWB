import 'package:flutter/material.dart';

class Reminder {
  final String? reminderId;
  final String title;
  final String message;
  final String patientId;
  final List<String> days;
  final List<DateTime> scheduledTime;
  final String status;
  final DateTime? createdAt;
  String get type => 'Medication';

  Reminder({
    this.reminderId,
    required this.title,
    required this.message,
    required this.patientId,
    required this.days,
    required this.scheduledTime,
    required this.status,
    this.createdAt,
  });

  factory Reminder.fromJson(Map<String, dynamic> json) {
    return Reminder(
      reminderId: json['reminder_id'],
      title: json['title'],
      message: json['message'],
      patientId: json['patient_id'],
      days: List<String>.from(json['days']),
      scheduledTime: (json['scheduled_time'] as List)
          .map((time) => DateTime.parse(time))
          .toList(),
      status: json['status'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'patient_id': patientId,
      'title': title,
      'message': message,
      'scheduled_time': scheduledTime.map((time) => time.toIso8601String()).toList(),
      'days': days,
      'status': status,
    };
  }

  // Helper getters for UI
  bool get isActive => status == 'active';
  
  List<TimeOfDay> get times {
    return scheduledTime.map((dateTime) => 
      TimeOfDay(hour: dateTime.hour, minute: dateTime.minute)
    ).toSet().toList(); // Remove duplicates
  }
} 