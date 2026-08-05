import os
import json
import matplotlib.pyplot as plt

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

    fig, ax1 = plt.subplots(figsize=(8, 5))

    color = 'tab:blue'
    ax1.set_xlabel('Sample Size (N iterations)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Cumulative Unique Failures Discovered K(N)', color=color, fontsize=12, fontweight='bold')
    ax1.plot(budgets, cumulative_K, marker='o', color=color, linewidth=2.5, label='K(N) Cumulative Failures')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axvline(x=100000, color='red', linestyle='--', linewidth=1.5, label='100k Sampling Limit')

    ax2 = ax1.twinx()  
    color = 'tab:orange'
    ax2.set_ylabel('Discovery Velocity dK/dN', color=color, fontsize=12, fontweight='bold')
    ax2.plot(budgets, velocities, marker='s', color=color, linewidth=2, linestyle=':', label='dK/dN Velocity')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Monte Carlo Discovery Velocity & Failure Mode Saturation (dK/dN)', fontsize=13, fontweight='bold', pad=15)
    fig.tight_layout()

    out_dir = os.path.join("reports", "figures")
    os.makedirs(out_dir, exist_ok=True)
    out_img = os.path.join(out_dir, "discovery_velocity_plateau.png")
    plt.savefig(out_img, dpi=300)
    print(f"Discovery velocity plot saved to: {out_img}")

if __name__ == "__main__":
    main()
