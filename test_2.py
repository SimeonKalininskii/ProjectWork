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
import geopandas as gpd
import libpysal
import zipfile
import io

# df = pd.read_csv('dataframes.csv')  # путь к вашей таблице
# print(df.info())
# print(df.head())
# print(df.isnull().sum().sum())  # общее количество пропусков, должно быть 0

# zip_path = r"data\rus_adm_gadm_2022_v03.gdb.zip"
# gdf = gpd.read_file(r"C:/Users/semen/Desktop/Похожие работы/rus_adm_gadm_2022_v03.gdb", layer='rus_admbnda_adm1_gadm_2022_v02')
# print("Столбцы атрибутов:", gdf.columns.tolist())
# gdf_names = gdf['ADM1_EN'].unique()
# print(sorted(gdf_names)[:20])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb

# ------------------------------
# 1. Загрузка и подготовка данных
# ------------------------------
df = pd.read_csv('dataframe_v2.csv', index_col=0)
df = df.drop(df.columns[[0,1,2,3,4,5,6,7,8,9,10]], axis=1)
print(df.head(0))
# df = df.reset_index(drop=True)
# df2 = df.to_excel("dataframe_v3.xlsx")
# Удаление строк с пропусками (если есть)
# df = df.dropna().reset_index(drop=True)

# Признаки (исключаем 'region', 'year', целевую переменную 'opzh')
features1 = [col for col in df.columns if col not in ['region', 'year', 'opzh']]

# Корреляция признаков с целевой переменной
corr_target = df[features1 + ['opzh']].corr()['opzh'].sort_values(ascending=False)
print("Корреляция признаков с ожидаемой продолжительностью жизни:\n", corr_target, "\n")

# Тепловая карта корреляции между признаками
plt.figure(figsize=(12, 10))
sns.heatmap(df[features1].corr(), annot=True, fmt='.2f', cmap='coolwarm', square=True)
plt.title('Корреляционная матрица признаков')
plt.show()

# ------------------------------
# 2. Разделение на обучающую и тестовую выборки по регионам
# ------------------------------
regions_unique = df['region'].unique()
train_regions, test_regions = train_test_split(regions_unique, test_size=0.2, random_state=42)

train = df[df['region'].isin(train_regions)]
test = df[df['region'].isin(test_regions)]

X_train = train[features1]
y_train = train['opzh']
X_test = test[features1]
y_test = test['opzh']

print(f"Средняя продолжительность жизни в данных: {df['opzh'].mean():.2f}\n")
print(f"Размер обучения: {X_train.shape}, размер теста: {X_test.shape}\n")

# ------------------------------
# 3. Линейная регрессия (с масштабированием)
# ------------------------------
def linear_regression(X_train, y_train, X_test, y_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    lr = LinearRegression()
    lr.fit(X_train_scaled, y_train)
    y_pred = lr.predict(X_test_scaled)

    print("=== Линейная регрессия ===")
    print(f"MAE : {mean_absolute_error(y_test, y_pred):.3f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.3f}")
    print(f"R²  : {r2_score(y_test, y_pred):.3f}\n")
    return lr, scaler, X_train_scaled, X_test_scaled

# ------------------------------
# 4. Случайный лес (без масштабирования)
# ------------------------------
def random_forest(X_train, y_train, X_test, y_test):
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    print("=== Случайный лес ===")
    print(f"MAE : {mean_absolute_error(y_test, y_pred):.3f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.3f}")
    print(f"R²  : {r2_score(y_test, y_pred):.3f}\n")
    return rf

# ------------------------------
# 5. XGBoost (без масштабирования)
# ------------------------------
def xgboost_model(X_train, y_train, X_test, y_test):
    xgb_reg = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, random_state=42, max_depth=3, min_child_weight=5, subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=2.0)
    xgb_reg.fit(X_train, y_train)
    y_pred = xgb_reg.predict(X_test)

    print("=== XGBoost ===")
    print(f"MAE : {mean_absolute_error(y_test, y_pred):.3f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.3f}")
    print(f"R²  : {r2_score(y_test, y_pred):.3f}\n")
    return xgb_reg

rf_model = random_forest(X_train, y_train, X_test, y_test)
xgb_model = xgboost_model(X_train, y_train, X_test, y_test)
lr_model, scaler, X_train_scaled, X_test_scaled = linear_regression(X_train, y_train, X_test, y_test)



# Для XGBOOST
explainer_xgb = shap.Explainer(xgb_model, X_train)   # TreeExplainer по умолчанию
shap_values_xgb = explainer_xgb(X_test)

# Для линейной регрессии (опционально)
explainer_lr = shap.LinearExplainer(lr_model, X_train_scaled)
shap_values_lr = explainer_lr.shap_values(X_test_scaled)



shap.summary_plot(shap_values_lr, X_test_scaled, feature_names=features1, show=False)
plt.title("SHAP summary plot (XGBoost)", fontsize=14)
plt.tight_layout()
plt.show()

# Для XGBoost используем оригинальный X_test (не масштабированный)
# shap_values_xgb уже содержит объект Explanation, возьмём .values

# 1. Зависимость SHAP от hospital_beds
shap.dependence_plot('hospital_beds',
                     shap_values_xgb.values,
                     X_test,
                     feature_names=features1,
                     interaction_index='auto',
                     show=False)
plt.title("Dependence plot: hospital_beds")
plt.tight_layout()
plt.show()

# 2. lag_opzh
shap.dependence_plot('lag_opzh',
                     shap_values_xgb.values,
                     X_test,
                     feature_names=features1,
                     interaction_index='auto',
                     show=False)
plt.title("Dependence plot: lag_opzh")
plt.tight_layout()
plt.show()

# 3. unemployment_rate
shap.dependence_plot('unemployment_rate',
                     shap_values_xgb.values,
                     X_test,
                     feature_names=features1,
                     interaction_index='auto',
                     show=False)
plt.title("Dependence plot: unemployment_rate")
plt.tight_layout()
plt.show()