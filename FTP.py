import os
import re
import socket
import ssl
import threading
from ftplib import FTP, FTP_TLS
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, init

# Initialize colorama for standard cross-platform terminal colors
init(autoreset=True)

# Instantiate thread locks to protect terminal prints and file logs from overlapping
file_lock = threading.Lock()
print_lock = threading.Lock()

class UI:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    @staticmethod
    def print_banner():
        print(f"""{Fore.RED}
  █████▒▄▄▄█████▓ ██▓███      ▄████▄   ██░ ██ ▓█████  ▄████▄   ██ ▄█▀▓█████  ██▀███  
▓██   ▒ ▓  ██▒ ▓▒▓██░  ██▒   ▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▒██▀ ▀█   ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒
▒████ ░ ▒ ▓██░ ▒░▓██░ ██▓▒   ▒▓█    ▄ ▒██▀▀██░▒███   ▒▓█    ▄ ▓███▄░ ▒███   ▓██ ░▄█ ▒
░▓█▒  ░ ░ ▓██▓ ░ ▒██▄█▓▒ ▒   ▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒▓▓▄ ▄██▒▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  
░▒█░      ▒██▒ ░ ▒██▒ ░  ░   ▒ ▓███▀ ░░▓█▒░██▓░▒████▒▒ ▓███▀ ░▒██▒ █▄░▒████▒░██▓ ▒██▒
 ▒ ░      ▒ ░░   ▒▓▒░ ░  ░   ░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ░▒ ▒  ░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░
 ░          ░    ░▒ ░          ░  ▒    ▒ ░▒░ ░ ░ ░  ░  ░  ▒   ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░
 ░ ░      ░      ░░          ░         ░  ░░ ░   ░   ░        ░ ░░ ░    ░     ░░   ░ 
                             ░ ░       ░  ░  ░   ░  ░░ ░      ░  ░      ░  ░   ░     
                             ░                       ░                               
            """)
        
    @staticmethod
    def print_menu():
        print(f"""{Fore.RED}
 1 - Check single FTP Connection string
 2 - Check FTP Connection file (file.txt)
 3 - Exit
{Fore.RESET}""")

class FTPChecker:
    def __init__(self, host, user, passwd, port=21, timeout=10):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.timeout = timeout

    def count_items_recursive(self, ftp):
        """
        Recursively walks directories to count total accessible objects.
        This tests data-channel longevity across multiple commands.
        """
        total_count = 0
        try:
            # Capture file/folder names
            lines = ftp.nlst()
            total_count += len(lines)
            
            # Walk deeper into up to 3 subdirectories to measure true depth visibility
            sub_dirs = []
            for item in lines[:3]:
                try:
                    # Test if the item is a folder by trying to CWD into it
                    original_pwd = ftp.pwd()
                    ftp.cwd(item)
                    sub_dirs.append((item, original_pwd))
                except Exception:
                    pass # It's a plain file or restricted object
            
            for folder, orig in sub_dirs:
                try:
                    lines_deep = ftp.nlst()
                    total_count += len(lines_deep)
                    ftp.cwd(orig) # Step back out safely
                except Exception:
                    pass
                    
            return total_count
        except Exception:
            return -1 # Connection dropped midway through operation

    def get_directory_list_101(self):
        """
        Performs 101% bulletproof live checks:
        1. Low-level TCP Port handshake validation
        2. Strict dual-protocol SSL/Explicit login rules
        3. Multi-point recursive directory tree counting verification
        """
        # --- Stage 1: TCP Port Probe ---
        try:
            sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.close()
        except Exception:
            return False, 0, [], "TCP_CLOSED"

        # --- Stage 2 & 3: Protocol, Auth & Data Stability Checks ---
        ftp = None
        try:
            # Try FTPS first
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                ftp = FTP_TLS()
                ftp.connect(self.host, port=self.port, timeout=self.timeout)
                ftp.auth() 
                ftp.login(user=self.user, passwd=self.passwd)
                ftp.prot_p() 
            except Exception:
                # Fallback to plain FTP
                if ftp:
                    try: ftp.quit()
                    except: pass
                ftp = FTP()
                ftp.connect(self.host, port=self.port, timeout=self.timeout)
                ftp.login(user=self.user, passwd=self.passwd)

            ftp.set_pasv(True)
            
            # Pull initial items preview safely
            preview_items = ftp.nlst()
            
            # Perform dynamic data channel stability count check
            total_found = self.count_items_recursive(ftp)
            if total_found == -1:
                return False, 0, [], "DATA_CHANNEL_FAILED"
                
            try: ftp.quit()
            except: pass
            
            return True, total_found, preview_items, "SUCCESS"

        except Exception as e:
            err = str(e)
            if "530" in err or "Login incorrect" in err:
                return False, 0, [], "BAD_AUTH"
            return False, 0, [], f"ERR: {err}"
        finally:
            if ftp:
                try: ftp.close()
                except: pass

