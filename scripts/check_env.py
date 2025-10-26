import sys
import os
import importlib.util

def in_virtualenv() -> bool:
    """Return True if running inside a virtual environment (.venv or VIRTUAL_ENV)."""
    if os.environ.get("VIRTUAL_ENV"):
        return True
    exe = sys.executable.lower()
    return (".venv" in exe) or (os.path.sep + "venv" + os.path.sep in exe)

def module_installed(name: str):
    """Return version string if module is installed, else None."""
    spec = importlib.util.find_spec(name)
    if not spec:
        return None
    try:
        mod = importlib.import_module(name)
        return getattr(mod, "__version__", str(mod))
    except Exception:
        return "installed"

def check_private_settings():
    """Check for private_settings and DMI_API_KEY."""
    try:
        # ensure project root is on path if script is executed from repo root
        proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if proj_root not in sys.path:
            sys.path.insert(0, proj_root)
        import private_settings  # type: ignore
        key = getattr(private_settings, "DMI_API_KEY", None)
        return True, bool(key)
    except Exception:
        return False, False

def main():
    print("Environment check")
    print("-----------------")
    print("Python executable:", sys.executable)
    print("Python version:   ", sys.version.splitlines()[0])
    print("Virtualenv active:", in_virtualenv())
    req_ver = module_installed("requests")
    print("requests installed:", bool(req_ver), ("("+str(req_ver)+")") if req_ver else "")
    ps_exists, dmi_present = check_private_settings()
    print("private_settings importable:", ps_exists)
    print("DMI_API_KEY present in private_settings:", dmi_present)
    print()
    print("Quick actions:")
    print(" - If virtualenv not active: create + activate one in project root (PowerShell):")
    print("     python -m venv .venv")
    print("     .venv\\Scripts\\Activate.ps1")
    print(" - Install deps:")
    print("     pip install -r requirements.txt")
    print(" - Run this check again:")
    print("     python scripts/check_env.py")
    print()
    if not in_virtualenv() or not req_ver or not ps_exists:
        print("Status: NOT READY — follow the quick actions above.")
        sys.exit(1)
    print("Status: READY")

if __name__ == "__main__":
    main()
