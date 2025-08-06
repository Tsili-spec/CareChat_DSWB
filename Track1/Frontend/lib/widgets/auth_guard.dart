import 'package:flutter/material.dart';
import 'package:care_chat/services/auth_service.dart';
import 'package:care_chat/screen/login.dart';

class AuthGuard extends StatelessWidget {
  final Widget child;
  
  const AuthGuard({
    Key? key,
    required this.child,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: AuthService().isAuthenticated(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
        
        if (snapshot.hasData && snapshot.data == true) {
          return child;
        }
        
        // User not authenticated, redirect to login
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(builder: (context) => const LoginScreen()),
            (route) => false,
          );
        });
        
        return const Scaffold(
          body: Center(
            child: CircularProgressIndicator(),
          ),
        );
      },
    );
  }
}