#!/usr/bin/env bash
# Build script for Render deployment
set -e

# Backend dependencies
pip install -r requirements.txt

# Frontend build
cd ../frontend
npm install
npm run build
cd ../backend

# Seed articles (idempotent — safe to re-run)
python seed_articles.py
