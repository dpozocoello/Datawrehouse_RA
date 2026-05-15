"""
Generador de los diagramas faltantes: Cross-Schema y Waste/Chemical detallado.
"""
import os
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


def draw_cross_schema(cur, filename):
    """Diagrama de relaciones cross-schema."""
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
    
    # Count per schema pair
    pair_counts = defaultdict(int)
    pair_examples = defaultdict(list)
    for fk in fks:
        src_s, src_t, src_c, ref_s, ref_t, ref_c = fk
        pair = (src_s, ref_s)
        pair_counts[pair] += 1
        if len(pair_examples[pair]) < 3:
            pair_examples[pair].append(f"{src_t}.{src_c}")
    
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
    
    schema_pos = {
        "suia_iii": (0.2, 0.78),
        "coa_mae": (0.8, 0.78),
        "coa_waste_generator_record": (0.2, 0.22),
        "chemical_pesticides": (0.8, 0.22),
        "public": (0.5, 0.5),
    }
    
    for s, (x, y) in schema_pos.items():
        fc = COLORS.get(s, ("#999", "#eee"))[0]
        box = FancyBboxPatch((x-0.13, y-0.06), 0.26, 0.12,
                              boxstyle="round,pad=0.01", fc=fc, ec='#333', lw=2, alpha=0.85)
        ax.add_patch(box)
        ax.text(x, y+0.015, s, ha='center', va='center',
                fontsize=10 if len(s) < 15 else 7, fontweight='bold', color='white')
        ax.text(x, y-0.025, f"{schema_counts.get(s, 0)} tablas",
                ha='center', va='center', fontsize=9, color='white', alpha=0.9)
    
    seen_pairs = set()
    for pair, count in pair_counts.items():
        src_s, ref_s = pair
        if pair not in seen_pairs and src_s in schema_pos and ref_s in schema_pos:
            seen_pairs.add(pair)
            sx, sy = schema_pos[src_s]
            tx, ty = schema_pos[ref_s]
            
            ax.annotate("", xy=(tx, ty), xytext=(sx, sy),
                        arrowprops=dict(arrowstyle="-|>", color='#333',
                                        lw=2, alpha=0.6,
                                        connectionstyle="arc3,rad=0.15"))
            mid_x = (sx + tx) / 2 + 0.03
            mid_y = (sy + ty) / 2 + 0.03
            ax.text(mid_x, mid_y, f"{count} FKs",
                    fontsize=9, fontweight='bold', color='#333',
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', fc='#FFF9C4', ec='#F57F17', alpha=0.9))
    
    ax.set_title(
        "Diagrama de Relaciones Cross-Schema\n"
        "Base de Datos: suia_enlisy @ 172.16.0.179:5632",
        fontsize=14, fontweight='bold', pad=15)
    
    legend_patches = [mpatches.Patch(color=COLORS[s][0], alpha=0.85, label=s) 
                      for s in schemas + ["public"]]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=10)
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
    
    # Get ALL FKs involving these schemas
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
    
    waste_tables = sorted([k for k in all_info if all_info[k]["schema"] == "coa_waste_generator_record"])
    chem_tables = sorted([k for k in all_info if all_info[k]["schema"] == "chemical_pesticides"])
    
    n_max = max(len(waste_tables), len(chem_tables), 1)
    fig_h = max(14, n_max * 1.6 + 3)
    
    fig, ax = plt.subplots(figsize=(24, fig_h))
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    
    positions = {}
    
    # Waste tables on the left
    spacing_w = 0.9 / max(len(waste_tables), 1)
    for i, full_name in enumerate(waste_tables):
        x = 0.2
        y = 0.95 - i * spacing_w
        positions[full_name] = (x, y)
        
        info = all_info[full_name]
        tname = full_name.split(".")[-1]
        fc, lc = COLORS["coa_waste_generator_record"]
        
        header = FancyBboxPatch((x-0.14, y-0.005), 0.28, 0.018,
                                 boxstyle="round,pad=0.003", fc=fc, ec='#333', lw=1.2, alpha=0.9)
        ax.add_patch(header)
        ax.text(x, y+0.004, tname[:35], ha='center', va='center',
                fontsize=5.5, fontweight='bold', color='white')
        
        n_cols = min(len(info["cols"]), 8)
        body_h = 0.010 * n_cols + 0.004
        body = FancyBboxPatch((x-0.14, y-0.005-body_h), 0.28, body_h,
                               boxstyle="round,pad=0.003", fc=lc, ec='#ccc', lw=0.5, alpha=0.7)
        ax.add_patch(body)
        
        for j, (col_name, dtype) in enumerate(info["cols"][:8]):
            cy = y - 0.012 - j*0.010
            pk_mark = "PK " if col_name in info["pk"] else "   "
            ax.text(x-0.13, cy, f"{pk_mark}{col_name} ({dtype[:10]})",
                    ha='left', va='center', fontsize=3.2, color='#333')
    
    # Chemical tables on the right
    spacing_c = 0.9 / max(len(chem_tables), 1)
    for i, full_name in enumerate(chem_tables):
        x = 0.8
        y = 0.95 - i * spacing_c
        positions[full_name] = (x, y)
        
        info = all_info[full_name]
        tname = full_name.split(".")[-1]
        fc, lc = COLORS["chemical_pesticides"]
        
        header = FancyBboxPatch((x-0.14, y-0.005), 0.28, 0.018,
                                 boxstyle="round,pad=0.003", fc=fc, ec='#333', lw=1.2, alpha=0.9)
        ax.add_patch(header)
        ax.text(x, y+0.004, tname[:35], ha='center', va='center',
                fontsize=5.5, fontweight='bold', color='white')
        
        n_cols = min(len(info["cols"]), 8)
        body_h = 0.010 * n_cols + 0.004
        body = FancyBboxPatch((x-0.14, y-0.005-body_h), 0.28, body_h,
                               boxstyle="round,pad=0.003", fc=lc, ec='#ccc', lw=0.5, alpha=0.7)
        ax.add_patch(body)
        
        for j, (col_name, dtype) in enumerate(info["cols"][:8]):
            cy = y - 0.012 - j*0.010
            pk_mark = "PK " if col_name in info["pk"] else "   "
            ax.text(x-0.13, cy, f"{pk_mark}{col_name} ({dtype[:10]})",
                    ha='left', va='center', fontsize=3.2, color='#333')
    
    # Draw FK arrows for cross-schema relationships
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
                
                is_cross = src_s != ref_s
                color = '#E65100' if is_cross else '#666'
                lw = 1.5 if is_cross else 0.8
                
                ax.annotate("", xy=(tx, ty), xytext=(sx, sy),
                            arrowprops=dict(arrowstyle="->", color=color,
                                            lw=lw, alpha=0.7,
                                            connectionstyle="arc3,rad=0.15"))
                if is_cross:
                    mid_x = (sx + tx) / 2
                    mid_y = (sy + ty) / 2
                    ax.text(mid_x, mid_y, src_c[:15], fontsize=3.5, color='#E65100',
                            ha='center', va='center',
                            bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='#E65100', alpha=0.8))
    
    ax.set_title(
        "Diagrama ER Detallado: Registro Generador de Desechos & Sustancias Quimicas\n"
        "coa_waste_generator_record (izquierda) <-> chemical_pesticides (derecha)\n"
        f"Fuente: suia_enlisy @ 172.16.0.179:5632 | waste: {len(waste_tables)} tablas | chemical: {len(chem_tables)} tablas",
        fontsize=12, fontweight='bold', pad=15)
    
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


def main():
    conn = psycopg2.connect(**CONN)
    cur = conn.cursor()
    print("Conectado a suia_enlisy en 172.16.0.179:5632\n")
    
    print("Generando diagrama cross-schema...")
    draw_cross_schema(cur, os.path.join(OUT, "er_cross_schema.png"))
    
    print("\nGenerando diagrama waste <-> chemical...")
    draw_waste_chem_detail(cur, os.path.join(OUT, "er_waste_chemical_detail.png"))
    
    cur.close()
    conn.close()
    
    print("\n=== TODOS LOS DIAGRAMAS ===")
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".png"):
            fp = os.path.join(OUT, f)
            print(f"  {f} ({os.path.getsize(fp)/1024:.0f} KB)")

if __name__ == "__main__":
    main()
