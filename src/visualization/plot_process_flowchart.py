import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm

def draw_flowchart():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.5, 8.5)
    ax.axis('off')

    def draw_box(x, y, width, height, text, title, color='#E8F0FE', edgecolor='#1A73E8'):
        box = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1", 
                             ec=edgecolor, fc=color, lw=2)
        ax.add_patch(box)
        
        # Add Title
        ax.text(x + width/2, y + height - 0.25, title, ha='center', va='center', 
                fontsize=13, fontweight='bold', color='#202124')
        
        # Add Subtext
        ax.text(x + width/2, y + height/2 - 0.2, text, ha='center', va='center', 
                fontsize=11, color='#3C4043', wrap=True)
        return box

    def draw_arrow(start_x, start_y, end_x, end_y, text="", text_offset_x=0.0, text_offset_y=0.15, ha='center', va='bottom'):
        arrow = FancyArrowPatch((start_x, start_y), (end_x, end_y),
                                arrowstyle='-|>', mutation_scale=20, lw=2, color='#5F6368')
        ax.add_patch(arrow)
        if text:
            ax.text((start_x + end_x)/2 + text_offset_x, (start_y + end_y)/2 + text_offset_y, text, 
                    ha=ha, va=va, fontsize=10, color='#1A73E8', fontweight='bold')

    # Define dimensions
    bw, bh = 2.8, 1.2
    
    # Row 1: Dataset
    draw_box(1, 6, bw, bh, "Load 343 legacy\nprompts", "1. Raw Dataset", '#FCE8E6', '#D93025')
    draw_box(5, 6, bw, bh, "Map fragmented variables\nusing unified mapping", "2. Standardization", '#FCE8E6', '#D93025')
    draw_box(9, 6, bw, bh, "Inject variables & valid\nvalues as @dataclass", "3. Dataclass Injection", '#FCE8E6', '#D93025')
    
    draw_arrow(1 + bw, 6 + bh/2, 5, 6 + bh/2)
    draw_arrow(5 + bw, 6 + bh/2, 9, 6 + bh/2)
    
    # Row 2: Generation
    draw_box(9, 4, bw, bh, "Generate 5 independent\nsamples per prompt", "4. Parallel Generation", '#E8F0FE', '#1A73E8')
    draw_box(5, 4, bw, bh, "Extract valid Python\nsyntax block", "5. Syntax Extraction", '#E8F0FE', '#1A73E8')
    
    draw_arrow(9 + bw/2, 6, 9 + bw/2, 4 + bh, "Query APIs\n(Gemini & Grok)", text_offset_x=0.1, text_offset_y=0, ha='left', va='center')
    draw_arrow(9, 4 + bh/2, 5 + bw, 4 + bh/2)
    
    # Row 3: Testing & Auditing
    draw_box(5, 2, bw, bh, "Detect utilized variables\nvia Regex pattern matching", "6. Regex Parsing", '#E6F4EA', '#1E8E3E')
    draw_box(1, 2, bw, bh, "Cartesian Product of\nall valid inputs", "7. Permutation Gen", '#E6F4EA', '#1E8E3E')
    draw_box(1, 0, bw, bh, "Cap at 100,000 samples\nto prevent explosion", "8. Monte Carlo Cutoff", '#E6F4EA', '#1E8E3E')
    draw_box(5, 0, bw, bh, "Execute code logic against\nevery generated sample", "9. Dynamic Execution", '#E6F4EA', '#1E8E3E')
    
    draw_arrow(5 + bw/2, 4, 5 + bw/2, 2 + bh)
    draw_arrow(5, 2 + bh/2, 1 + bw, 2 + bh/2)
    draw_arrow(1 + bw/2, 2, 1 + bw/2, 0 + bh, "If > 100k", text_offset_x=-0.1, text_offset_y=0, ha='right', va='center')
    draw_arrow(1 + bw, 0 + bh/2, 5, 0 + bh/2)
    
    # Special arrow from 7 to 9 if <= 100k
    draw_arrow(1 + bw, 2 + bh/4, 5, 0 + 3*bh/4, "If <= 100k", text_offset_x=0.0, text_offset_y=0.15, ha='center', va='bottom')

    # Row 4: Classification
    draw_box(9, 0, bw, bh, "Categorize discrepancy:\nProtected vs. Functional", "10. Bias Classification", '#FEF7E0', '#F9AB00')
    
    draw_arrow(5 + bw, 0 + bh/2, 9, 0 + bh/2, "")
    
    # Overall section labels
    ax.text(0.2, 6.6, "DATASET", fontsize=14, fontweight='bold', color='#D93025', rotation=90, va='center')
    ax.text(0.2, 4.6, "GENERATION", fontsize=14, fontweight='bold', color='#1A73E8', rotation=90, va='center')
    ax.text(0.2, 1.6, "AUDITING", fontsize=14, fontweight='bold', color='#1E8E3E', rotation=90, va='center')
    
    plt.tight_layout()
    os.makedirs(os.path.join('reports', 'figures'), exist_ok=True)
    plt.savefig(os.path.join('reports', 'figures', 'EndToEndProcess.png'), dpi=300, bbox_inches='tight')
    print("Flowchart generated successfully!")

if __name__ == '__main__':
    draw_flowchart()
