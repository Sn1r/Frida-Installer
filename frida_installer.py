import ppadb
import subprocess
import requests
import time
import os
from bs4 import BeautifulSoup
from ppadb.client import Client as AdbClient
import lzma

# ANSI Colors
RESET = "\033[0m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"


def print_banner():
    print("""
  _____     _     _         ___           _        _ _           
 |  ___| __(_) __| | __ _  |_ _|_ __  ___| |_ __ _| | | ___ _ __ 
 | |_ | '__| |/ _` |/ _` |  | || '_ \/ __| __/ _` | | |/ _ \ '__|
 |  _|| |  | | (_| | (_| |  | || | | \__ \ || (_| | | |  __/ |   
 |_|  |_|  |_|\__,_|\__,_| |___|_| |_|___/\__\__,_|_|_|\___|_|   
                                            
                                            {Sn1r}
    """)
    time.sleep(1)

def connect_to_device():
    print("[~] Checking if devices are connected via ADB...")
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    if len(devices) > 0:
        device = devices[0]
        print(f"{GREEN}[+] Device connected: {device.serial}\n{RESET}")
        return device
    else:
        print(f"{RED}[!] No devices found. Aborting...{RESET}")
        return
    
def get_frida_latest(device):
    url = "https://github.com/frida/frida/releases/latest"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    version = soup.find("h1", class_="d-inline mr-3").text.split()[1]
    cpu_arch = device.shell("getprop ro.product.cpu.abi").strip()
    if "arm64" in cpu_arch:
        cpu_arch = device.shell("getprop ro.product.cpu.abi").strip().split('-')[0]
    return version, cpu_arch

def download_frida_server(version, cpu_arch):
    url = f"https://github.com/frida/frida/releases/download/{version}/frida-server-{version}-android-{cpu_arch}.xz"
    r = requests.get(url, stream=True)
    print("[~] Downloading the latest Frida Server...")
    with open(f"frida-{cpu_arch}-android.xz", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
    print(f"{GREEN}[+] Done. Downloaded at {os.path.join(os.getcwd(), f.name)}\n{RESET}")
    return True

def install_frida_server(cpu_arch):
    try:
        with lzma.open(f"frida-{cpu_arch}-android.xz") as xz_file:
            with open(f"frida-server-{cpu_arch}", "wb") as f:
                for chunk in xz_file:
                    f.write(chunk)
        
        print("[~] Pushing frida-server to the device...")
        adb_push_cmd = ["adb", "push", f"frida-server-{cpu_arch}", "/data/local/tmp/frida-server"]
        subprocess.run(adb_push_cmd, capture_output=True)

        print("[~] Settings permissions for frida-server...")
        adb_chmod_cmd = ["adb", "shell", "chmod", "700", "/data/local/tmp/frida-server"]
        subprocess.run(adb_chmod_cmd, capture_output=True)

        print("[~] Cleaning up the downloads...")
        os.remove(f"frida-server-{cpu_arch}")
        os.remove(f"frida-{cpu_arch}-android.xz")

        print(f"\n{GREEN}[+] Done. Frida server installed at /data/local/tmp/frida-server\n{RESET}")
        return True

    except Exception as e:
        print(f"{RED}[!] Error installing frida-server:\n{e}\n{RESET}")
        return False
        


def main():
    success_statuses = []
    try:
        device = connect_to_device()
        if device:
            version, cpu_arch = get_frida_latest(device)

            if version is None or cpu_arch is None:
                print(f"{RED}[!] Failed to get the latest Frida version and CPU architecture{RESET}")
                success_statuses.append(False)
            else:
                download_success = download_frida_server(version, cpu_arch)
                install_success = install_frida_server(cpu_arch)

                success_statuses.extend([download_success, install_success])
                
                command = ['pip3', 'install', 'frida']
                print("[~] Installing frida...")
                output = subprocess.run(command, text=True, capture_output=True)

                if "Requirement already satisfied" in output.stdout:
                    print(f"{YELLOW}[!] frida is already installed. Checking if upgrade is needed...{RESET}")
                    success_statuses.append(True)
                    command = ['pip3', 'install', 'frida', '--upgrade']
                    output = subprocess.run(command, text=True, capture_output=True)
                
                if output.returncode != 0:
                    print(output.stderr)
                    print(f"{RED}[!] Failed to install frida{RESET}")
                    success_statuses.append(False)
                
                else:
                    print(f"{GREEN}[+] Done. frida is installed\n{RESET}")
                    success_statuses.append(True)
                
                command = ['pip3', 'install', 'frida-tools']
                print("[~] Installing frida-tools...")
                output = subprocess.run(command, text=True, capture_output=True)

                if "Requirement already satisfied" in output.stdout:
                    print(f"{YELLOW}[!] frida-tools is already installed. Checking if upgrade is needed...{RESET}")
                    success_statuses.append(True)
                    command = ['pip3', 'install', 'frida-tools', '--upgrade']
                    output = subprocess.run(command, text=True, capture_output=True)
                
                if output.returncode != 0:
                    print(output.stderr)
                    print(f"{RED}[!] Failed to install frida {RESET}")
                    success_statuses.append(False)

                else:
                    print(f"{GREEN}[+] Done. frida-tools is installed\n{RESET}")
                    success_statuses.append(True)
            
            

    except subprocess.CalledProcessError as e:
        print(f"{RED}[!] Error executing command: {e}{RESET}")
        print(f"{RED}[!] Error output: {e.stderr}{RESET}")
        success_statuses.append(False)

    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
        success_statuses.append(False)
        
    except KeyboardInterrupt:
        print(f"{YELLOW}[!] Keyboard Interrupted{RESET}")
        success_statuses.append(False)
    
    if all(success_statuses):
        print(f"{CYAN}[+] Everything is installed. You're all set to use frida{RESET}")
    else:
        print(f"{RED}[!] Some errors occurred. Installation may not be completed successfully.{RESET}")


if __name__ == '__main__':
    print_banner()
    main()
