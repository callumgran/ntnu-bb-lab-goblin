# 🧌 NTNU BB LAB Goblin

A goblin that crawls NTNU Blackboard and downloads + renames all student submissions so you don’t have to 📥

## Features

* Downloads all pending student submissions for grading.
* Renames files to include the student’s name and lab/assignment number.
* Organizes everything neatly in a local folder.

## Requirements

* Python 3.8+
* Firefox installed
* A copied Firefox profile (see setup below)
* [NTNU Blackboard](https://ntnu.blackboard.com) account with grading access

## Setup

### 1. Copy your Firefox profile

To avoid messing with your daily browser profile, make a copy just for the goblin:

```bash
cp -r ~/.mozilla/firefox/<some-random-id>.default-release ~/.mozilla/firefox/selenium-profile
```

This way, cookies and sessions are reused automatically. If you are already logged in to NTNU Blackboard in that profile, the goblin should work without needing to re-authenticate.

### 2. Install the goblin

Clone the repository and install it as a package:

```bash
git clone https://github.com/callumgran/ntnu-bb-lab-goblin.git
cd ntnu-bb-lab-goblin
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

This will install the CLI command `bb-downloader` globally inside your virtual environment.

### 3. Run the goblin

Now you can simply run:

```bash
bb-downloader --course_id <your_course_id>
```

All downloads will appear in the `bb_downloads/` folder inside the project.

## Optional Flags

The CLI supports several flags to control behavior:

* `--course-id <id>`: NTNU Blackboard course ID (e.g. `_52568_1`).
  Required unless you’ve set a default in `config/settings.py`.

* `--download-dir <path>`: Directory to save downloaded files.
  Default: `./bb_downloads`.

* `--profile <path>`: Path to your copied Firefox profile.
  Default: `~/.mozilla/firefox/selenium-profile`.

* `--lab-num <n>`: Only download submissions for a specific lab/assignment number (`1`, `2`, `3`, …).
  Default: download all labs.

* `--headless`: Run the browser in headless mode (no GUI).
  Useful for running on a server or CI without opening Firefox.

### Example usage

```bash
# Download everything for course _52568_1
bb-downloader --course-id _52568_1

# Download only lab 2 submissions into a custom folder
bb-downloader --course-id _52568_1 --lab-num 2 --download-dir ~/Downloads/inft2503_lab2

# Run in headless mode with a specific Firefox profile
bb-downloader --course-id _52568_1 --profile ~/.mozilla/firefox/selenium-profile --headless
```

## Settings

Instead of passing flags every time, you can configure **default values** in `config/settings.py`:

```python
from pathlib import Path

COURSE_ID = "_52568_1"  # Course ID for INFT2503 (the reason this script exists)
DOWNLOAD_DIR = str(Path.cwd() / "bb_downloads")
FIREFOX_PROFILE = str(Path.home() / ".mozilla/firefox/selenium-profile")
WAIT = 10  # Timeout for Selenium waits in seconds
```

These act as fallbacks if no CLI flag is provided.
For example:

* If you don’t pass `--course-id`, it uses `COURSE_ID` from settings.
* If you don’t pass `--download-dir`, it uses `DOWNLOAD_DIR`.
* If you don’t pass `--profile`, it uses `FIREFOX_PROFILE`.

This way you can tailor the goblin to your workflow once and just run:

```bash
bb-downloader
```

without any flags.

## Course ID

You need to supply the correct `course_id` for the course. This is **not** automatically detected.

For example, if your course outline URL looks like this:

```
https://ntnu.blackboard.com/ultra/courses/_52568_1/cl/outline
```

The `course_id` is:

```
_52568_1
```

You must update the script/config with this value.

## Contributing 🤝

The goblin is still young and only tested on one NTNU Blackboard course so far.
If you want to help improve it, contributions are welcome!

### How to contribute

1. **Fork** the repository on GitHub
2. **Clone** your fork locally and set up a virtual environment:

   ```bash
   git clone https://github.com/<your-username>/ntnu-bb-lab-goblin.git
   cd ntnu-bb-lab-goblin
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```
3. **Create a new branch** for your fix/feature:

   ```bash
   git checkout -b feat|fix|refactor|.../thing-you-did
   ```
4. **Make changes**, Ensure the code is clean. Run formatting & linting (e.g., with `black`, `flake8`, or `ruff`) before committing.
5. **Commit and push** to your fork.
6. **Open a Pull Request** describing your changes.

### What to improve

Some ideas where you could help:

* Broader support for different Blackboard courses (selectors might differ).
* Smarter error handling when downloads fail.
* Cross-browser support (Chrome/Edge).
* General code cleanup and docs.

Even small fixes (typos, better docs, tiny refactors) are very welcome.

## Limitations ⚠️

* Tested only on **one NTNU Blackboard course** so far (INFT2503).
* Blackboard layouts can differ slightly between courses; expect to tweak selectors if it breaks.
* Only Firefox is supported (as that is what I use).
* May need occasional manual login if NTNU/Microsoft SSO session expires.