# 💀 FTP-ShadowProbe
🕶️ Python-based FTP/FTPS security auditing tool with multithreading, authentication analysis, directory enumeration, and connection validation.
<img width="1220" height="599" alt="image" src="https://github.com/user-attachments/assets/51ad3aa7-7912-4ec8-a8f1-566253ea87f3" />

> 🕶️ **ENTER THE SHADOWS. SCAN THE NETWORK.**

🐍 A Python-based FTP security auditing utility designed for authorized infrastructure testing. Features FTP/FTPS connectivity checks, authentication response analysis, directory enumeration, recursive visibility checks, and multithreaded processing.

## 🚀 Key Features

- ⚡ **Multithreading:** Concurrent FTP connection testing using `ThreadPoolExecutor`.
- 🌐 **TCP Port Detection:** Checks whether the target FTP port is reachable.
- 🔐 **FTP Authentication:** Tests supplied credentials against FTP services.
- 🛡️ **FTPS Support:** Attempts explicit FTPS before falling back to plain FTP.
- 🔄 **Protocol Fallback:** Automatically attempts standard FTP if FTPS fails.
- 📂 **Directory Enumeration:** Retrieves accessible directory listings using `NLST`.
- 🌳 **Recursive Directory Checks:** Examines up to three subdirectories for additional visibility.
- 📊 **Live Status Reporting:** Displays connection status, accessible items, and error details.
- ⏱️ **Configurable Timeout:** Controls connection and response waiting time.
- 💾 **Automatic Result Export:** Saves successful connection records to a text file.
- 🎨 **Colored Terminal Interface:** Uses Colorama for readable terminal output.
- 🧵 **Thread-Safe Logging:** Uses locks to protect terminal output and file writes.

## 📂 Supported Input Formats

The tool supports four connection-string formats:

**1. Pipe Format**
```text
HOST|USERNAME|PASSWORD
```

**2. Hash with @ Format**
```text
HOST#USERNAME@PASSWORD
```

**3. Hash with Colon Format**
```text
HOST#USERNAME:PASSWORD
```

**4. Colon Format with Custom Port**
```text
HOST:PORT:USERNAME:PASSWORD
```

**Examples**
```text
ftp.example.com|username|password
ftp.example.com#username@password
ftp.example.com#username:password
ftp.example.com:21:username:password
```

## ⚙️ Requirements

- 🐍 Python 3.8+
- `requests` is not required.
- `colorama`
- Python standard libraries: `ftplib`, `socket`, `ssl`, `threading`

## 📦 Installation

```bash
pip install colorama
```

## 💻 Usage

Run the script:

```bash
python ftp_checker.py
```

### Available Modes

**1️⃣ Single FTP Connection**

Enter an individual FTP connection string and inspect its connectivity and accessible directory listing.

**2️⃣ Batch FTP File Processing**

Load multiple connection strings from a text file and process them using a configurable number of worker threads.

**3️⃣ Exit**

Close the application.

## 📁 Output

```text
ftp_results.txt
```

- ✅ Stores successfully authenticated FTP/FTPS connection records.
- 📂 Includes the host, port, username, and password fields from the input.

## 🔍 Detection Results

| Status | Meaning |
|---|---|
| 🟢 VALID | Authentication and directory listing succeeded |
| 🔴 DEAD | TCP port unavailable or data channel failed |
| ❌ FAIL | Authentication rejected |
| 🟠 DROP | Connection or network error |

## 🛠️ Technical Components

| Component | Technology |
|---|---|
| FTP communication | `ftplib.FTP` |
| Secure FTP | `ftplib.FTP_TLS` |
| TCP connectivity | `socket` |
| SSL/TLS | `ssl` |
| Concurrent execution | `ThreadPoolExecutor` |
| Thread synchronization | `threading.Lock` |
| Terminal colors | `colorama` |

## ⚠️ Disclaimer

This project is intended for authorized FTP/FTPS security auditing, educational purposes, and testing infrastructure you own or have explicit permission to assess.

Do not use this software against systems or credentials without authorization.

**🔒 ETHICAL TESTING. TECHNICAL PRECISION. CYBERSECURITY.**
