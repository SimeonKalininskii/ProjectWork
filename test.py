import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from sklearn.model_selection import GroupKFold, train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv('dataframes.csv')
features1 = [col for col in df.columns if col not in ['region', 'year', 'opzh']]
corr_target = df[features1 + ['opzh']].corr()['opzh'].sort_values(ascending=False)
print(corr_target, '\n')

# тепловая карта
plt.figure(figsize=(12, 10))
sns.heatmap(df[features1].corr(), annot=True, fmt='.2f', cmap='coolwarm', square=True)
plt.title('Корреляция между признаками')
plt.show()

regions_unique = df['region'].unique()
train_regions, test_regions = train_test_split(regions_unique, test_size=0.2, random_state=42)

train = df[df['region'].isin(train_regions)]
test = df[df['region'].isin(test_regions)]

x_train = train[features1]
y_train = train['opzh']
x_test = test[features1]
y_test = test['opzh']

scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)

# region LINEAR REGRESSION
lr = LinearRegression()
lr.fit(x_train_scaled, y_train)
y_pred_lr = lr.predict(x_test_scaled)

print("Linear Regression:")
print(f"MAE: {mean_absolute_error(y_test, y_pred_lr):.3f}")
print(f"R²: {r2_score(y_test, y_pred_lr):.3f}\n")
# endregion

# region RANDOM FOREST
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(x_train, y_train)  # без масштабирования
y_pred_rf = rf.predict(x_test)

print("Random Forest:")
print(f"MAE: {mean_absolute_error(y_test, y_pred_rf):.3f}")
print(f"R²: {r2_score(y_test, y_pred_rf):.3f}\n")
# endregion RANDOM FOREST

# region XGBOOST

xgb_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
xgb_model.fit(x_train, y_train)

y_pred_xgb = xgb_model.predict(x_test)

print('XGBOOST:')
print(f"MAE: {mean_absolute_error(y_test, y_pred_xgb):.3f}")
print(f"R²: {r2_score(y_test, y_pred_xgb):.3f}")

# endregion