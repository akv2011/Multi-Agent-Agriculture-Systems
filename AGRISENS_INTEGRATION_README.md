# AgriMitr Integration with Multi-Agent Agriculture Systems

This README describes the integration of AgriMitr AI models with the Multi-Agent Agriculture Systems project, covering both backend and frontend aspects.

## Overview

AgriMitr provides advanced machine learning models for agricultural applications, including:
- Crop recommendation (99.55% accuracy Random Forest model)
- Disease identification (CNN model for 38 diseases across 14 crops)
- Irrigation scheduling (ML-enhanced water management)

These models have been integrated into our agent-based system to enhance decision-making capabilities.

## Backend Integration

### 1. Models

The following model integrations have been implemented:

- **Crop Recommendation Model**: `/src/models/AgriMitr_crop_recommendation.py`
  - Random Forest model with 99.55% accuracy
  - Analyzes NPK values, climate factors, and soil properties
  - Enhanced with satellite data integration
  
- **Disease Identification Model**: `/src/models/AgriMitr_disease_identification.py`
  - CNN-based model for identifying 38 different plant diseases
  - Works with 14 crop types including wheat, rice, tomato, apple
  - Provides treatment recommendations and prevention strategies
  
- **Irrigation Scheduling Model**: `/src/models/AgriMitr_irrigation_scheduling.py`
  - Optimizes water application based on crop needs and environmental factors
  - Reduces water usage while maximizing yield
  - Integrates with satellite soil moisture data

### 2. Agents

The following agents leverage the AgriMitr models:

- **Crop Selection Agent**: `/src/agents/crop_selection_agent.py`
  - Uses AgriMitr crop recommendation model
  - Enhanced with satellite data integration
  
- **Irrigation Agent**: `/src/agents/irrigation_agent.py`
  - Uses AgriMitr irrigation scheduling model
  - Generates water-efficient irrigation schedules
  
- **Disease Identification Agent**: `/src/agents/disease_identification_agent.py`
  - NEW agent that uses AgriMitr CNN models
  - Identifies plant diseases from images
  - Provides treatment and prevention recommendations

### 3. Tests

Integration tests have been added to validate the model integrations:

- `tests/test_AgriMitr_integration.py`: Tests all three agent integrations
- `tests/test_irrigation_model_integration.py`: Specific tests for irrigation model

## Frontend Integration

The frontend has been updated to accommodate the new disease identification capabilities and to display all AgriMitr-enabled agents:

### 1. Dashboard Updates

- Added the Disease Identification Specialist agent to the dashboard in `AgricultureDashboard.tsx`
- Enhanced the disease identification UI in the chat interface

### 2. Disease Identification UI

The disease image upload UI in `AgricultureChat.tsx` has been enhanced with:
- Better guidance about supported crops and diseases
- Indication that the CNN model is being used
- Clear workflow for uploading and analyzing disease images

### 3. Results Visualization

The frontend now properly displays disease identification results including:
- Detected disease with confidence level
- Severity assessment and affected area percentage
- Treatment and prevention recommendations

## Demo Script

A demonstration script has been created to showcase the integrated models:

- `AgriMitr_demo.py`: Shows all three AgriMitr models in action
  - Crop recommendation with different locations
  - Irrigation scheduling for different crops
  - Disease identification with example plant images

## Running the Integration

1. Start the backend server:
   ```bash
   python main.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Run the AgriMitr demo:
   ```bash
   ./AgriMitr_demo.py
   ```

4. Run integration tests:
   ```bash
   python -m unittest tests/test_AgriMitr_integration.py
   ```

## Future Improvements

1. Add more crop types to the disease identification model
2. Implement fertilizer recommendation based on AgriMitr models
3. Create a specialized visualization dashboard for disease identification results
4. Add real-time disease monitoring with regular satellite image analysis
