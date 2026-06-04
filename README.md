# 🚂 AI KAVACH - Smart Train Collision Prevention System

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.6.1-orange)](https://scikit-learn.org)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-green)](https://docs.python.org/3/library/tkinter.html)
[![AI](https://img.shields.io/badge/AI-Powered-red)](https://github.com/Amoghdatta/AI-Kavach)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

🔗 **GitHub Repository**: [https://github.com/Amoghdatta/AI-Kavach.git](https://github.com/Amoghdatta/AI-Kavach.git)

> **AI-powered railway collision prevention system with real-time monitoring, concurrent AI recommendations, and automatic emergency response**

## 🎯 Overview

AI KAVACH is an intelligent train collision prevention system that uses advanced AI algorithms to monitor multiple trains in real-time, predict collision risks, and automatically implement safety measures to prevent accidents.

## ✨ Key Features

- 🚨 **Real-time Collision Detection** - Advanced physics-based collision prediction
- 🤖 **AI-Powered Recommendations** - Smart safety suggestions and automatic responses
- 🛑 **Automatic Emergency Braking** - Progressive speed reduction and emergency stops
- 📊 **Multi-Train Monitoring** - Simultaneous tracking of multiple trains
- ⚡ **Instant Response** - 5 updates per second for immediate collision prevention
- 🎮 **Interactive GUI** - User-friendly control center interface
- 🔧 **No External Dependencies** - Self-contained AI models (no sklearn required)

## 🚀 Quick Start

### Single Command Launch

```bash
# Main command to start AI Kavach
python ai_kavach.py
```

### Alternative Commands

```bash
# Windows PowerShell
python.exe ai_kavach.py

# macOS/Linux
python3 ai_kavach.py

# Direct control center launch
python control_center_prototype.py
```

### What Happens When You Run

The system will automatically:

1. ✅ Check Python version (3.7+ required)
2. ✅ Verify system dependencies (tkinter, math, time, threading)
3. ✅ Initialize standalone AI models (no external dependencies)
4. ✅ Test collision detection algorithms
5. ✅ Launch interactive GUI control center
6. ✅ Start concurrent AI recommendation engine
7. ✅ Begin real-time train monitoring

### Expected Output

```
🚂 AI KAVACH - Smart Train Collision Prevention System
============================================================
🎯 Single Command Launcher
📅 Version: 2025.09.21
👨‍💻 Optimized for real-time collision prevention
============================================================

✅ Python version: 3.12.10
🔍 Checking dependencies...
   ✅ tkinter
   ✅ time
   ✅ random
   ✅ math
   ✅ threading
   ✅ json
✅ All dependencies satisfied

🤖 Initializing AI models...
✅ Standalone AI models loaded successfully
✅ Collision detection working
✅ AI models initialized successfully

🚀 Starting AI KAVACH Control Center...
✅ Control center loaded
🎯 System ready for operation
```

## 📋 System Requirements

### Environment Requirements

- **Python**: 3.7 or higher (recommended: Python 3.10+)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 1GB RAM minimum (recommended: 2GB+)
- **Storage**: 100MB free space
- **Display**: GUI desktop environment (for Tkinter interface)

### Python Dependencies

#### Core Dependencies (Built-in)

- `tkinter` - GUI framework (included with Python)
- `math` - Mathematical calculations
- `time` - Time utilities
- `threading` - Multi-threading support
- `json` - Data handling
- `random` - Random number generation

#### Optional Dependencies

- `scikit-learn==1.6.1` - For advanced AI models (optional, built-in fallback available)

### Environment Setup

#### Windows

```bash
# Check Python version
python --version

# Install scikit-learn (optional)
pip install scikit-learn==1.6.1
```

#### macOS/Linux

```bash
# Check Python version
python3 --version

# Install tkinter if missing (Linux only)
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install tkinter          # CentOS/RHEL

# Install scikit-learn (optional)
pip3 install scikit-learn==1.6.1
```

## 📦 Installation

### Option 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/Amoghdatta/AI-Kavach.git
cd AI-Kavach

# Optional: Install scikit-learn for advanced features
pip install scikit-learn==1.6.1

# Run the system
python ai_kavach.py
```

### Option 2: Download ZIP

1. Visit: [https://github.com/Amoghdatta/AI-Kavach.git](https://github.com/Amoghdatta/AI-Kavach.git)
2. Click "Code" → "Download ZIP"
3. Extract to your desired folder
4. Open terminal/command prompt in the folder
5. Run: `python ai_kavach.py`

### Option 3: Manual Setup

Download these core files to a folder:

- `ai_kavach.py` (main launcher - **required**)
- `control_center_prototype.py` (control center - **required**)
- `ai_recommendations.py` (AI recommendation engine - **required**)
- `standalone_ai_models.py` (AI models - **required**)
- `requirements.txt` (dependencies list)

### Verify Installation

```bash
# Test the installation
python ai_kavach.py

# Should show system startup messages and open GUI
```

## 🎮 Usage Guide

### Starting the System

```bash
# Main command (recommended)
python ai_kavach.py

# Alternative commands
python control_center_prototype.py  # Direct control center
python3 ai_kavach.py               # macOS/Linux
python.exe ai_kavach.py            # Windows explicit
```

### Control Center Interface

#### Main Sections

1. **Train Display** - Visual representation of trains and tracks
2. **AI Recommendations** - Real-time safety suggestions
3. **Control Panel** - Manual train controls and emergency stop
4. **Status Monitor** - System health and train information

#### Key Controls

- **Emergency Stop** 🛑 - Immediately stops all trains
- **AI Toggle** 🤖 - Enable/disable AI recommendations
- **Speed Control** ⚡ - Manual train speed adjustment
- **Track Selection** 🛤️ - Monitor specific railway segments

### Collision Prevention Features

#### Automatic Safety Measures

- **3000+ feet**: Early warning (speed limit: 60 mph)
- **2000+ feet**: Caution mode (speed limit: 40 mph)
- **1200+ feet**: Moderate reduction (speed limit: 20 mph)
- **800+ feet**: Auto-slow (speed limit: 5 mph)
- **Under 500 feet**: Emergency stop (both trains stopped)

#### AI Recommendations

The system automatically generates recommendations for:

- Speed adjustments
- Route changes
- Emergency stops
- Signal modifications
- Maintenance alerts

## 🧪 Testing

### Run System Tests

```bash
# Comprehensive system test
python test_system.py

# Individual component tests
python demo_collision_response.py  # Test collision prevention
python test_emergency_stop.py      # Test emergency systems
```

### Test Results

The system test validates:

- ✅ AI model functionality (5/5 models)
- ✅ Collision detection (3/3 scenarios)
- ✅ GUI components
- ✅ File operations
- ✅ Cross-platform compatibility

## 🐛 Troubleshooting

### Common Issues

#### Python Version Error

```
❌ Error: Python 3.7 or higher required
```

**Solution**: Install Python 3.7+ from [python.org](https://python.org)

#### Tkinter Missing (Linux)

```
❌ tkinter - MISSING
```

**Solution**:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
```

#### Permission Errors

```
❌ Write permissions failed
```

**Solution**: Run from a folder where you have write access

## 🤝 Contributing

### Development Setup

1. Clone the repository
2. Make your changes
3. Run tests: `python test_system.py`
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author & Maker

Developed and created by **[Amoghdatta](https://github.com/Amoghdatta)**.

## 🙋‍♂️ Support

### Getting Help

- Check the troubleshooting section above
- Run `python test_system.py` for diagnostics
- Create an issue on GitHub with system test output

## 📋 Project Structure

```
ai_kavach/
├── ai_kavach.py                    # 🚀 Main launcher (START HERE)
├── control_center_prototype.py     # 🖥️ GUI control center
├── ai_recommendations.py           # 🤖 AI recommendation engine
├── standalone_ai_models.py         # 🧠 AI models & algorithms
├── requirements.txt                # 📦 Dependencies list
├── README.md                      # 📚 This documentation
├── LICENSE                        # ⚖️ License information
└── ai_models/                     # 📁 Pre-trained models (optional)
    ├── collision_model.pkl
    ├── delay_prediction_model.pkl
    └── ...
```

## 🔧 Technical Specifications

### Core Technologies

- **Language**: Python 3.7+
- **GUI Framework**: Tkinter (cross-platform)
- **AI Engine**: Standalone algorithms + optional scikit-learn
- **Architecture**: Multi-threaded concurrent processing
- **Data Processing**: Built-in Python libraries

### Performance Specifications

- **Real-time Updates**: 5 FPS (200ms cycles)
- **AI Analysis**: 3-second intervals
- **Collision Detection**: Continuous monitoring
- **Response Time**: <1 second emergency stops
- **Memory Usage**: ~50MB baseline

## 🆘 Emergency Features

### Automatic Safety Systems

- **Progressive Speed Control**: Distance-based automatic speed reduction
- **Emergency Braking**: Instant stop for collision risks <1000 feet
- **Stationary Train Detection**: Stop approaching trains automatically
- **Head-on Collision Prevention**: Both trains stopped immediately
- **Multi-train Coordination**: System-wide emergency protocols

---

## 🎯 Ready to Get Started?

### **Single Command to Launch Everything:**

```bash
python ai_kavach.py
```

### **GitHub Repository:**

🔗 [https://github.com/Amoghdatta/AI-Kavach.git](https://github.com/Amoghdatta/AI-Kavach.git)

---

**⚡ Start preventing train collisions with AI - Run the command above and experience the future of railway safety!** 🚂🛡️
