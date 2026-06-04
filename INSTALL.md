# 🛠️ AI KAVACH Installation Guide

Complete installation instructions for Windows, macOS, and Linux.

## 📋 Pre-Installation Checklist

Before installing AI KAVACH, ensure you have:

- [ ] Python 3.7 or higher installed
- [ ] Terminal/Command Prompt access
- [ ] Internet connection (for downloading)
- [ ] 50MB free disk space

## 🖥️ Windows Installation

### Method 1: Direct Download & Run

1. **Download Files**

   ```cmd
   # Create a folder for AI KAVACH
   mkdir C:\AI_KAVACH
   cd C:\AI_KAVACH

   # Download the main files (or use git clone)
   ```

2. **Check Python Installation**

   ```cmd
   python --version
   ```

   Should show Python 3.7+ (e.g., "Python 3.12.10")

3. **Run AI KAVACH**
   ```cmd
   python ai_kavach.py
   ```

### Method 2: Git Clone (Recommended)

```cmd
# Clone the repository
git clone https://github.com/[YOUR_USERNAME]/ai-kavach.git
cd ai-kavach

# Run system test
python test_system.py

# Start the application
python ai_kavach.py
```

### Troubleshooting Windows

- **Python not found**: Install from [python.org](https://python.org)
- **Tkinter missing**: Usually included with Python on Windows
- **Permission denied**: Run Command Prompt as Administrator

## 🍎 macOS Installation

### Method 1: Using Terminal

1. **Open Terminal** (Applications > Utilities > Terminal)

2. **Check Python Installation**

   ```bash
   python3 --version
   ```

3. **Download and Run**

   ```bash
   # Create directory
   mkdir ~/AI_KAVACH
   cd ~/AI_KAVACH

   # Clone or download files
   git clone https://github.com/[YOUR_USERNAME]/ai-kavach.git
   cd ai-kavach

   # Run the application
   python3 ai_kavach.py
   ```

### Troubleshooting macOS

- **Python not found**: Install from [python.org](https://python.org) or use Homebrew
  ```bash
  # Using Homebrew
  brew install python
  ```
- **Tkinter missing**: Usually included with Python on macOS

## 🐧 Linux Installation

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python and Tkinter
sudo apt install python3 python3-tk git

# Clone the repository
git clone https://github.com/[YOUR_USERNAME]/ai-kavach.git
cd ai-kavach

# Run system test
python3 test_system.py

# Start the application
python3 ai_kavach.py
```

### CentOS/RHEL/Fedora

```bash
# Install Python and Tkinter
sudo yum install python3 python3-tkinter git
# OR for newer versions
sudo dnf install python3 python3-tkinter git

# Clone and run
git clone https://github.com/[YOUR_USERNAME]/ai-kavach.git
cd ai-kavach
python3 ai_kavach.py
```

### Arch Linux

```bash
# Install dependencies
sudo pacman -S python python-tk git

# Clone and run
git clone https://github.com/[YOUR_USERNAME]/ai-kavach.git
cd ai-kavach
python ai_kavach.py
```

## 🐳 Docker Installation (Optional)

Create a Dockerfile for containerized deployment:

```dockerfile
FROM python:3.11-slim

# Install tkinter
RUN apt-get update && apt-get install -y python3-tk

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Run the application
CMD ["python", "ai_kavach.py"]
```

Build and run:

```bash
docker build -t ai-kavach .
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ai-kavach
```

## ✅ Verification

After installation, verify everything works:

### 1. Run System Test

```bash
python test_system.py
```

Expected output:

```
🎯 AI KAVACH - COMPLETE SYSTEM TEST
✅ IMPORTS         PASS
✅ AI_MODELS       PASS
✅ COLLISION       PASS
✅ GUI             PASS
✅ FILES           PASS
🚀 AI KAVACH system is ready!
```

### 2. Quick Feature Test

```bash
python demo_collision_response.py
```

Should show collision prevention in action.

### 3. Launch Main Application

```bash
python ai_kavach.py
```

Should open the GUI control center.

## 🚨 Common Issues & Solutions

### Python Version Issues

```bash
# Check version
python --version
python3 --version

# If version is < 3.7, install newer Python
```

### GUI Not Working (Linux)

```bash
# For SSH connections, enable X11 forwarding
ssh -X username@hostname

# Or install VNC server for remote GUI access
```

### File Permission Issues

```bash
# Make sure you have write permissions
chmod +x ai_kavach.py
chmod 755 .
```

### Missing Dependencies

All dependencies are part of Python standard library. If you get import errors:

```bash
# Reinstall Python with full standard library
# Windows: Download from python.org (check "Add to PATH")
# macOS: brew install python
# Linux: sudo apt install python3-full
```

## 🔧 Development Setup

For developers who want to modify the code:

```bash
# Clone with development branch
git clone -b develop https://github.com/[YOUR_USERNAME]/ai-kavach.git
cd ai-kavach

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Run in development mode
python ai_kavach.py

# Run all tests
python test_system.py
```

## 📞 Getting Help

If you encounter issues:

1. **Check System Requirements**: Python 3.7+, tkinter installed
2. **Run Diagnostics**: `python test_system.py`
3. **Check Documentation**: Read the README.md file
4. **Search Issues**: Check GitHub issues for similar problems
5. **Create Issue**: Report bugs with system test output

## 🎉 Next Steps

After successful installation:

1. Explore the GUI interface
2. Try the collision prevention demo
3. Experiment with different train scenarios
4. Read the usage guide in README.md
5. Contribute to the project!

---

**🚂 Happy train collision prevention with AI KAVACH!**
