import os
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def main():
    report_file = os.path.join("reports", "summary", "sensitivity_analysis_report.json")
    if not os.path.exists(report_file):
        print(f"Report file not found: {report_file}")
        return

    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dv_summary = data.get("discovery_velocity_summary", {})
    if not dv_summary:
        print("No discovery_velocity_summary found.")
        return

    budgets = [int(b) for b in dv_summary.keys()]
    cumulative_K = [dv_summary[str(b)]["cumulative_failure_modes_K"] for b in budgets]
    velocities = [dv_summary[str(b)]["discovery_velocity_dK_dN"] for b in budgets]

    # Configure publication aesthetic
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#CBD5E0'
    plt.rcParams['axes.linewidth'] = 0.8

    fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax1.set_facecolor('#FAFAFA')

    # Shaded saturation zone
    ax1.axvspan(25000, 100000, color='#EBF8FF', alpha=0.5, label='Saturation Zone (Plateau)')

    # Primary Y-Axis: Cumulative Failure Modes K(N)
    color_k = '#2B6CB0'  # Deep Ocean Blue
    ax1.set_xlabel('Sample Size (N iterations)', fontsize=12, fontweight='bold', labelpad=10, color='#2D3748')
    ax1.set_ylabel('Cumulative Unique Failure Modes K(N)', color=color_k, fontsize=12, fontweight='bold', labelpad=10)
    line1 = ax1.plot(budgets, cumulative_K, marker='o', markersize=6, color=color_k, linewidth=2.5, zorder=4, label='Failure Modes K(N)')
    ax1.tick_params(axis='y', labelcolor=color_k, labelsize=10)
    ax1.tick_params(axis='x', labelsize=10, colors='#2D3748')
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax1.set_ylim(0, max(cumulative_K) * 1.15)
    ax1.grid(True, linestyle='--', alpha=0.4, color='#A0AEC0', zorder=1)

    # 100k Limit Vertical Line
    ax1.axvline(x=100000, color='#E53E3E', linestyle='--', linewidth=1.8, zorder=5, label='100k Sampling Limit')

    # Secondary Y-Axis: Discovery Velocity dK/dN
    ax2 = ax1.twinx()  
    color_v = '#DD6B20'  # Burnt Coral
    ax2.set_ylabel('Discovery Velocity dK/dN', color=color_v, fontsize=12, fontweight='bold', labelpad=10)
    line2 = ax2.plot(budgets, velocities, marker='s', markersize=5, color=color_v, linewidth=2, linestyle=':', zorder=4, label='Discovery Velocity (dK/dN)')
    ax2.tick_params(axis='y', labelcolor=color_v, labelsize=10)
    ax2.set_ylim(-0.01, max(velocities) * 1.15)

    # Callout Annotation for Plateau
    ax1.annotate('Plateau Reached\n(dK/dN → 0.0000)', xy=(100000, cumulative_K[-1]), xytext=(65000, cumulative_K[-1] * 0.70),
                 arrowprops=dict(facecolor='#2B6CB0', shrink=0.08, width=1.5, headwidth=6),
                 fontsize=10, fontweight='bold', color='#1A365D',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#EDF2F7', edgecolor='#CBD5E0', alpha=0.9))

    # Unified Legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E0', fontsize=10)

    plt.title('Monte Carlo Discovery Velocity & Failure Mode Saturation (dK/dN)', fontsize=14, fontweight='bold', pad=15, color='#1A202C')
    fig.tight_layout()

    out_dir = os.path.join("reports", "figures")
    os.makedirs(out_dir, exist_ok=True)
    out_img = os.path.join(out_dir, "discovery_velocity_plateau.png")
    out_pdf = os.path.join(out_dir, "discovery_velocity_plateau.pdf")
    plt.savefig(out_img, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    print(f"Discovery velocity plot saved to: {out_img} and {out_pdf}")

if __name__ == "__main__":
    main()
