# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the dashboard frontend for CareChat - a React TypeScript application that displays analytics for hospital feedback and reminder data. The dashboard provides visualizations for sentiment analysis, rating distributions, common issues, and reminder activity.

## Development Commands

### Core Development Commands
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production  
npm run build

# Lint code
npm run lint

# Type check
npm run typecheck

# Preview production build
npm run preview
```

## Architecture Overview

### Project Structure
- **src/main.tsx**: App entry point with React initialization
- **src/App.tsx**: Root component that renders the Dashboard
- **src/components/**: Reusable UI components
  - **Dashboard.tsx**: Main dashboard component with data fetching and chart rendering
  - **StatsCard.tsx**: Reusable statistics card component  
  - **ChartCard.tsx**: Wrapper component for chart visualizations

### Key Components

#### Dashboard Architecture
The `Dashboard` component (`src/components/Dashboard.tsx:26`) is the central orchestrator that:
- Fetches data from API endpoints using `useEffect` and `useState` hooks
- Handles loading, error, and retry states
- Transforms raw API data into chart-compatible formats
- Renders stats cards and various chart visualizations

#### Data Flow
- Dashboard fetches data from `https://darkness-pulse-calibration-continuing.trycloudflare.com///api/summary` (line 38)
- API data is transformed for chart consumption (Recharts format) starting at line 99
- Export functionality downloads CSV from `/api/export` endpoint (line 51-69)
- Loading states and error handling with retry functionality (lines 71-95)

#### Chart Types and Data Processing
- **Pie Chart**: Sentiment analysis distribution (lines 100-104, 177-197)
- **Bar Charts**: Rating distribution (lines 106-109, 199-211) and common issues (lines 111-114, 214-225) 
- **Line Chart**: Daily reminder activity over time (lines 116-119, 227-238)

### Technology Stack
- **React 19**: UI framework with hooks for state management
- **TypeScript**: Type safety and development experience  
- **Vite**: Build tool and development server with React SWC plugin
- **Tailwind CSS**: Styling framework with @tailwindcss/vite plugin
- **Recharts**: Chart library for data visualizations
- **Lucide React**: Icon library

### Configuration Files
- **vite.config.ts**: Vite configuration with React SWC and Tailwind plugins
- **eslint.config.js**: ESLint configuration with TypeScript, React hooks, and React refresh plugins
- **tsconfig.json**: TypeScript project references configuration
- **vercel.json**: Vercel deployment configuration for SPA routing

### API Integration
- Backend API hosted at `https://darkness-pulse-calibration-continuing.trycloudflare.com///api/`
- `/summary` endpoint provides analytics data with structure defined in `ApiData` interface (lines 7-24)
- `/export` endpoint returns CSV file for data export
- Error handling with user-friendly messages and retry functionality

### Styling Approach
- Utility-first CSS with Tailwind
- Responsive design with mobile-first approach (grid layouts adapt from 1 to 4 columns)
- Consistent color scheme (blue primary, semantic colors for sentiment)
- Card-based layout with subtle shadows and borders
- Loading spinner and error states with proper UX patterns