# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CareChat is a Flutter healthcare application designed for patient reminder management and hospital experience tracking. The app includes user authentication, reminder creation/management, and patient experience feedback features.

## Development Commands

### Core Flutter Commands
```bash
# Run the app in debug mode
flutter run

# Build for release
flutter build apk              # Android APK
flutter build appbundle       # Android App Bundle
flutter build ios             # iOS (requires macOS)

# Run tests
flutter test

# Analyze code for issues
flutter analyze

# Format code
flutter format .

# Clean build artifacts
flutter clean

# Get dependencies
flutter pub get

# Upgrade dependencies
flutter pub upgrade
```

### Platform-Specific Commands
```bash
# Run on specific platform
flutter run -d chrome         # Web
flutter run -d windows        # Windows
flutter run -d macos          # macOS
flutter run -d linux          # Linux

# Build for specific platforms
flutter build web
flutter build windows
flutter build macos
flutter build linux
```

## Architecture Overview

### Project Structure
- **lib/main.dart**: App entry point, routes to SplashScreen
- **lib/screen/**: UI screens including authentication, main navigation, and feature screens
- **lib/services/**: Business logic layer with API communication and data management
- **lib/models/**: Data models for application entities

### Key Components

#### Navigation Architecture
- **MainScreen**: Central navigation hub with bottom navigation bar (3 tabs: Home, Reminders, Profile)
- **SplashScreen**: Initial loading screen that routes to appropriate screens
- Uses PageView with PageController for smooth tab transitions

#### Service Layer
- **ApiService**: Handles HTTP requests, authentication token management with flutter_secure_storage
- **ReminderService**: In-memory reminder management (no persistence)
- **API Endpoints**: Centralized API URL configuration pointing to render.com backend

#### Authentication Flow
- Login/signup screens with phone number and email-based authentication
- Secure token storage using flutter_secure_storage
- Backend integration with REST API

#### Reminder System
- Local reminder management with Reminder model
- Create/view reminders with time and day scheduling
- Floating action button integration on reminder tab

### Dependencies
- **flutter_sound**: Audio recording capabilities
- **http**: REST API communication
- **flutter_secure_storage**: Secure token/credential storage
- **flutter_lints**: Code quality and style enforcement

### Development Notes
- Uses Material Design components
- Custom gradient styling for bottom navigation
- No local persistence for reminders (service layer uses in-memory storage)
- Backend API hosted on render.com at `https://carechat-dswb-v8ex.onrender.com/api/`