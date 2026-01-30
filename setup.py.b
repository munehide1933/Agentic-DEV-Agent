#!/usr/bin/env python3
"""
一键安装脚本 - Meta-Agent Development System
支持 Windows 和 Linux
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None, shell=False):
    """执行命令"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python():
    """检查Python版本"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ is required, but found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_node():
    """检查Node.js"""
    print("Checking Node.js...")
    success, output = run_command(["node", "--version"])
    if not success:
        print("❌ Node.js is not installed")
        print("Please install from: https://nodejs.org/")
        return False
    print(f"✅ Node.js {output.strip()}")
    return True

def setup_backend():
    """设置后端"""
    print("\n📦 Setting up backend...")
    
    backend_dir = Path("backend")
    venv_dir = backend_dir / "venv"
    
    # 创建虚拟环境
    if not venv_dir.exists():
        print("Creating virtual environment...")
        if platform.system() == "Windows":
            success, _ = run_command(["python", "-m", "venv", "venv"], cwd=backend_dir)
        else:
            success, _ = run_command(["python3", "-m", "venv", "venv"], cwd=backend_dir)
        
        if not success:
            print("❌ Failed to create virtual environment")
            return False
    
    # 激活虚拟环境并安装依赖
    print("Installing Python dependencies...")
    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"
    
    success, _ = run_command(
        [str(pip_path), "install", "-r", "requirements.txt"],
        cwd=backend_dir
    )
    
    if not success:
        print("❌ Failed to install Python dependencies")
        return False
    
    print("✅ Backend setup complete")
    return True

def setup_frontend():
    """设置前端"""
    print("\n📦 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    
    print("Installing Node.js dependencies...")
    success, _ = run_command(["npm", "install"], cwd=frontend_dir)
    
    if not success:
        print("❌ Failed to install Node.js dependencies")
        return False
    
    print("✅ Frontend setup complete")
    return True

def setup_env():
    """设置环境变量文件"""
    print("\n📝 Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path("backend/.env.example")
    
    if not env_file.exists():
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Created .env from template")
            print("\n⚠️  IMPORTANT: Please edit .env and add your Azure OpenAI credentials!")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def create_directories():
    """创建必要的目录"""
    print("\n📁 Creating data directories...")
    
    directories = [
        "data/qdrant",
        "data/sqlite",
        "data/uploads"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Data directories created")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("Meta-Agent Development System - Setup")
    print("=" * 50)
    print()
    
    # 检查前置条件
    if not check_python():
        return 1
    
    if not check_node():
        return 1
    
    # 设置环境
    if not setup_env():
        return 1
    
    # 创建目录
    if not create_directories():
        return 1
    
    # 设置后端
    if not setup_backend():
        return 1
    
    # 设置前端
    if not setup_frontend():
        return 1
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Edit .env file with your Azure OpenAI credentials")
    print("2. Run the application:")
    if platform.system() == "Windows":
        print("   - Windows: run_windows.bat")
    else:
        print("   - Linux: ./run_linux.sh")
    print()
    print("Backend will be available at: http://localhost:8000")
    print("Frontend will be available at: http://localhost:5173")
    print("API Documentation: http://localhost:8000/docs")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())