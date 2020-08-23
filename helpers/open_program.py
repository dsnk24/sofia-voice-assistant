import subprocess

def open_app(app):
    apps = {
        "sublime": "C:\\Program Files\\Sublime Text 3\\sublime_text.exe",
        "spotify": "C:\\Users\\Eric\\AppData\\Roaming\\Spotify\\Spotify.exe",
        "vscode": "C:\\Users\\Eric\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "discord": "C:\\Users\\Eric\\AppData\\Local\\Discord\\Update.exe",
        "chrome": "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    }

    subprocess.Popen(apps[app])

