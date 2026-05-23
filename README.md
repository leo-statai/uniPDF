# uniPDF

> A lightweight desktop app to merge multiple PDF files in any order — no uploads, no cloud, no fees.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

---

## Features

- **Drag-free reordering** — move files up/down with ▲ ▼ buttons before merging
- **Multi-select add** — pick several PDFs at once from the file picker
- **Custom output path** — type a name or browse to any folder
- **100 % local** — nothing leaves your machine; uses only Python stdlib + pypdf
- **Minimal dependencies** — one pip package (`pypdf`)

---

## Preview

```
┌──────────────────────────────────────────────────────┐
│  Arquivos para mesclar (na ordem desejada):          │
│  ┌────────────────────────────────────────────────┐  │
│  │  contrato.pdf                                  │  │
│  │  anexo_1.pdf                                   │  │
│  │  anexo_2.pdf                                   │  │
│  └────────────────────────────────────────────────┘  │
│  [Adicionar]  [Remover]  [▲]  [▼]                    │
│                                                      │
│  Salvar como: [pdfs_agrupados.pdf]  [Escolher…]      │
│                                                      │
│               [  Mesclar PDFs  ]                     │
└──────────────────────────────────────────────────────┘
```

---

## Requirements

| Dependency | Notes |
|---|---|
| Python 3.8+ | |
| `tkinter` | Ships with Python. On Ubuntu/Debian run `sudo apt install python3-tk` if missing |
| `pypdf 6.10.2` | Installed via pip |

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/leo-statai/uniPDF.git
cd uniPDF

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
python merge_pdfs.py
```

| Step | Action |
|---|---|
| 1 | Click **Adicionar** and select one or more PDF files |
| 2 | Use **▲** / **▼** to set the merge order |
| 3 | Select a file and click **Remover** to remove it from the list |
| 4 | Set the output filename/path in the **Salvar como** field |
| 5 | Click **Mesclar PDFs** — a confirmation dialog shows the saved path |

---

## Running the Tests

```bash
source venv/bin/activate
python -m unittest test_merge_pdfs -v
```

The test suite covers:

- `merge_pdfs()` core function — file creation, page count, page order, automatic subdirectory creation
- `App` GUI logic — add, remove, reorder (up/down), output path picker, and input validations

---

## Project Structure

```
uniPDF/
├── merge_pdfs.py       # App entry point (GUI + merge logic)
├── test_merge_pdfs.py  # Unit tests
├── requirements.txt    # pypdf pin
└── README.md
```

---

## Tech Stack

- **[pypdf](https://github.com/py-pdf/pypdf)** — pure-Python PDF reading and writing
- **tkinter** — Python's built-in GUI toolkit (no extra install on most systems)

---

## License

[MIT](LICENSE)
