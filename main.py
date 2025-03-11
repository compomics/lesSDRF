import webview
from streamlit.web import cli as stcli
import sys
import subprocess
import multiprocessing
from typing import Optional, Dict

# TODO def findAvailablePort()

def startStreamlitApp() -> None:
    streamlit_process = subprocess.Popen(["streamlit", "run", "./application/Home.py", "--server.headless=true", "--global.developmentMode=false", "text=True"])

    try:
        print('Webview create window')
        window = webview.create_window("app", "http://localhost:8501/")
        webview.start()
    except:
        print("Something went wrong")
    finally:
        # Ensure the Streamlit process is terminated
        streamlit_process.terminate()

if __name__ == '__main__':
    startStreamlitApp()