
# UI/UX Branch for Track 1: Patient Feedback and Reminder Management System

## Overview
The `UI/UX` branch of the (https://github.com/Tsili-spec/CareChat_DSWB.git) is dedicated to storing and collaborating on UI/UX design assets for 
**Track 1: Patient Feedback and Reminder Management System**. This branch contains wireframes, mockups, prototypes, and related design files for patient-facing (e.g., Feedback Interface, Reminder Confirmation) and admin-facing (e.g., Feedback Analysis Dashboard) pages.

## Purpose
- **Centralized Design Storage**: Store all UI/UX assets (e.g., PNGs, PDFs, GIFs) for team review and iteration.
- **Collaboration**: Enable designers, developers, and stakeholders to provide feedback via GitHub Issues and Pull Requests.
- **Version Control**: Track design iterations using Git’s branching system.

## Contents
The branch includes design assets, organized as follows:
- **Wireframes**: Low-fidelity designs
- **Mockups**: High-fidelity designs 
- **Prototypes**: Interactive prototypes or animations 
- **Screenshots**: UI screenshots 
- **Documentation**: Notes or specifications 


## Contact
For questions or feedback, create an Issue or contact the repository owner. Carechat team.


# Patient Feedback Analysis Module
https://github.com/user-attachments/assets/60eda92f-b8df-4f49-a94f-35e3a5d7f7f0
https://github.com/user-attachments/assets/51398e84-94cb-4d8e-83cf-59683d373815

This branch contains the core logic for analyzing patient feedback using a combination of NLP (Natural Language Processing) and star ratings. 

🔍 What This Module Does
Sentiment Analysis

Uses NLP to classify feedback as positive, neutral, or negative.

Falls back to star rating when no text is provided.

Prioritizes text sentiment when both are available.

Topic Detection

Identifies key topics in feedback: wait_time, staff_attitude, medication, cost.

Urgency Flagging

Detects critical feedback using urgent keywords like "emergency", "bleeding", "wrong drug", etc.
# CareChat - Hospital Feedback & Analytics Platform

A comprehensive healthcare feedback system consisting of a Flutter mobile application for patient feedback collection and a React-based analytics dashboard for data visualization and insights.

## 🏗️ Project Structure

```
├── lib/                          # Flutter Mobile App
│   ├── main.dart                 # App entry point
│   ├── models/                   # Data models
│   ├── screen/                   # UI screens
│   │   ├── splash_screen.dart
│   │   ├── welcome.dart
│   │   ├── login.dart
│   │   ├── create_account.dart
│   │   ├── main_screen.dart
│   │   ├── home.dart
│   │   ├── profile.dart
│   │   ├── reminder.dart
│   │   ├── create_reminder.dart
│   │   └── feedback.dart
│   └── services/                 # Business logic & API services
│       └── reminder_service.dart
├── Dashboard/dashboard/          # React Analytics Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── StatsCard.tsx
│   │   │   └── ChartCard.tsx
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
├── android/                      # Android platform files
├── ios/                         # iOS platform files
└── assets/                      # Shared assets
```
<!-- Alternative video embedding methods:

#### Option 1: YouTube Embed (Click to play)
[![Mobile App Demo](https://img.youtube.com/vi/YOUR_YOUTUBE_ID/0.jpg)](https://www.youtube.com/watch?v=YOUR_YOUTUBE_ID)

#### Option 2: GIF Preview with Video Link
![App Demo](assets/demo.gif)
[📹 Watch Full Video](https://your-video-link.com)

#### Option 3: HTML5 Video (if supported)
<video width="320" height="240" controls>
  <source src="assets/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

-->

### Features
- **Patient Feedback Collection**: Intuitive interface for hospital experience feedback
- **Reminder System**: Medication and appointment reminders
- **User Authentication**: Secure login and account creation
- **Multi-language Support**: English language support with expandable architecture
- **Offline Capability**: Local data storage with sync capabilities

### Tech Stack
- **Framework**: Flutter 3.x
- **Language**: Dart
- **State Management**: StatefulWidget with local state
- **Storage**: Flutter Secure Storage
- **Audio**: Flutter Sound for voice recordings
- **Permissions**: Permission Handler
- **HTTP**: Built-in HTTP client for API communication

### Getting Started

#### Prerequisites
- Flutter SDK (3.0 or higher)
- Dart SDK
- Android Studio / VS Code
- Android SDK / Xcode (for iOS)

#### Installation
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd carechat
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the application**
   ```bash
   # For Android
   flutter run
   
   # For iOS
   flutter run -d ios
   
   # For specific device
   flutter devices
   flutter run -d <device-id>
   ```

#### Build for Production
```bash
# Android APK
flutter build apk --release

# Android App Bundle
flutter build appbundle --release

# iOS
flutter build ios --release
```

### Key Screens

#### Home Screen (`lib/screen/home.dart`)
- Welcome interface with CareChat branding
- Custom robot icon animation
- Navigation to feedback collection

#### Feedback Screen (`lib/screen/feedback.dart`)
- Hospital experience rating system
- Sentiment analysis integration
- Voice and text feedback options

#### Reminder System (`lib/screen/reminder.dart`)
- Medication reminders
- Appointment scheduling
- Notification management

#### Profile Management (`lib/screen/profile.dart`)
- User account settings
- Preferences configuration
- Data export options

### API Integration
The Flutter app communicates with the backend API:
- **Base URL**: `https://carechat-dswb-v8ex.onrender.com/api/`
- **Endpoints**:
  - `/summary` - Analytics data
  - `/export` - Data export functionality

## 📊 React Analytics Dashboard

### Features
- **Real-time Analytics**: Live data visualization from patient feedback
- **Sentiment Analysis**: Positive, neutral, and negative feedback trends
- **Rating Distribution**: Star rating breakdowns and trends
- **Issue Tracking**: Common problems and negative topic analysis
- **Reminder Analytics**: Daily reminder activity tracking
- **Data Export**: CSV export functionality for further analysis

### Tech Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 7.x
- **Styling**: Tailwind CSS v4
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React
- **HTTP Client**: Fetch API

### Getting Started

#### Prerequisites
- Node.js (18 or higher)
- npm or yarn

#### Installation
1. **Navigate to dashboard directory**
   ```bash
   cd Dashboard/dashboard
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

5. **Preview production build**
   ```bash
   npm run preview
   ```

### Dashboard Components

#### Main Dashboard (`src/components/Dashboard.tsx`)
- Fetches data from API endpoints
- Handles loading and error states
- Orchestrates all chart components
- Manages data export functionality

#### Stats Cards (`src/components/StatsCard.tsx`)
- Key metrics display
- Trend indicators
- Icon-based visual representation

#### Chart Cards (`src/components/ChartCard.tsx`)
- Reusable chart container
- Consistent styling and layout
- Title and description support

### Data Visualization

#### Sentiment Analysis (Pie Chart)
- Visual breakdown of positive, neutral, and negative feedback
- Color-coded segments for easy interpretation

#### Rating Distribution (Bar Chart)
- Star rating frequency analysis
- Helps identify satisfaction patterns

#### Common Issues (Horizontal Bar Chart)
- Most frequently reported problems
- Prioritizes areas needing attention

#### Daily Reminders (Line Chart)
- Reminder activity over time
- Trend analysis for user engagement

### API Integration
The dashboard consumes the following endpoints:

```typescript
// Summary data for all analytics
GET https://carechat-dswb-v8ex.onrender.com/api/summary

// Response format:
{
  "rating_trends": {
    "Unknown": { "0": 6, "2": 1, "3": 2, "4": 3 }
  },
  "sentiment_summary": {
    "negative": 5, "neutral": 4, "positive": 3
  },
  "negative_topic_counts": {
    "Unidentified": 1,
    "{staff_attitude}": 3,
    "{medication,cost}": 1
  },
  "reminders_by_day": {
    "2025-07-18": 2
  }
}

// CSV export endpoint
GET https://carechat-dswb-v8ex.onrender.com/api/export
```

## 🚀 Deployment

### Flutter Mobile App
1. **Android Play Store**
   ```bash
   flutter build appbundle --release
   # Upload to Google Play Console
   ```

2. **iOS App Store**
   ```bash
   flutter build ios --release
   # Archive and upload via Xcode
   ```

### React Dashboard
1. **Build production assets**
   ```bash
   cd Dashboard/dashboard
   npm run build
   ```

2. **Deploy to hosting service**
   - Vercel: `vercel --prod`
   - Netlify: Drag and drop `dist` folder
   - AWS S3: Upload `dist` contents

## 🔧 Configuration

### Environment Variables
Create `.env` files for environment-specific configurations:

```bash
# Flutter (android/local.properties)
FLUTTER_API_BASE_URL=https://carechat-dswb-v8ex.onrender.com/api/

# React Dashboard (.env)
VITE_API_BASE_URL=https://carechat-dswb-v8ex.onrender.com/api/
```

### Tailwind CSS v4 Configuration
The dashboard uses Tailwind CSS v4 with the following setup:

```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

```css
/* src/index.css */
@import "tailwindcss";
```

## 🧪 Testing

### Flutter Testing
```bash
# Run unit tests
flutter test

# Run integration tests
flutter drive --target=test_driver/app.dart
```

### React Testing
```bash
# Run component tests
npm run test

# Run with coverage
npm run test:coverage
```

## 📝 Development Guidelines

### Code Style
- **Flutter**: Follow Dart style guide with `flutter analyze`
- **React**: ESLint configuration with TypeScript strict mode
- **Commits**: Use conventional commit messages

### Performance Optimization
- **Flutter**: Use `const` constructors, avoid rebuilds
- **React**: Implement proper memoization, code splitting
- **Images**: Optimize assets for mobile and web

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

## 🔄 Version History

- **v1.0.0** - Initial release with basic feedback collection
- **v1.1.0** - Added reminder system and analytics dashboard
- **v1.2.0** - Enhanced UI/UX and performance improvements


**Built with ❤️ for better healthcare experiences**


