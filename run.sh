#!/bin/bash
cd /home/stock-api
source .env/bin/activate
export PYTHONPATH=$(pwd)
uvicorn app.api:app --host 0.0.0.0 --port 8000
