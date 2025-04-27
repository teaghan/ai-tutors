web: streamlit run main.py --server.enableCORS false --server.port $PORT --server.headless true & python startup.py & wait
api: uvicorn api.app:app --port $PORT --host 0.0.0.0
