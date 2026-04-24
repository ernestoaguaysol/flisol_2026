```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python sqlite_setup.py
docker compose up -d
python agente.py
```
