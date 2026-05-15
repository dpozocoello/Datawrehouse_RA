import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 'import streamlit as st' in line:
        new_lines.append(line)
        new_lines.append("from auth_utils import login_screen, log_audit, hash_password, validate_password_strength, engine as auth_engine\n")
        new_lines.append("from config_utils import load_config, save_config, apply_custom_theme, save_local_image, get_base64_image, apply_global_frame\n")
        continue
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
