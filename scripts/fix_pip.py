import sys
import subprocess
import tempfile
import urllib.request
import os

def try_force_reinstall_pip():
    """Try to upgrade and force-reinstall pip via python -m pip."""
    try:
        print("Trying: python -m pip install --upgrade --force-reinstall pip")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", "pip"])
        return True
    except Exception as e:
        print("Force-reinstall failed:", e)
        return False

def try_ensurepip():
    """Try to bootstrap pip using ensurepip (bundled with CPython)."""
    try:
        import ensurepip
        print("Trying: ensurepip.bootstrap(upgrade=True)")
        ensurepip.bootstrap(upgrade=True)
        return True
    except Exception as e:
        print("ensurepip failed:", e)
        return False

def try_get_pip():
    """Download get-pip.py and run it with the active python."""
    url = "https://bootstrap.pypa.io/get-pip.py"
    tmp = None
    try:
        print("Downloading get-pip.py from", url)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        urllib.request.urlretrieve(url, tmp.name)
        print("Running get-pip.py with", sys.executable)
        subprocess.check_call([sys.executable, tmp.name])
        return True
    except Exception as e:
        print("get-pip.py install failed:", e)
        return False
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

def main():
    print("Repairing pip in:", sys.executable)
    if try_force_reinstall_pip():
        print("pip reinstalled via --force-reinstall.")
        return
    if try_ensurepip():
        print("pip installed via ensurepip.")
        return
    if try_get_pip():
        print("pip installed via get-pip.py.")
        return
    print("All methods failed. Try running the script as an administrator or check network/connectivity.")

if __name__ == "__main__":
    main()