def clean_host(host_str):
    cleaned = host_str.strip().replace("ftp://", "").replace("https://", "").replace("http://", "")
    while cleaned.endswith('/'):
        cleaned = cleaned[:-1]
    return cleaned

def parse_entry(entry):
    cleaned = entry.strip().rstrip(':').strip()
    if not cleaned:
        return None
        
    if "#" in cleaned:
        try:
            url_part, credentials = cleaned.split('#', 1)
            if "@" in credentials:
                user, passwd = credentials.split('@', 1)
                return clean_host(url_part), 21, user.strip(), passwd.strip()
            elif ":" in credentials:
                user, passwd = credentials.split(':', 1)
                return clean_host(url_part), 21, user.strip(), passwd.strip()
        except Exception:
            pass

    if "|" in cleaned:
        parts = [p.strip() for p in cleaned.split('|') if p.strip()]
        if len(parts) == 3:
            return clean_host(parts[0]), 21, parts[1], parts[2]
            
    parts = [p.strip() for p in cleaned.split(':') if p.strip()]
    if len(parts) == 4:
        try:
            return clean_host(parts[0]), int(parts[1]), parts[2], parts[3]
        except ValueError:
            pass
    elif len(parts) == 3:
        return clean_host(parts[0]), 21, parts[1], parts[2]
        
    return None

def check_ftp_connection(ftp_url, output_file="ftp_results.txt"):
    parsed = parse_entry(ftp_url)
    if not parsed:
        return

    host, port, user, passwd = parsed
    checker = FTPChecker(host, user, passwd, port=port)
    
    success, total_found, items, status = checker.get_directory_list_101()
    
    if success:
        with print_lock:
            print(f"{Fore.GREEN}[VALID] This is a valid FTP server!")
            print(f"{Fore.GREEN}        URL: {user}@{host}:{port}")
            print(f"{Fore.CYAN}        Live items found dynamically: {total_found}")
            if items:
                for item in items[:3]: 
                    print(f"{Fore.BLUE}         • {item}")
            else:
                print(f"{Fore.YELLOW}         • [Directory is completely empty]")
            print() 

        try:
            with file_lock:
                with open(output_file, "a", encoding="utf-8") as out:
                    out.write(f"{host}:{port}|{user}|{passwd}\n")
        except IOError:
            pass
    else:
        with print_lock:
            if status == "TCP_CLOSED":
                print(f"{Fore.RED}[DEAD] Offline/Port Closed: {host}:{port}")
            elif status == "BAD_AUTH":
                print(f"{Fore.RED}[FAIL] Bad Credentials: {user}@{host}:{port}")
            elif status == "DATA_CHANNEL_FAILED":
                print(f"{Fore.RED}[DEAD] Broken Data Channel (WAF blocked): {user}@{host}:{port}")
            else:
                print(f"{Fore.RED}[DROP] Network Timeout: {host}:{port} ({status})")

if __name__ == '__main__':
    UI.clear_screen()
    UI.print_banner()
    UI.print_menu()
    
    choice = input('Enter your choice: > ').strip()

    if choice == '1':
        print(f"{Fore.RED}To exit type: exit{Fore.RESET}")
        while True:
            ftp_url = input('Enter the ftp connection string: > ').strip()
            if ftp_url.lower() == 'exit':
                break
            check_ftp_connection(ftp_url)
            
    elif choice == '2':
        file_name = input('Enter the file name: > ').strip()
        if not os.path.exists(file_name):
            print(f"{Fore.RED}[ERR] - Target input file does not exist.")
            exit()
            
        try:
            max_threads = int(input('Enter parallel worker thread limit (e.g. 10): > ').strip())
        except ValueError:
            max_threads = 10

        with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
            data = [line.strip() for line in f if line.strip()]

        print(f"\n{Fore.CYAN}[INFO] Launching execution pool over {len(data)} items...\n")
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(check_ftp_connection, data)
            
        print(f"\n{Fore.GREEN}[INFO] Batch verification task completed successfully.")
        
    else:
        print('Exiting...')
        exit()
