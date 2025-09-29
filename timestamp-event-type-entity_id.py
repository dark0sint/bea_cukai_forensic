# In visualize.py (simplified example)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('data/customs_log.csv')

# Create timeline plot
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='timestamp', y='event_count', hue='event_type')
plt.title('Bea Cukai Event Timeline')
plt.xlabel('Timestamp')
plt.ylabel('Event Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('results/timeline.png')
plt.show()
