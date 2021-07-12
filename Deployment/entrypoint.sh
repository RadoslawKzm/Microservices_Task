#!/bin/bash
set -e

uvicorn "$ENV_APP_FOLDER".code_folder.main:app --host 0.0.0.0 --port 8000