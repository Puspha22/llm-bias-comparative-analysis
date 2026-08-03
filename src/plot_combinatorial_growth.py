import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'text.usetex': True,
    'font.family': 'serif',
    'font.serif': ['Computer Modern Roman'],
    'font.size': 18,
    'axes.titlesize': 24,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18
})

attributes = np.arange(1, 11)
# Cartesian search space for n attributes, assuming ~5 values per attribute on average
combinations = 5 ** attributes

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(attributes, combinations, marker='o', linestyle='-', color='red', linewidth=3, markersize=8, label='Cartesian Search Space ($5^n$ avg. values/attr)')

# Limit line
ax.axhline(y=100000, color='black', linestyle='--', linewidth=2, label='Monte Carlo Sampling Limit (100,000)')

# Fill the area above the limit
ax.fill_between(attributes, 100000, combinations, where=(combinations > 100000), color='gray', alpha=0.3)

# Note: No log scale applied here, using linear scale to show exponential hockey stick

ax.set_title('Combinatorial Explosion of Search Space', pad=20)
ax.set_xlabel('Number of Utilized Attributes ($n$)')
ax.set_ylabel('Total Possible Combinations')

ax.set_xticks(np.arange(1, 11, 1))

# Format y-axis with commas for readability
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper left', fontsize=14)

# CREATE INSET PLOT
inset_ax = ax.inset_axes([0.15, 0.30, 0.35, 0.35])
inset_ax.plot(attributes[:7], combinations[:7], marker='o', linestyle='-', color='red', linewidth=2, markersize=5)
inset_ax.axhline(y=100000, color='black', linestyle='--', linewidth=1.5)
inset_ax.set_title('Zoomed: $n=1$ to $7$', fontsize=14)
inset_ax.set_xticks(np.arange(1, 8, 1))
inset_ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
inset_ax.tick_params(axis='both', which='major', labelsize=12)
inset_ax.grid(True, linestyle=':', alpha=0.6)
# Ensure the inset has the right limits to show the 1-7 curve nicely
inset_ax.set_ylim(-1000, 85000)

plt.tight_layout()
plt.savefig('siuethesis/Assets/combinatorial_growth.png', dpi=300, bbox_inches='tight')
print('Saved combinatorial_growth.png with linear scale and inset')
