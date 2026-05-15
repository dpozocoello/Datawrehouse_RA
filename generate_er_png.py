"""
Generador de Diagramas ER en formato PNG usando SOLO matplotlib.
Sin dependencia de networkx (incompatible con Python 3.14).
"""
import os
import sys
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from collections import defaultdict
import psycopg2

CONN = {
    "host": "172.16.0.179", "port": 5632,
    "database": "suia_enlisy", "user": "postgres", "password": "postgres",
}
OUT = r"f:\Datawrehouse_RA\diagramas_er"
os.makedirs(OUT, exist_ok=True)

COLORS = {
    "suia_iii": ("#2196F3", "#E3F2FD"),
    "coa_mae": ("#4CAF50", "#E8F5E9"),
    "coa_waste_generator_record": ("#FF9800", "#FFF3E0"),
    "chemical_pesticides": ("#9C27B0", "#F3E5F5"),
    "public": ("#607D8B", "#ECEFF1"),
}


def get_data(cur, schema):
    cur.execute("""
        SELECT t.table_name, count(c.column_name)
        FROM information_schema.tables t
        LEFT JOIN information_schema.columns c ON t.table_name=c.table_name AND t.table_schema=c.table_schema
        WHERE t.table_schema=%s AND t.table_type='BASE TABLE'
        GROUP BY t.table_name ORDER BY t.table_name;
    """, (schema,))
    tables = cur.fetchall()

    cur.execute("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema
        WHERE tc.table_schema=%s AND tc.constraint_type='PRIMARY KEY';
    """, (schema,))
    pks = defaultdict(list)
    for r in cur.fetchall():
        pks[r[0]].append(r[1])

    cur.execute("""
        SELECT tc.table_name, kcu.column_name, ccu.table_schema, ccu.table_name, ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name
        WHERE tc.table_schema=%s AND tc.constraint_type='FOREIGN KEY';
    """, (schema,))
    fks = cur.fetchall()
    
    # Get top columns for important tables (max 8 per table)
    top_cols = {}
    for tname, _ in tables:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema=%s AND table_name=%s
            ORDER BY ordinal_position LIMIT 8;
        """, (schema, tname))
        top_cols[tname] = cur.fetchall()

    return tables, dict(pks), fks, top_cols


def circular_layout(n, cx=0.5, cy=0.5, rx=0.4, ry=0.38):
    coords = {}
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi / 2
        coords[i] = (cx + rx * math.cos(angle), cy + ry * math.sin(angle))
    return coords


def grid_layout(n, cols_per_row=6, cell_w=0.15, cell_h=0.12, x0=0.05, y0=0.92):
    coords = {}
    for i in range(n):
        r = i // cols_per_row
        c = i % cols_per_row
        coords[i] = (x0 + c * cell_w, y0 - r * cell_h)
    return coords


def draw_er_table(ax, x, y, table_name, pk_str, col_count, color_pair, top_cols=None, w=0.13, h_base=0.06):
    """Draw a single table entity box."""
    fc, lc = color_pair
    
    # Header
    header = FancyBboxPatch((x - w/2, y - 0.015), w, 0.03,
                             boxstyle="round,pad=0.003", fc=fc, ec='#333', lw=1.2, alpha=0.9)
    ax.add_patch(header)
    ax.text(x, y, table_name[:28], ha='center', va='center',
            fontsize=5, fontweight='bold', color='white')
    
    # Body with columns
    if top_cols:
        n_rows = min(len(top_cols), 6)
        body_h = 0.015 * n_rows + 0.005
        body = FancyBboxPatch((x - w/2, y - 0.015 - body_h), w, body_h,
                               boxstyle="round,pad=0.003", fc=lc, ec='#999', lw=0.5, alpha=0.8)
        ax.add_patch(body)
        
        for j, (col_name, dtype) in enumerate(top_cols[:6]):
            cy_pos = y - 0.025 - j * 0.015
            is_pk = "PK" if "id" in col_name.lower() and j == 0 else ""
            short_dtype = dtype[:8]
            label = f"{is_pk} {col_name[:18]} ({short_dtype})"
            ax.text(x - w/2 + 0.005, cy_pos, label,
                    ha='left', va='center', fontsize=3.5, color='#333')
    else:
        body = FancyBboxPatch((x - w/2, y - 0.035), w, 0.02,
                               boxstyle="round,pad=0.003", fc=lc, ec='#999', lw=0.5, alpha=0.8)
        ax.add_patch(body)
        ax.text(x, y - 0.025, f"PK: {pk_str[:20]} | {col_count} cols",
                ha='center', va='center', fontsize=3.5, color='#555')


