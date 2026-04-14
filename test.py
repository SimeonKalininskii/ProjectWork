import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import xgboost as xgb
import shap
import matplotlib.ticker as ticker
from sklearn.model_selection import GroupKFold, train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans

df = pd.read_csv('dataframes.csv')
features1 = [col for col in df.columns if col not in ['region', 'year', 'opzh']]
corr_target = df[features1 + ['opzh']].corr()['opzh'].sort_values(ascending=False)
print(corr_target, '\n')

# тепловая карта корреляции между признаками
plt.figure(figsize=(12, 10))
sns.heatmap(df[features1].corr(), annot=True, fmt='.2f', cmap='coolwarm', square=True)
plt.title('Корреляция между признаками')
plt.show()

regions_unique = df['region'].unique()
train_regions, test_regions = train_test_split(regions_unique, test_size=0.2, random_state=42)

train = df[df['region'].isin(train_regions)]
test = df[df['region'].isin(test_regions)]
print("train", train)

x_train = train[features1]
y_train = train['opzh']

x_test = test[features1]
y_test = test['opzh']


average_opzh = df['opzh'].mean()
print(f"Средняя продолжительность жизни:{average_opzh}\n")

def linear_regression():
    # масштабирование
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)
    # region LINEAR REGRESSION
    lr = LinearRegression()
    lr.fit(x_train_scaled, y_train)
    y_pred_lr = lr.predict(x_test_scaled)

    print("Linear Regression:")
    print(f"Средняя ошибка (MAE): {mean_absolute_error(y_test, y_pred_lr):.3f}")
    print(f"Средняя квадратичная ошибка (RMSE): {mean_squared_error(y_test, y_pred_lr):.3f}")
    print(f"R²: {r2_score(y_test, y_pred_lr):.3f}\n")
    # endregion

def random_forest():
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(x_train, y_train)  # без масштабирования
    y_pred_rf = rf.predict(x_test)

    print("Random Forest:")
    print(f"Средняя ошибка (MAE): {mean_absolute_error(y_test, y_pred_rf):.3f}")
    print(f"Средняя квадратичная ошибка (RMSE): {mean_squared_error(y_test, y_pred_rf):.3f}")
    print(f"R²: {r2_score(y_test, y_pred_rf):.3f}\n")

print(train['vrp'].describe(),'\n')

print("x_test min vrp:", x_test['vrp'].min())
print("x_test max vrp:", x_test['vrp'].max())
print("x_test mean vrp:", x_test['vrp'].mean())

def xgboost():
    xgb_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    xgb_model.fit(x_train, y_train)

    y_pred_xgb = xgb_model.predict(x_test)

    print('XGBOOST:')
    print(f"Средняя ошибка (MAE): {mean_absolute_error(y_test, y_pred_xgb):.3f}")
    print(f"Средняя квадратичная ошибка (RMSE): {mean_squared_error(y_test, y_pred_xgb):.3f}")
    print(f"R²: {r2_score(y_test, y_pred_xgb):.3f}\n")
    return xgb_model

# region SHAP
xgb_model = xgboost()
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(x_test)

# График важности признаков
shap.summary_plot(shap_values, x_test, feature_names=features1)

# График зависимости для конкретного признака (например, vrp)
shap.dependence_plot('vrp', shap_values,  x_test, feature_names=features1)
# endregion

top_features = ['vrp', 'living_wage', 'emissions_mass_level']
x_cluster = df.groupby('region')[top_features].mean()
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(x_cluster)
x_cluster['cluster'] = clusters
print(x_cluster.groupby('cluster').mean())
x_cluster[['cluster']].to_excel('regions_cluster.xlsx')
