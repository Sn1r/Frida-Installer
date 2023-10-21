![image](https://github.com/Sn1r/Frida-Installer/assets/71400526/e0e1788f-f652-4118-943e-74a60d4381d7)

Frida Installer is a Python script that automates the installation of [Frida](https://frida.re/), a powerful dynamic instrumentation toolkit, along with its essential tools. It's designed to simplify and speed up the process of setting up Frida on your host and Android device.

## Features

- Automatically detects the connected Android device's CPU architecture
- Downloads the latest compatible Frida server
- Installs `frida` and `frida-tools` via pip

## Requirements

Before using the script, ensure the following requirements are met:

1. ADB installed and added to the system's PATH
2. An Android device connected to the host via USB or Wi-Fi
3. You have a stable internet connectivity

## Installation & Usage

Install requirements

```bash
pip3 install -r requirements.txt
```

Run the script

```bash
python3 frida_installer.py
```

## Notes

- The script uses ADB to communicate with the Android device, so make sure ADB is properly configured and the device is authorized for debugging
- The installation process may take a few seconds, depending on your internet speed and the device's CPU architecture