def draw_schema_diagram(schema, tables, pks, fks, top_cols, filename):
    """Draw complete schema ER diagram."""
    n = len(tables)
    if n == 0:
        return
    
    color_pair = COLORS.get(schema, ("#999", "#eee"))
    
    # Layout
    if n <= 20:
        cols_per_row = 5
        cell_w = 0.18
        cell_h = 0.14
    elif n <= 50:
        cols_per_row = 7
        cell_w = 0.13
        cell_h = 0.13
    else:
        cols_per_row = 8
        cell_w = 0.12
        cell_h = 0.11
    
    rows_needed = math.ceil(n / cols_per_row)
    fig_h = max(10, rows_needed * 2.0 + 2)
    fig_w = max(16, cols_per_row * 2.5)
    
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    
    coords = grid_layout(n, cols_per_row, cell_w, cell_h, 0.07, 0.92)
    table_names = [t[0] for t in tables]
    table_positions = {}
    
    for i, (tname, col_count) in enumerate(tables):
        x, y = coords[i]
        pk_str = ",".join(pks.get(tname, ["N/A"]))
        tc = top_cols.get(tname, None)
        draw_er_table(ax, x, y, tname, pk_str, col_count, color_pair, tc, w=cell_w*0.85)
        table_positions[tname] = (x, y)
    
    # Draw FK relationships (arrows)
    seen = set()
    for fk in fks:
        src, src_col, ref_schema, ref_table, ref_col = fk
        if src in table_positions and ref_table in table_positions:
            if ref_schema == schema:
                key = (src, ref_table)
                if key not in seen:
                    seen.add(key)
                    sx, sy = table_positions[src]
                    tx, ty = table_positions[ref_table]
                    ax.annotate("", xy=(tx, ty - 0.02), xytext=(sx, sy - 0.05),
                                arrowprops=dict(arrowstyle="->", color="#666",
                                                lw=0.6, alpha=0.4,
                                                connectionstyle="arc3,rad=0.15"))
    
    ax.set_title(f"Diagrama Entidad-Relacion: {schema}\n"
                 f"Base: suia_enlisy @ 172.16.0.179:5632 | Tablas: {n} | FK: {len(fks)}",
                 fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  -> {filename} ({os.path.getsize(filename)/1024:.0f} KB)")


def draw_waste_chem_detail(cur, filename):
    """Diagrama detallado waste <-> chemical con columnas."""
    schemas = ['coa_waste_generator_record', 'chemical_pesticides']
    
    all_info = {}
    for s in schemas:
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema=%s AND table_type='BASE TABLE' ORDER BY table_name;
        """, (s,))
        tbls = [r[0] for r in cur.fetchall()]
        
        for t in tbls:
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position;
            """, (s, t))
            cols = cur.fetchall()
            
            cur.execute("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name 
                    AND tc.table_schema=kcu.table_schema
                WHERE tc.table_schema=%s AND tc.table_name=%s AND tc.constraint_type='PRIMARY KEY';
            """, (s, t))
            pk = [r[0] for r in cur.fetchall()]
            all_info[f"{s}.{t}"] = {"schema": s, "cols": cols, "pk": pk}
    
    # Get cross-FKs
    cur.execute("""
        SELECT tc.table_schema, tc.table_name, kcu.column_name,
               ccu.table_schema, ccu.table_name, ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
            AND tc.table_schema=kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name
        WHERE tc.constraint_type='FOREIGN KEY'
          AND (tc.table_schema=ANY(%s) OR ccu.table_schema=ANY(%s));
    """, (schemas, schemas))
    fks = cur.fetchall()
    
    # Layout: waste on left, chemical on right
    waste_tables = [k for k in all_info if all_info[k]["schema"] == "coa_waste_generator_record"]
    chem_tables = [k for k in all_info if all_info[k]["schema"] == "chemical_pesticides"]
    
    n_max = max(len(waste_tables), len(chem_tables), 1)
    fig_h = max(14, n_max * 1.4 + 3)
    
    fig, ax = plt.subplots(figsize=(22, fig_h))
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    
    positions = {}
    
    # Waste tables on the left
    for i, full_name in enumerate(waste_tables):
        x = 0.2
        y = 0.95 - i * (0.9 / max(len(waste_tables), 1))
        positions[full_name] = (x, y)
        
        info = all_info[full_name]
        tname = full_name.split(".")[-1]
        fc, lc = COLORS["coa_waste_generator_record"]
        
        header = FancyBboxPatch((x - 0.14, y - 0.005), 0.28, 0.018,
                                 boxstyle="round,pad=0.003", fc=fc, ec='#333', lw=1.2, alpha=0.9)
        ax.add_patch(header)
        ax.text(x, y + 0.004, tname[:35], ha='center', va='center',
                fontsize=5.5, fontweight='bold', color='white')
        
        n_cols = min(len(info["cols"]), 8)
        body_h = 0.012 * n_cols + 0.004
        body = FancyBboxPatch((x - 0.14, y - 0.005 - body_h), 0.28, body_h,
                               boxstyle="round,pad=0.003", fc=lc, ec='#ccc', lw=0.5, alpha=0.7)
        ax.add_patch(body)
        
        for j, (col_name, dtype) in enumerate(info["cols"][:8]):
            cy = y - 0.014 - j * 0.012
            pk_mark = "PK " if col_name in info["pk"] else "   "
            ax.text(x - 0.13, cy, f"{pk_mark}{col_name} ({dtype[:10]})",
                    ha='left', va='center', fontsize=3.5, color='#333')
    
    # Chemical tables on the right
    for i, full_name in enumerate(chem_tables):
        x = 0.8
        y = 0.95 - i * (0.9 / max(len(chem_tables), 1))
        positions[full_name] = (x, y)
        
        info = all_info[full_name]
        tname = full_name.split(".")[-1]
        fc, lc = COLORS["chemical_pesticides"]
        
        header = FancyBboxPatch((x - 0.14, y - 0.005), 0.28, 0.018,
                                 boxstyle="round,pad=0.003", fc=fc, ec='#333', lw=1.2, alpha=0.9)
        ax.add_patch(header)
        ax.text(x, y + 0.004, tname[:35], ha='center', va='center',
                fontsize=5.5, fontweight='bold', color='white')
        
        n_cols = min(len(info["cols"]), 8)
        body_h = 0.012 * n_cols + 0.004
        body = FancyBboxPatch((x - 0.14, y - 0.005 - body_h), 0.28, body_h,
                               boxstyle="round,pad=0.003", fc=lc, ec='#ccc', lw=0.5, alpha=0.7)
        ax.add_patch(body)
        
        for j, (col_name, dtype) in enumerate(info["cols"][:8]):
            cy = y - 0.014 - j * 0.012
            pk_mark = "PK " if col_name in info["pk"] else "   "
            ax.text(x - 0.13, cy, f"{pk_mark}{col_name} ({dtype[:10]})",
                    ha='left', va='center', fontsize=3.5, color='#333')
    
    # Draw FK arrows
    seen = set()
    for fk in fks:
        src_s, src_t, src_c, ref_s, ref_t, ref_c = fk
        src_key = f"{src_s}.{src_t}"
        ref_key = f"{ref_s}.{ref_t}"
        
        if src_key in positions and ref_key in positions:
            edge = (src_key, ref_key)
            if edge not in seen:
                seen.add(edge)
                sx, sy = positions[src_key]
                tx, ty = positions[ref_key]
                ax.annotate("", xy=(tx, ty), xytext=(sx, sy),
                            arrowprops=dict(arrowstyle="->", color="#E65100",
                                            lw=1.5, alpha=0.7,
                                            connectionstyle="arc3,rad=0.2"))
                mid_x = (sx + tx) / 2
                mid_y = (sy + ty) / 2
                ax.text(mid_x, mid_y, src_c[:15], fontsize=4, color='#E65100',
                        ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='#E65100', alpha=0.8))
    
    ax.set_title(
        "Diagrama ER Detallado: Registro Generador de Desechos & Sustancias Quimicas\n"
        "coa_waste_generator_record (izq) <-> chemical_pesticides (der)\n"
        "Base: suia_enlisy @ 172.16.0.179:5632",
        fontsize=13, fontweight='bold', pad=15)
    
    legend_patches = [
        mpatches.Patch(color=COLORS["coa_waste_generator_record"][0], alpha=0.9,
                       label=f"coa_waste_generator_record ({len(waste_tables)} tablas)"),
        mpatches.Patch(color=COLORS["chemical_pesticides"][0], alpha=0.9,
                       label=f"chemical_pesticides ({len(chem_tables)} tablas)"),
    ]
    ax.legend(handles=legend_patches, loc='lower center', fontsize=10, ncol=2)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  -> {filename} ({os.path.getsize(filename)/1024:.0f} KB)")


def draw_cross_schema(cur, filename):
    """Diagrama de relaciones cross-schema entre todos los esquemas."""
    schemas = ["suia_iii", "coa_mae", "coa_waste_generator_record", "chemical_pesticides"]
    
    cur.execute("""
        SELECT tc.table_schema, tc.table_name, kcu.column_name,
               ccu.table_schema, ccu.table_name, ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
            AND tc.table_schema=kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name
        WHERE tc.constraint_type='FOREIGN KEY'
          AND tc.table_schema=ANY(%s)
          AND ccu.table_schema!=tc.table_schema;
    """, (schemas,))
    fks = cur.fetchall()
    
    # Aggregate at schema level
    schema_rels = defaultdict(lambda: defaultdict(list))
    for fk in fks:
        src_s, src_t, src_c, ref_s, ref_t, ref_c = fk
        key = (src_s, ref_s)
        if (src_t, ref_t) not in [(t, r) for t, r, _ in schema_rels[key]]:
            schema_rels[key].setdefault("tables", []).append((src_t, ref_t, src_c))
    
    # Also get table counts per schema
    schema_counts = {}
    for s in schemas + ["public"]:
        cur.execute("""
            SELECT count(*) FROM information_schema.tables
            WHERE table_schema=%s AND table_type='BASE TABLE';
        """, (s,))
        schema_counts[s] = cur.fetchone()[0]
    
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    
    # Position schemas in a layout
    schema_pos = {
        "suia_iii": (0.2, 0.75),
        "coa_mae": (0.8, 0.75),
        "coa_waste_generator_record": (0.2, 0.25),
        "chemical_pesticides": (0.8, 0.25),
        "public": (0.5, 0.5),
    }
    
    # Draw schema boxes
    for s, (x, y) in schema_pos.items():
        fc, lc = COLORS.get(s, ("#999", "#eee"))
        box_w, box_h = 0.25, 0.12
        
        box = FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                              boxstyle="round,pad=0.01", fc=fc, ec='#333', lw=2, alpha=0.85)
        ax.add_patch(box)
        
        ax.text(x, y + 0.015, s, ha='center', va='center',
                fontsize=11, fontweight='bold', color='white')
        ax.text(x, y - 0.02, f"{schema_counts.get(s, 0)} tablas",
                ha='center', va='center', fontsize=9, color='white', alpha=0.9)
    
    # Draw cross-schema FK arrows
    seen_pairs = set()
    for fk in fks:
        src_s, src_t, src_c, ref_s, ref_t, ref_c = fk
        pair = (src_s, ref_s)
        if pair not in seen_pairs and src_s in schema_pos and ref_s in schema_pos:
            seen_pairs.add(pair)
            sx, sy = schema_pos[src_s]
            tx, ty = schema_pos[ref_s]
            
            # Count FKs for this pair
            count = sum(1 for f in fks if f[0] == src_s and f[3] == ref_s)
            
            ax.annotate("", xy=(tx, ty), xytext=(sx, sy),
                        arrowprops=dict(arrowstyle="-|>", color='#333',
                                        lw=2, alpha=0.6,
                                        connectionstyle="arc3,rad=0.15"))
            mid_x = (sx + tx) / 2
            mid_y = (sy + ty) / 2
            ax.text(mid_x, mid_y, f"{count} FKs",
                    fontsize=8, fontweight='bold', color='#333',
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', fc='#FFF9C4', ec='#F57F17', alpha=0.9))
    
    ax.set_title(
        "Diagrama de Relaciones Cross-Schema\n"
        "Base de Datos: suia_enlisy @ 172.16.0.179:5632\n"
        "Esquemas: suia_iii, coa_mae, coa_waste_generator_record, chemical_pesticides",
        fontsize=14, fontweight='bold', pad=15)
    
    legend_patches = [mpatches.Patch(color=COLORS[s][0], alpha=0.85, label=s) 
                      for s in schemas + ["public"]]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  -> {filename} ({os.path.getsize(filename)/1024:.0f} KB)")


def main():
    conn = psycopg2.connect(**CONN)
    cur = conn.cursor()
    print("Conectado a suia_enlisy en 172.16.0.179:5632\n")
    
    for schema in ["suia_iii", "coa_mae", "coa_waste_generator_record", "chemical_pesticides"]:
        print(f"Generando ER para: {schema}")
        tables, pks, fks, top_cols = get_data(cur, schema)
        draw_schema_diagram(schema, tables, pks, fks, top_cols,
                            os.path.join(OUT, f"er_{schema}.png"))
    
    print("\nGenerando diagrama cross-schema...")
    draw_cross_schema(cur, os.path.join(OUT, "er_cross_schema.png"))
    
    print("\nGenerando diagrama waste <-> chemical...")
    draw_waste_chem_detail(cur, os.path.join(OUT, "er_waste_chemical_detail.png"))
    
    cur.close()
    conn.close()
    
    print("\n=== DIAGRAMAS GENERADOS ===")
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".png"):
            fp = os.path.join(OUT, f)
            print(f"  {f} ({os.path.getsize(fp)/1024:.0f} KB)")

if __name__ == "__main__":
    main()
