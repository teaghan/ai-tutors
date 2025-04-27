import os
import subprocess
import multiprocessing
import sys

def run_fastapi():
    """Run the FastAPI server"""
    # When behind Nginx, always use port 8000 for FastAPI
    api_port = 8000
    
    print(f"Starting FastAPI server on port {api_port}")
    from api.app import run_api
    run_api(host="127.0.0.1", port=api_port)

def run_streamlit():
    """Run the Streamlit app"""
    # When behind Nginx, always use port 8501 for Streamlit
    cmd = [
        "streamlit", "run", "main.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.address", "127.0.0.1"  # Only listen on localhost
    ]
    print("Starting Streamlit server on port 8501")
    subprocess.run(cmd)

def run_startup():
    """Run the startup script if it exists"""
    if os.path.exists("startup.py"):
        print("Running startup script")
        subprocess.run([sys.executable, "startup.py"])

if __name__ == "__main__":
    # Start processes
    processes = []
    
    # Run FastAPI in a separate process
    api_process = multiprocessing.Process(target=run_fastapi)
    api_process.start()
    processes.append(api_process)
    
    # Run startup script if available
    if os.path.exists("startup.py"):
        startup_process = multiprocessing.Process(target=run_startup)
        startup_process.start()
        processes.append(startup_process)
    
    # Run Streamlit in the main process
    run_streamlit()
    
    # If we get here (Streamlit exited), terminate other processes
    for p in processes:
        if p.is_alive():
            p.terminate() 