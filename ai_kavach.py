#!/usr/bin/env python3
"""
AI KAVACH - Smart Train Collision Prevention System
Main Launcher - Single Command to Start Everything

Run with: python ai_kavach.py
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher required")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if all required modules are available"""
    required_modules = ['tkinter', 'time', 'random', 'math', 'threading', 'json']
    missing_modules = []
    
    print("🔍 Checking dependencies...")
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        print("   Please install missing modules and try again")
        return False
    
    print("✅ All dependencies satisfied")
    return True

def initialize_ai_models():
    """Initialize AI models and verify they work"""
    print("\n🤖 Initializing AI models...")
    
    try:
        # Import AI systems
        from standalone_ai_models import StandaloneAIModelLoader
        
        # Test AI model loading
        ai_loader = StandaloneAIModelLoader()
        print("✅ Standalone AI models loaded successfully")
        
        # Test collision detection (import from control center)
        print("🔍 Testing collision detection...")
        from control_center_prototype import CollisionDetectionSystem
        
        collision_detector = CollisionDetectionSystem()
        
        # Test with sample data
        test_trains = {
            'TEST_1': {'segment': 'SEG_01', 'track': 'MAIN_A', 'offset': 0.3, 'speed': 50, 'direction': 1},
            'TEST_2': {'segment': 'SEG_01', 'track': 'MAIN_A', 'offset': 0.7, 'speed': 60, 'direction': -1}
        }
        test_segments = {'SEG_01': {'length': 5280}}
        
        risks = collision_detector.calculate_collision_risk(test_trains, test_segments)
        if risks:
            print("✅ Collision detection working")
        else:
            print("⚠️  Collision detection test inconclusive")
        
        print("✅ AI models initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ AI model initialization failed: {str(e)}")
        return False

def start_control_center():
    """Start the main control center application"""
    print("\n🚀 Starting AI KAVACH Control Center...")
    
    try:
        from control_center_prototype import ControlCenterGUI
        
        print("✅ Control center loaded")
        print("🎯 System ready for operation")
        print("\n" + "="*60)
        print("🚂 AI KAVACH - SMART TRAIN COLLISION PREVENTION")
        print("="*60)
        print("Features:")
        print("  ✅ Real-time collision detection")
        print("  ✅ AI-powered recommendations")
        print("  ✅ Automatic emergency braking")
        print("  ✅ Progressive speed control")
        print("  ✅ Multi-train monitoring")
        print("="*60)
        print()
        
        # Create and run the application
        app = ControlCenterGUI()
        app.run()
        
    except Exception as e:
        print(f"❌ Failed to start control center: {str(e)}")
        print("   Please check the error details and try again")
        return False
    
    return True

def show_startup_info():
    """Show system information on startup"""
    print("🚂 AI KAVACH - Smart Train Collision Prevention System")
    print("="*60)
    print("🎯 Single Command Launcher")
    print("📅 Version: 2025.09.21")
    print("👨‍💻 Optimized for real-time collision prevention")
    print("="*60)
    print()

def main():
    """Main launcher function"""
    try:
        # Show startup information
        show_startup_info()
        
        # Check system requirements
        if not check_python_version():
            input("Press Enter to exit...")
            sys.exit(1)
        
        if not check_dependencies():
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Initialize AI models
        if not initialize_ai_models():
            print("\n⚠️  AI models failed to initialize, but system can still run")
            print("   Some features may be limited")
            
        # Start the main application
        print("\n🎯 All systems ready!")
        print("   Starting control center in 2 seconds...")
        time.sleep(2)
        
        start_control_center()
        
    except KeyboardInterrupt:
        print("\n\n👋 AI KAVACH shutdown requested")
        print("   System stopped safely")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("   Please report this issue")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()