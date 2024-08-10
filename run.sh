#!/bin/bash
export DEBUG=1
uvicorn src.app:app --reload --port 5101
