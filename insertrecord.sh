#!/usr/bin/env bash
pip install -r requirements.txt -t "$PWD"
export method=insert
python function.py