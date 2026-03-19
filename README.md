# CSR Generator GUI

A lightweight desktop application to generate **RSA Private Keys** and **Certificate Signing Requests (CSRs)** through a clean graphical interface — no command-line knowledge required.

Built with Python, Tkinter, and the PyCA `cryptography` library.

---

## What it does

- Accepts identity details (domain, organisation, country, state, city) through a form
- Generates a **2048-bit RSA private key** and a **PKCS #10 compliant CSR** instantly
- Displays both outputs in the Summary section with masked private key by default
- Lets you **copy** or **download** the `.csr` and `.key` files directly to the project folder
- Validates all inputs before processing — empty fields and invalid country codes are caught early

---

## Project Structure

```
csr/
├── main.py            # Entry point — launches the app
├── gui.py             # GUI window, layout, and all user interactions
├── csr_generator.py   # RSA key generation and CSR creation logic
├── utils.py           # File save helper
├── requirements.txt   # Python dependencies
└── README.md
```

Generated files (after clicking Download):
```
csr/
├── request.csr        # Certificate Signing Request — submit this to a CA
└── private.key        # RSA Private Key — keep this secret, never share it
```

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.8 or higher |
| cryptography (PyCA) | Latest via pip |
| Tkinter | Bundled with Python (Linux needs separate install) |

---

## Setup and Installation

### Step 1 — Clone or download the project

```bash
git clone https://github.com/gparthiv/csr-generator-gui.git
cd csr-generator-gui
```

Or download the ZIP and extract it, then open a terminal inside the folder.

### Step 2 — Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies

```bash
pip install cryptography
```

### Step 4 — Install Tkinter (Linux only)

On Windows and macOS, Tkinter is bundled with Python. On Linux (Ubuntu/Debian) run:

```bash
sudo apt install python3-tk -y
```

### Step 5 — Run the application

```bash
python3 main.py
```

A window will open centered on your screen.

---

## How to Use

1. Fill in all five fields in the **Certificate Details** form:

   | Field | Description | Example |
   |---|---|---|
   | Common Name | Domain you want to secure | `example.com` |
   | Organisation | Legal name of your entity | `Acme Pvt Ltd` |
   | Country | ISO 3166-1 alpha-2 code (2 letters only) | `IN` |
   | State / Province | Full state name | `West Bengal` |
   | City / Locality | City of your organisation | `Kolkata` |

2. Click **Generate CSR** — the Summary section will populate automatically.

3. In the **Summary** section:
   - View the generated CSR in the text box
   - Private key is masked (`•••`) by default — click **Show** to reveal, **Hide** to mask again
   - Click **Copy** to copy either output to clipboard
   - Click **Download .csr** or **Download .key** to save files to the project folder

4. The status bar at the bottom confirms the exact file path after each download.

---

## Security Notes

- The private key is **generated and stored locally only** — it is never transmitted over any network
- The private key is hidden by default in the UI to prevent accidental exposure
- The `.key` file should be kept in a secure location — do not commit it to version control
- Add `*.key` and `*.csr` to your `.gitignore` if pushing to a repository

```
# .gitignore
private.key
request.csr
```

---

## Cryptographic Specification

| Property | Value |
|---|---|
| Algorithm | RSA (Rivest-Shamir-Adleman) |
| Key size | 2048 bits |
| Public exponent | 65537 |
| Signing hash | SHA-256 |
| CSR standard | PKCS #10 |
| Output encoding | PEM (Base64) |

The generated `.csr` file is compatible with all major Certificate Authorities including Let's Encrypt, DigiCert, and Sectigo.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'tkinter'`**
→ Run `sudo apt install python3-tk -y` (Linux only)

**`ModuleNotFoundError: No module named 'cryptography'`**
→ Run `pip install cryptography` inside your activated virtual environment

**Country field warning even after filling**
→ Country must be exactly 2 letters (e.g. `IN`, `US`, `GB`) — no more, no less

**Files not appearing after download**
→ Check the project folder (`csr/`) — files save there, not to Downloads

**Window too small / content cut off**
→ The window is resizable — drag the bottom edge to expand, or use the scroll wheel

---

## License

This project is submitted as an academic mini project. For educational use only.