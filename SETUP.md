# Seed counter: setup guide

Version 2.5.0. This guide installs the program. How to use it is in `MANUAL.md`.

The commands are for **Windows** (PowerShell or Command Prompt). On Linux, use `/` instead of `\`,
`python3` instead of `python`, and `.venv/bin/python` instead of `.venv\Scripts\python`.

---

## 1. What you need

| | |
|---|---|
| Operating system | Windows 10 or 11, or Linux (macOS should work but is untested) |
| Python | **3.10 to 3.14**. Tested with Python 3.12 and **3.14**. |
| Disk space | About 400 MB for the Python packages, plus room for your images and results |
| Browser | Any current browser (Edge, Chrome, Firefox) for the review page |
| Internet | Only during installation (to download the packages). The program itself runs offline. |

Every package has ready-made files for Windows and Python 3.14, so nothing has to be compiled.

## 2. Check or install Python

Open PowerShell and type:

```
python --version
```

It should print `Python 3.10` or newer, e.g. `Python 3.14.0`.

- If several Python versions are installed, the Windows launcher `py` picks one:
  `py -3.14 --version`. You can then use `py -3.14` wherever this guide says `python`
  (only in step 4; after that the commands use the `.venv` Python).
- If Python is missing, install it from [python.org/downloads](https://www.python.org/downloads/) or your
  company's software portal. In the python.org installer, tick **"Add python.exe to PATH"**.

## 3. Unzip the project

Unzip `seed_project.zip`, for example to `C:\Users\<you>\seed_project`. Then open a terminal **in that folder**:
in File Explorer open the `seed_project` folder, click in the address bar, type `powershell` and press Enter.
All following commands are typed there.

What is in the folder:

| Folder / file | Contents |
|---|---|
| `input_images\` | The TIFF images to count (empty: put your images here, or add them in the review page) |
| `output\` | Results: report, tables, annotated images; `output\review\` holds your review work (empty at first) |
| `ground_truth\` | Hand-annotated images used to check and tune the program (empty at first; `manifest.yaml` is a blank template) |
| `config\default.yaml` | All settings |
| `config\keybindings.yaml` | Keyboard shortcuts of the review page |
| `scripts\` | The programs you start (`review.py`, `run_count.py`, `calibrate.py`, `evaluate.py`) and setup helpers |
| `src\seedcounter\` | The program code |
| `tests\` | Automatic tests |
| `requirements.txt` | The Python packages the program needs |
| `MANUAL.md`, `SETUP.md` | The user manual and this guide |

## 4. Create the virtual environment

A virtual environment is a private folder (`.venv`) for the program's packages, so they do not mix with
other Python software on the computer.

```
python -m venv .venv
```

(With several Python versions: `py -3.14 -m venv .venv`.) This creates the `.venv` folder. There is no need to
"activate" it: the following commands call its Python directly as `.venv\Scripts\python`.

## 5. Install the packages

```
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
```

Always write `-r` before `requirements.txt`, and use `python -m pip` rather than `pip` on its own: this installs
into exactly the Python that will run the program.

What gets installed:

| Package | Used for |
|---|---|
| numpy, scipy | Calculations on images |
| scikit-image, opencv-python-headless | Image processing (seed detection, borders, drawing) |
| tifffile, imagecodecs | Reading TIFF files, including compressed and multi-page ones |
| PyYAML | Reading the settings and shortcut files |
| tqdm | Progress bars in the terminal |
| pytest | The automatic tests |

The review page itself needs nothing extra: it uses Python's built-in web server and works without internet.

## 6. Check the installation

```
.venv\Scripts\python -c "import numpy, scipy, skimage, cv2, tifffile, yaml; print('all packages OK')"
```

It should print `all packages OK`. For a full check, run the automatic tests (about 30 seconds):

```
.venv\Scripts\python -m pytest tests
```

The last line should say `9 passed, 26 skipped`. The skipped tests compare the counts with hand-counted example
images, which are not included; skipping them is normal.

## 7. If your computer blocks programs (Application Control)

Some organisations only allow approved programs to run. Typical messages are *"An Application Control policy
has blocked this file"* or *"This program is blocked by group policy"*. Do not try to get around the policy;
use the options below or ask your IT department.

| What is blocked | What to do |
|---|---|
| `pip.exe` | Use `python -m pip ...` as written above, never `pip ...` on its own. |
| Script files (`.ps1`, `.bat`) | Not needed: every step in this guide is a typed command. Do not "activate" the environment (`Activate.ps1` is a script); call `.venv\Scripts\python` directly. |
| `.venv\Scripts\python.exe` | Skip the virtual environment: install with `python -m pip install --user -r requirements.txt` and start the programs with `python` instead of `.venv\Scripts\python`. |
| The packages' program files (step 6 shows `DLL load failed ... blocked`) | Only IT can fix this: ask them to allow Python 3.10 or newer with the packages in `requirements.txt` (all standard open-source packages from pypi.org), or to provide an approved Python such as Anaconda. |

**Starting by double-click when script files are blocked**: create a Windows shortcut instead of using the
`.bat` file. Right-click the desktop → *New* → *Shortcut*; as location enter
`C:\Users\<you>\seed_project\.venv\Scripts\python.exe scripts\review.py`; then open the shortcut's
*Properties* and set *Start in* to `C:\Users\<you>\seed_project`.

## 8. Optional: setup and start helpers

If your computer allows script files, these do steps 4 and 5 (and the start) for you:

| File | Does |
|---|---|
| `scripts\setup_env.bat` (double-click) or `scripts\setup_env.ps1` | Creates `.venv` and installs the packages (Windows) |
| `scripts/setup_env.sh` | The same on Linux: `bash scripts/setup_env.sh` |
| `scripts\start_review.bat` (double-click) / `scripts/start_review.sh` | Starts the review page |

Files downloaded from the internet may be marked as unsafe by Windows; if a `.bat` file does nothing, right-click it →
*Properties* → tick *Unblock*, or use the typed commands.

## 9. Start the review page

From the `seed_project` folder:

```
.venv\Scripts\python scripts\review.py
```

The first start analyses all images in `input_images\` (about a second per image); if the folder is empty, the
page opens ready for *Add images*. Then your browser opens
**http://localhost:8000** (if not, type that address yourself). Stop the program with **Ctrl+C** in the terminal;
your work is saved as you go. How to use the page is described in `MANUAL.md`.
