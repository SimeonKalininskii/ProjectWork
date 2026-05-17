import numpy as np
import pandas as pd
import piecewise_regression
from sklearn.tree import DecisionTreeRegressor, export_text
from test_2 import shap_values_xgb
from test_2 import df
from test_2 import X_test

# region Сегментированная регрессия и пороги hospital_beds
X_feature = X_test['hospital_beds'].values
shap_values_feature = shap_values_xgb[:, 'hospital_beds'].values

print("\n--- МЕТОД 1: Сегментированная регрессия hospital_beds ---")
pw_fit = piecewise_regression.Fit(X_feature, shap_values_feature, n_breakpoints=3)
pw_fit.summary()
results = pw_fit.get_results()
breakpoints = [
    data["estimate"]
    for key, data in results["estimates"].items()
    for i in range(1, 4) if key == f"breakpoint{i}"
]
print("\nПороги hospital_beds:")
for i, bp in enumerate(sorted(breakpoints), 1):
    print(f"Порог {i}: {bp:.2f}")
# endregion

# region Сегментированная регрессия и пороги lag_opzh
X_feature = X_test['lag_opzh'].values
shap_values_feature = shap_values_xgb[:, 'lag_opzh'].values
print("\n--- МЕТОД 1: Сегментированная регрессия lag_opzh ---")
pw_fit = piecewise_regression.Fit(X_feature, shap_values_feature, n_breakpoints=3)
pw_fit.summary()
results2 = pw_fit.get_results()
breakpoints2 = [
    data["estimate"]
    for key, data in results2["estimates"].items()
    for i in range(1, 4) if key == f"breakpoint{i}"
]
print("\nПороги lag_opzh:")
for i, bp in enumerate(sorted(breakpoints2), 1):
    print(f"Порог {i}: {bp:.2f}")
# endregion

# region Сегментированная регрессия и пороги unemployment_rate
X_feature = X_test['unemployment_rate'].values
shap_values_feature = shap_values_xgb[:, 'unemployment_rate'].values
print("\n--- МЕТОД 1: Сегментированная регрессия unemployment_rate ---")
pw_fit = piecewise_regression.Fit(X_feature, shap_values_feature, n_breakpoints=3)
pw_fit.summary()
results3 = pw_fit.get_results()
breakpoints3 = [
    data["estimate"]
    for key, data in results3["estimates"].items()
    for i in range(1, 4) if key == f"breakpoint{i}"
]
print("\nПороги unemployment_rate:")
for i, bp in enumerate(sorted(breakpoints3), 1):
    print(f"Порог {i}: {bp:.2f}")
# endregion



