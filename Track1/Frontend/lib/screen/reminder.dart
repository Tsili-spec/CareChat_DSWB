import 'package:care_chat/models/reminder_model.dart';
import 'package:care_chat/services/reminder_service.dart';
import 'package:flutter/material.dart';

class RemindersScreen extends StatefulWidget {
  final ReminderService reminderService;
  const RemindersScreen({Key? key, required this.reminderService}) : super(key: key);

  @override
  State<RemindersScreen> createState() => _RemindersScreenState();
}

class _RemindersScreenState extends State<RemindersScreen> {
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadReminders();
  }

  Future<void> _loadReminders() async {
    if (!mounted) return;
    
    setState(() {
      _isLoading = true;
    });

    final result = await widget.reminderService.loadReminders();
    
    if (!mounted) return;
    
    setState(() {
      _isLoading = false;
    });

    if (result['success'] != true) {
      // If loading fails, show sample reminders for demo
      if (widget.reminderService.reminders.isEmpty) {
        // Add a sample reminder using the exact API format for testing
        final sampleReminder = Reminder(
          reminderId: "6b5d1b22-7a0e-4617-9bcb-0efb114675ae",
          title: "Take Morning Medication",
          message: "Please take your blood pressure medication with breakfast and a full glass of water",
          patientId: "e2625f6b-81ff-4450-981b-394ac39c497a",
          days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
          scheduledTime: [
            DateTime.parse("2024-01-15T08:00:00"),
            DateTime.parse("2024-01-16T08:00:00")
          ],
          status: "active",
          createdAt: DateTime.parse("2025-07-18T09:34:11.695680"),
        );
        
        widget.reminderService.reminders.add(sampleReminder);
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message'] ?? 'Failed to load reminders. Showing sample data.'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
    }
  }

  Future<void> _refreshReminders() async {
    await _loadReminders();
  }

  Widget _buildReminderCard({
    required Reminder reminder,
    VoidCallback? onCopyTap,
    VoidCallback? onShareTap,
  }) {
    IconData getTypeIcon() {
      switch (reminder.type) {
        case 'Medication':
          return Icons.medication;
        case 'Appointment':
          return Icons.event;
        case 'Exercise':
          return Icons.fitness_center;
        case 'Diet':
          return Icons.restaurant;
        case 'Checkup':
          return Icons.health_and_safety;
        default:
          return Icons.notifications;
      }
    }

    Color getTypeColor() {
      switch (reminder.type) {
        case 'Medication':
          return const Color(0xFF4CAF50);
        case 'Appointment':
          return const Color(0xFF2196F3);
        case 'Exercise':
          return const Color(0xFFFF9800);
        case 'Diet':
          return const Color(0xFF9C27B0);
        case 'Checkup':
          return const Color(0xFFE91E63);
        default:
          return const Color(0xFF607D8B);
      }
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [getTypeColor(), getTypeColor().withOpacity(0.8)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                  padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                    getTypeIcon(),
                  color: Colors.white,
                    size: 18,
                  ),
              ),
              const SizedBox(width: 12),
              Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        reminder.title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          reminder.status.toUpperCase(),
                          style: const TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w500,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
                  ),
                ),
                IconButton(
                  onPressed: onShareTap,
                  icon: const Icon(Icons.more_vert, color: Colors.white, size: 20),
              ),
            ],
          ),
            const SizedBox(height: 12),
          Text(
              reminder.message,
            style: const TextStyle(
                fontSize: 13,
              color: Colors.white,
                height: 1.3,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.schedule, color: Colors.white.withOpacity(0.8), size: 14),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    reminder.times.isNotEmpty 
                        ? reminder.times.map((time) => time.format(context)).join(', ')
                        : 'No times set',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white.withOpacity(0.9),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Icon(Icons.calendar_today, color: Colors.white.withOpacity(0.8), size: 14),
                const SizedBox(width: 4),
                Text(
                  '${reminder.days.length} days/week',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.white.withOpacity(0.9),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Row(
                children: [
                  // Back Button (Remove this since we're using bottom nav)
                  const SizedBox(width: 48), // Placeholder for spacing
                  
                  const Spacer(),
                  
                  // Title
                  const Text(
                    'Reminders',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF424242),
                    ),
                  ),
                  
                  const Spacer(),
                  
                  // Search Button
                  GestureDetector(
                    onTap: () {
                      // Handle search
                    },
                    child: Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: Colors.transparent,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Icon(
                        Icons.search,
                        color: Color(0xFF757575),
                        size: 24,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            // Content
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : RefreshIndicator(
                      onRefresh: _refreshReminders,
              child: SingleChildScrollView(
                        physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  children: [
                    const SizedBox(height: 20),
                            if (widget.reminderService.reminders.isEmpty)
                              Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const SizedBox(height: 60),
                                    Icon(
                                      Icons.notifications_none,
                                      size: 80,
                                      color: Colors.grey[400],
                                    ),
                                    const SizedBox(height: 16),
                                    Text(
                                      'No reminders yet',
                                      style: TextStyle(
                                        fontSize: 18,
                                        color: Colors.grey[600],
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      'Create your first reminder using the + button',
                                      style: TextStyle(
                                        fontSize: 14,
                                        color: Colors.grey[500],
                                      ),
                                    ),
                                  ],
                                ),
                              )
                            else
                              ...widget.reminderService.reminders.map((reminder) {
                                return _buildReminderCard(
                                  reminder: reminder,
                      onCopyTap: () {
                        // Handle copy action
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Reminder copied to clipboard'),
                            duration: Duration(seconds: 2),
                          ),
                        );
                      },
                      onShareTap: () {
                        // Handle share action
                      },
                                );
                              }).toList(),
                            const SizedBox(height: 120), // Extra space for bottom navigation and FAB
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