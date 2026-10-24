import os
import time
import subprocess
from colorama import Fore, init
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import json
import re
from uuid import uuid4
from datetime import datetime
import socket
import webbrowser
import platform

init(autoreset=True)

# Global variable to store the public URL
PUBLIC_URL = ""

PORT = 8080
# Termux path agar exist karta hai to wahi, warna Kali/Linux ke liye home dir
if os.path.isdir("/data/data/com.termux/files/home"):
    WORKDIR = "/data/data/com.termux/files/home/DGTL-Photo-Hide"
else:
    WORKDIR = os.path.expanduser("~/DGTL-Photo-Hide")
DATA_FILE = os.path.join(WORKDIR, "data.json")

os.makedirs(WORKDIR, exist_ok=True)

# --- Banner ---
def print_banner():
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print("\033[1;31m██████╗  ██████╗ ████████╗██╗      \033[1;36m ██╗  ██╗██╗██╗  ██╗███████╗\033[0m")
    print("\033[1;33m██╔══██╗██╔════╝ ╚══██╔══╝██║      \033[1;34m██║  ██║██║██║  ██║██╔════╝\033[0m")
    print("\033[1;32m██║  ██║██║  ███╗   ██║   ██║      \033[1;32m███████║██║██║  ██║█████╗  \033[0m")
    print("\033[1;36m██║  ██║██║   ██║   ██║   ██║      \033[1;35m██╔══██║██║██║  ██║██╔══╝  \033[0m")
    print("\033[1;34m██████╔╝╚██████╔╝   ██║   ███████╗ \033[1;33m██║  ██║██║╚██████╔╝███████╗\033[0m")
    print("\033[1;35m╚═════╝  ╚═════╝    ╚═╝   ╚══════╝ \033[1;31m╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝\033[0m")
    print("\033[1;34m  <========================================================>\033[0m\n")
    print("\033[1;92m         WELCOME To DGTL HIDE\033[1;97m => \033[1;96mCreate by Afridi          \033[0m\n")
    print("\033[1;92m  <========================================================>\033[0m")
    print("\033[1;91m     YouTube bihar\033[1;90m => \033[1;93m https://www.youtube.com/@aryanafridi00\033[0m")
    print("\033[1;92m  <========================================================>\033[0m")
    print("\033[1;95m          Subscribe my YouTube Channel Er.Aryan Afridi\033[0m")
    print("\033[1;34m  <========================================================>\033[0m\n")

# --- Step 1: Tool Lock Message ---
def tool_lock():
    print(Fore.RED + "This tool is locked 🔒")
    print(Fore.YELLOW + "To unlock 🔐, you will be redirected to YouTube in 10 seconds")
    for i in range(10, 0, -1):
        print(Fore.CYAN + f"Redirecting in {i} seconds... ", end="\r")
        time.sleep(1)
    print("\n")

# --- Step 2: Open YouTube App ---
def open_youtube_app():
    try:
        subprocess.run([
            'am', 'start', '-a', 'android.intent.action.VIEW',
            '-d', 'https://www.youtube.com/@aryanafridi00'
        ], check=False)
    except FileNotFoundError:
        # Kali/Linux: default browser me open karo
        webbrowser.open('https://www.youtube.com/@aryanafridi00')

# --- Step 3: Wait for user to return ---
def wait_for_enter():
    input(Fore.GREEN + "\nPress Enter after returning from YouTube...")

# --- Data Management ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# --- Step 4: Ensure HTML files exist (copy from script folder to WORKDIR) ---
def ensure_html_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for fname in ("index.html", "view.html"):
        src = os.path.join(script_dir, fname)
        dst = os.path.join(WORKDIR, fname)
        if os.path.exists(src):
            with open(src, "r", encoding="utf-8") as f:
                content = f.read()
            with open(dst, "w", encoding="utf-8") as f:
                f.write(content)
            print(Fore.GREEN + f"[✓] {fname} loaded")
        else:
            print(Fore.RED + f"[!] {fname} not found in script folder: {script_dir}")
            print(Fore.YELLOW + f"    Please place {fname} next to this script.")

