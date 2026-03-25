import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


df = pd.read_csv('dataframes.csv')
features = ['opzh', 'vrp', 'real_wage_index', 'unemployment_rate', 'living_wage', 'capture_mass_level', 'emissions_mass_level']
corr = df[features].corr()

# тепловая карта
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', square=True, linewidths=0.5)
plt.title("Factor's correlation matrix")
plt.tight_layout()
plt.show()

