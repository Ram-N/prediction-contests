"""Generate a bar plot for the Third Place Race picks."""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

teams =       ['Ghana', 'Scotland', 'Sweden', 'Australia', 'Japan', 'Norway', 'Algeria', 'Czechia', 'Senegal', 'Saudi\nArabia']
picks =       [28,       27,         23,       23,          20,      19,       19,        18,        18,        18]
groups =      ['L',      'C',        'F',      'D',         'F',     'I',      'J',       'A',       'I',       'H']

# Team/national colors
colors = [
    '#FCD116',  # Ghana - gold
    '#003078',  # Scotland - blue
    '#006AA7',  # Sweden - blue
    '#00843D',  # Australia - green/gold -> green
    '#BC002D',  # Japan - red (from flag)
    '#EF2B2D',  # Norway - red
    '#006233',  # Algeria - green
    '#D7141A',  # Czechia - red
    '#00853F',  # Senegal - green
    '#006C35',  # Saudi Arabia - green
]

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(range(len(teams)), picks, color=colors, edgecolor='#333333', linewidth=0.5)

ax.set_yticks(range(len(teams)))
ax.set_yticklabels([f"{t} ({g})" for t, g in zip(teams, groups)], fontsize=12, fontweight='bold')
ax.invert_yaxis()

for bar, pick in zip(bars, picks):
    # Choose text color based on bar darkness
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            str(pick), va='center', fontsize=13, fontweight='bold')

ax.set_xlabel('Number of 3rd Place Picks (out of 51)', fontsize=12)
ax.set_title('The Third Place Race', fontsize=16, fontweight='bold', pad=15)
ax.set_xlim(0, 32)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('/home/ram/projects/prediction-contests/img/soccer/third_place_race.png', dpi=150, bbox_inches='tight')
print("Saved third_place_race.png")
