import re

with open('integrity_dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
indent_level = 0
in_tab_block = False

for i, line in enumerate(lines):
    # Detect the start of our new show_tab block
    if line.startswith('show_tab') and '=' in line and '(posicion_menu' in line:
        in_tab_block = True
        new_lines.append(line)
        continue
        
    if in_tab_block and line.startswith('if show_tab'):
        new_lines.append(line)
        continue
        
    if in_tab_block and line.startswith('    with (tabs['):
        new_lines.append(line)
        continue

    # If we hit another root level command that is NOT our tab setup, we might be out of the tab block
    # But all the code is meant to be under the `with` statement.
    # The `with` statement is now at 4 spaces. The code inside should be at 8 spaces.
    # The original code inside `with tabX:` was at 4 spaces.
    
    # Let's just indent anything that currently has exactly 4 spaces to 8 spaces, IF we are inside a tab block.
    # Wait, what if it's already 8 spaces? It should become 12.
    # Basically, add 4 spaces to everything until the next root level command (0 spaces).
    
    if in_tab_block:
        if line.strip() == '':
            new_lines.append(line)
        elif not line.startswith(' '):
            # We hit a root level line. We are no longer in the tab block.
            in_tab_block = False
            new_lines.append(line)
        else:
            # Add 4 spaces
            new_lines.append('    ' + line)
    else:
        new_lines.append(line)

with open('integrity_dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
    
print("Indentation fixed.")