# --- Step 5: Custom HTTP Request Handler ---
class HCORequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKDIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
            try:
                with open(os.path.join(WORKDIR, 'index.html'), 'r', encoding='utf-8') as f:
                    html = f.read()
                
                if PUBLIC_URL:
                    html = html.replace(
                        "const url = window.location.origin + '/view.html?code=' + encodeURIComponent(code);",
                        f"const url = '{PUBLIC_URL}/view.html?code=' + encodeURIComponent(code);"
                    )
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, f"Internal Server Error: {e}")
                return
        
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            code = str(uuid4())
            all_data = load_data()
            
            all_data[code] = {
                'image': data['image'],
                'password': data['password'],
                'timestamp': data.get('timestamp', datetime.now().isoformat())
            }
            
            save_data(all_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'success': True, 'code': code}
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/view':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            all_data = load_data()
            
            if data['code'] in all_data:
                stored_data = all_data[data['code']]
                
                if data['password'] == stored_data['password']:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': True, 'image': stored_data['image']}
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'message': 'Incorrect password'}
                    self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'message': 'Invalid code'}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Not Found")

# --- Step 6: Start HTTP Server with Auto Port Finder ---
def start_server():
    global PORT, PUBLIC_URL
    os.chdir(WORKDIR)
    
    max_attempts = 10
    for i in range(max_attempts):
        try:
            server = HTTPServer(('0.0.0.0', PORT), HCORequestHandler)
            break
        except OSError:
            print(Fore.YELLOW + f"Port {PORT} is busy, trying {PORT+1}...")
            PORT += 1
    else:
        print(Fore.RED + "Could not find an open port. Please close other apps using the port.")
        return

    print(Fore.GREEN + f"Server started at http://localhost:{PORT}")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        network_url = f"http://{local_ip}:{PORT}"
        print(Fore.GREEN + f"Network access: {network_url}")
    except:
        network_url = f"http://localhost:{PORT}"
        print(Fore.YELLOW + "Could not determine network IP, using localhost")
    
    print(Fore.CYAN + "DGTL Photo Hide is now running!")
    
    print(Fore.YELLOW + "\n[!] Generating Public URL via Cloudflare Tunnel...")
    try:
        tunnel_process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{PORT}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        public_url_found = False
        start_time = time.time()
        
        for line in iter(tunnel_process.stdout.readline, ''):
            if not line:
                break
            
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                PUBLIC_URL = match.group(0)
                print(Fore.GREEN + "\n" + "="*60)
                print(Fore.GREEN + "  PUBLIC URL GENERATED SUCCESSFULLY!")
                print(Fore.GREEN + f"  {PUBLIC_URL}")
                print(Fore.GREEN + "="*60 + "\n")
                print(Fore.CYAN + "Share this PUBLIC URL with anyone in the world:")
                print(Fore.CYAN + PUBLIC_URL)
                public_url_found = True
                break
            
            if time.time() - start_time > 20:
                print(Fore.RED + "Timeout: Could not generate public URL.")
                break
        
        if not public_url_found:
            print(Fore.RED + "Failed to get public URL. Make sure 'cloudflared' is installed.")
            print(Fore.YELLOW + "Install it by running: pkg install cloudflared")
            
    except FileNotFoundError:
        print(Fore.RED + "Error: 'cloudflared' is not installed.")
        print(Fore.YELLOW + "Please install it by running: pkg install cloudflared")
    except Exception as e:
        print(Fore.RED + f"Error starting tunnel: {e}")

    try:
        subprocess.run(['am', 'start', '-a', 'android.intent.action.VIEW', '-d', f'http://localhost:{PORT}'], check=False)
    except FileNotFoundError:
        # Kali/Linux: default browser me open karo
        webbrowser.open(f'http://localhost:{PORT}')
    
    server.serve_forever()

# --- Main Execution ---
if __name__ == "__main__":
    print_banner()
    tool_lock()
    open_youtube_app()
    wait_for_enter()
    ensure_html_files()
    
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "\nServer stopped by user")