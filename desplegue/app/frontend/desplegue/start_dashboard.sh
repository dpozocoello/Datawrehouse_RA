#!/bin/bash
# start_dashboard.sh - Lanzador para Linux
source .venv/bin/activate
streamlit run app/Dash_board_RG_v1.01.py --server.port 8050 --server.headless true
