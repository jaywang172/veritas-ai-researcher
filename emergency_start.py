#!/usr/bin/env python3
"""
Veritas 緊急啟動腳本 - 修復網頁打不開的問題
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def check_dependencies():
    """檢查基本依賴"""
    try:
        import fastapi
        import uvicorn
        import crewai
        print("✅ 基本依賴檢查通過")
        return True
    except ImportError as e:
        print(f"❌ 缺少依賴: {e}")
        return False

def check_api_keys():
    """檢查API配置"""
    from dotenv import load_dotenv
    load_dotenv()

    openai_key = os.getenv('OPENAI_API_KEY', '')
    if openai_key and openai_key != 'your_openai_api_key_here':
        print("✅ OpenAI API Key 已配置")
        return True
    else:
        print("❌ OpenAI API Key 未配置")
        return False

def kill_existing_processes():
    """終止可能存在的舊進程"""
    try:
        # 使用 lsof 查找佔用 8000 端口的進程
        result = subprocess.run(['lsof', '-ti:8000'],
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    subprocess.run(['kill', pid], check=False)
                    print(f"✅ 終止舊進程 PID: {pid}")
                except:
                    pass
        time.sleep(2)  # 等待進程完全終止
    except Exception as e:
        print(f"清理舊進程時遇到問題: {e}")

def start_api_server():
    """啟動API服務器"""
    print("🚀 啟動 Veritas API 服務器...")

    try:
        # 使用 subprocess 啟動服務器
        process = subprocess.Popen([
            sys.executable, "-c",
            """
import uvicorn
import sys
sys.path.append('.')
from api_server import app
uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
"""
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 等待服務器啟動
        print("等待服務器啟動...")
        time.sleep(5)

        # 檢查進程是否還在運行
        if process.poll() is None:
            print("✅ API 服務器啟動成功")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 服務器啟動失敗")
            if stderr:
                print(f"錯誤信息: {stderr.decode()}")
            return None

    except Exception as e:
        print(f"❌ 啟動服務器時發生錯誤: {e}")
        return None

def open_browser():
    """打開瀏覽器"""
    try:
        webbrowser.open('http://localhost:8000')
        print("✅ 瀏覽器已打開: http://localhost:8000")
        return True
    except Exception as e:
        print(f"⚠️ 無法自動打開瀏覽器: {e}")
        print("請手動打開: http://localhost:8000")
        return False

def main():
    print("🔧 Veritas 緊急修復啟動")
    print("=" * 50)

    # 檢查工作目錄
    if not Path("api_server.py").exists():
        print("❌ 請確認在正確的項目目錄中運行此腳本")
        sys.exit(1)

    # 檢查依賴
    if not check_dependencies():
        print("請運行: pip install -r requirements.txt")
        sys.exit(1)

    # 檢查API配置
    if not check_api_keys():
        print("請運行: python setup_api_keys.py")
        sys.exit(1)

    # 清理舊進程
    print("🧹 清理舊進程...")
    kill_existing_processes()

    # 啟動服務器
    server_process = start_api_server()
    if not server_process:
        print("❌ 無法啟動服務器，請檢查錯誤信息")
        sys.exit(1)

    # 打開瀏覽器
    open_browser()

    print("\n" + "=" * 50)
    print("🎉 Veritas 系統已啟動！")
    print("=" * 50)
    print("📱 前端界面: http://localhost:8000")
    print("📚 API 文檔: http://localhost:8000/docs")
    print("🛑 按 Ctrl+C 停止服務器")
    print("=" * 50)

    try:
        # 保持腳本運行，等待用戶中斷
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服務器...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("✅ 服務器已停止")

if __name__ == "__main__":
    main()
