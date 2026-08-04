import os
import sys
import urllib.request
import subprocess
import time
import re

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

EXE_PATH = os.path.join(os.path.dirname(__file__), "cloudflared.exe")

DOWNLOAD_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

def ensure_cloudflared():
    if not os.path.exists(EXE_PATH):
        print("📥 Downloading official Cloudflare Tunnel executable (cloudflared.exe)...")
        try:
            urllib.request.urlretrieve(DOWNLOAD_URL, EXE_PATH)
            print("✅ cloudflared.exe downloaded successfully!")
        except Exception as e:
            print(f"❌ Failed to download cloudflared.exe: {e}")
            sys.exit(1)

def run_app_and_tunnel():
    ensure_cloudflared()
    
    print("\n🚀 Starting Streamlit Dashboard Server on http://localhost:8501...")
    streamlit_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=localhost", "--server.headless=true"],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    time.sleep(3)
    
    print("\n🌐 Starting Cloudflare Tunnel...")
    tunnel_proc = subprocess.Popen(
        [EXE_PATH, "tunnel", "--url", "http://localhost:8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    public_url = None
    print("\n⌛ Waiting for Cloudflare Public Link generation...")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        line = tunnel_proc.stdout.readline()
        if not line:
            break
        print(f"[Cloudflare Log] {line.strip()}")
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if match:
            public_url = match.group(0)
            break
            
    if public_url:
        print("\n" + "="*70)
        print("🎉 YOUR DASHBOARD IS LIVE AND PUBLICLY ACCESSIBLE AT:")
        print(f"🔗 {public_url}")
        print("="*70 + "\n")
    else:
        print("⚠️ Tunnel started. Check logs for trycloudflare link.")
        
    print("📌 Dashboard server & Cloudflare tunnel are active and running in background...")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping server...")
        streamlit_proc.terminate()
        tunnel_proc.terminate()

if __name__ == "__main__":
    run_app_and_tunnel()

