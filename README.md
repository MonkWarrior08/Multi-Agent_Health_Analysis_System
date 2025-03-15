# 🤖 Multi-Agent Health Analysis System

![AutoGen](https://img.shields.io/badge/AutoGen-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🔍 Overview

AutoGen is an intelligent multi-agent system that analyzes health data from various sources to generate personalized daily health plans. The system uses a collaborative approach with specialized AI agents that work together to create actionable insights.

## ✨ Features

- **Multi-Agent Architecture**: Coordinated system of specialized agents for comprehensive analysis
- **Structured Data Analysis**: Processes app-based journal entries for pattern recognition
- **Historical Context**: Analyzes long-term health patterns from historical journals
- **Personal Insight Integration**: Incorporates subjective user observations into recommendations
- **Personalized Planning**: Generates daily health plans tailored to individual needs

## 🛠️ Components

- **Main Coordinator**: Orchestrates the analysis workflow and agent interactions
- **App Journal Analyst**: Specializes in structured health tracking data
- **Historical Journal Analyst**: Examines patterns from long-term health records
- **User Insights Analyst**: Evaluates subjective observations and preferences
- **Health Plan Synthesizer**: Creates actionable health plans from combined analyses

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- API keys for OpenAI and Google Gemini

### Installation

1. Clone this repository
```bash
git clone https://github.com/yourusername/autogen.git
cd autogen
```

2. Install required dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables (create a .env file with):
```
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### Usage

Run the main application:
```bash
python main.py
```

## 📁 File Utilities

The project includes utilities for processing and combining various data files:

- `combine_md.py`: Combines markdown journal entries with date sorting
- `combine_txt.py`: Combines text-based app journal entries chronologically
- `rename_md.py`: Utility for standardizing file names

## 🔧 Customization

Modify the agent system messages in `main.py` to adapt the analysis focus for different health contexts or data sources.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

⭐ **AutoGen** - Transforming health data into actionable insights ⭐