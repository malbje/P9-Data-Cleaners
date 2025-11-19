# P9-Data-Cleaners
README bruges som et "opslagsværk" til vores struktur for kode. 

--- Generelle guidelines ---

* Vi bruger ikke forkortelser i vores kode - funktioner skal være besrkevet udførligt for at andre gruppemedlemmer kan forstå uden at skulle konsulterer med skribent.

    IN CASE at man laver en forkortelse, skal den beskrives udførligt og tydeligt.

* Øverst i samtlige filer kræves en forklaring af filens funktion og formål
    Se eksempel:
    # -----------------------------
    # This page works with creating and sending notifications based on 
    # 
    # Currently it is printing 3 reminders in the terminal based on the mock data
    # -----------------------------

* Alt ud over vores README foregår på engelsk, thx


* Alle filers navne skal være deskriptive (atomiske) for deres funktion. Heller et langt navn end et forvirende. 


* Vi skal beskrive alle funktioner så de er let forståelige, i samme stilart. 
    Vi bruger google style docstrings som ligner javadoc i python eksempel: 

        def function_name(arg1, arg2):

            """
            Short description of what the function does.

            Args:
                arg1 (type): Description of the first argument.
                arg2 (type): Description of the second argument.

            Returns:
                type: Description of what is returned.

        """

* Når filer referer på tværs, beskriv referencen. Hvor er den, hvad er funktionen? Hvorfor?

## Opsætning og tjek (kort, dansk)

1) Opret og aktivér et virtuelt miljø i projektroden
- PowerShell:
  - python -m venv .venv
  - .venv\Scripts\Activate.ps1
- CMD:
  - python -m venv .venv
  - .venv\Scripts\activate.bat
- macOS / Linux:
  - python3 -m venv .venv
  - source .venv/bin/activate

2) Installer afhængigheder
- Hvis du har requirements.txt:
  - pip install -r requirements.txt
- Eller kun requests:
  - pip install requests

3) Tilføj din DMI API-nøgle lokalt
- Rediger filen `private_settings.py` i projektroden og sæt:
  - DMI_API_KEY = "din_nøgle_her"

4) Kør check-scriptet for at validere miljøet
- python scripts/check_env.py
- Output viser: Python executable, om venv er aktivt, om requests er installeret, og om private_settings + DMI nøgle findes.

5) Kør weather-demo
- python backend/weather.py

6) Fejl og rettelse (hurtigt)
- "requests not installed" -> pip install requests
- "private_settings import error" -> sørg for filen `private_settings.py` ligger i projektroden
- Virtualenv: Sørg for at du aktiverer .venv før du kører kommandoer i terminalen

## Quick PowerShell activation & troubleshooting

Correct activation (PowerShell, run from project root):
- Activate venv:
  & .\.venv\Scripts\Activate.ps1

If you accidentally type "..venv\..." you'll get:
- "& : The module '..venv' could not be loaded" — this is because "..venv" is treated as a module name.
Do NOT use two dots; use the form `.\.venv\...` (dot + backslash).

If ExecutionPolicy blocks the script:
- Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
- & .\.venv\Scripts\Activate.ps1

Quick checks and commands:
- Which Python is active:
  python -c "import sys; print(sys.executable)"
  (Should point to .venv\Scripts\python.exe when venv is active)

- Run the weather demo:
  python backend/weather.py
  or explicitly:
  .\.venv\Scripts\python.exe backend\weather.py

- Install dependencies:
  python -m pip install -r requirements.txt
  or:
  python -m pip install requests

## Troubleshooting: pip upgrade fails with "uninstall-no-record-file" error

If you see an error like:
  error: uninstall-no-record-file
  Cannot uninstall pip None
  The package's contents are unknown: no RECORD file was found for pip.

Do this inside the active virtual environment:

1) Activate your venv (PowerShell):
   .venv\Scripts\Activate.ps1

2) Try a force reinstall of pip:
   python -m pip install --upgrade --force-reinstall pip

3) If that fails, run the included helper script:
   python scripts/fix_pip.py

The helper will attempt three methods in order:
- pip --force-reinstall
- ensurepip.bootstrap()
- download and run get-pip.py

After repair, verify:
  python -m pip --version

--- 

Note (English commands to run):
- python --version
- python -m pip show requests
- python scripts/check_env.py


Error messages:
- Fejl: kunne ikke kontakte serveren ❌: Insufficient funds - der skal tankes op på AI tokens
- En fejl i login: Tjek adgang til AI nøgle i private_settings. "pip install requests"
- Hvis UI'en på frontenden prompter "Request failed", er det sandsynligvis fordi, du ikke har åbnet din My SQL Workbench app på din computer.

---

Imports troubles

1) googleapiclient.discovery won't import?
- pip install google-api-python-client, så vil importen lykkedes.