import numpy as np
import pandas as pd
import piecewise_regression
from test_2 import shap_values_xgb
from test_2 import X_test
import matplotlib.pyplot as plt
import seaborn as sns

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
pw_fit = piecewise_regression.Fit(X_feature, shap_values_feature, n_breakpoints=2)
pw_fit.summary()
results2 = pw_fit.get_results()
breakpoints2 = [
    data["estimate"]
    for key, data in results2["estimates"].items()
    for i in range(1, 3) if key == f"breakpoint{i}"
]
print("\nПороги lag_opzh:")
for i, bp in enumerate(sorted(breakpoints2), 1):
    print(f"Порог {i}: {bp:.2f}")
# endregion

# region Сегментированная регрессия и пороги unemployment_rate
X_feature = X_test['unemployment_rate'].values
shap_values_feature = shap_values_xgb[:, 'unemployment_rate'].values
print("\n--- МЕТОД 1: Сегментированная регрессия unemployment_rate ---")
start_breakpoints_unemp = [3.7, 11.5, 15.0, 22.0]
pw_fit = piecewise_regression.Fit(X_feature, shap_values_feature, n_breakpoints=4, start_values=start_breakpoints_unemp)
pw_fit.summary()
results3 = pw_fit.get_results()
breakpoints3 = [
    data["estimate"]
    for key, data in results3["estimates"].items()
    for i in range(1, 5) if key == f"breakpoint{i}"
]
print("\nПороги unemployment_rate:")
for i, bp in enumerate(sorted(breakpoints3), 1):
    print(f"Порог {i}: {bp:.2f}")
# endregion

# region типология регионов
np.random.seed(42)
n_regions = X_test.shape[0]

df_typology = pd.DataFrame({
    'region_name': [f'Регион {i}' for i in range(1, n_regions + 1)],
    'hospital_beds': X_test['hospital_beds'].values,
    'lag_opzh': X_test['lag_opzh'].values,
    'unemployment_rate': X_test['unemployment_rate'].values
})

POROGI = {
    'hospital_beds': [62.15, 131.09],  # Склеили 131 и 135 в один логический барьер избытка
    'lag_opzh': [66.66, 72.21],
    'unemployment_rate': [3.72, 11.92, 28.11]
}

# --- 3. АВТОМАТИЧЕСКАЯ КАТЕГОРИЗАЦИЯ ФАКТОРОВ ---
# Размечаем койки
df_typology['status_hospital_beds'] = pd.cut(
    df_typology['hospital_beds'],
    bins=[-np.inf, POROGI['hospital_beds'][0], POROGI['hospital_beds'][1], np.inf],
    labels=['Дефицит (Высокий SHAP)', 'Линейная норма', 'Избыток (Низкий SHAP)']
)

# Размечаем пространственный лаг
df_typology['status_lag_opzh'] = pd.cut(
    df_typology['lag_opzh'],
    bins=[-np.inf, POROGI['lag_opzh'][0], POROGI['lag_opzh'][1], np.inf],
    labels=['Депрессивное окружение', 'Интенсивный транзит', 'Оптимальный кластер']
)

# Размечаем безработицу
df_typology['status_unemployment'] = pd.cut(
    df_typology['unemployment_rate'],
    bins=[-np.inf, POROGI['unemployment_rate'][0], POROGI['unemployment_rate'][1], POROGI['unemployment_rate'][2], np.inf],
    labels=['Естественный минимум', 'Макроэкономическая норма', 'Критический шок', 'Глубокий кризис']
)


# --- 4. СИНТЕЗ ФИНАЛЬНОЙ ТИПОЛОГИИ РЕГИОНОВ ---
def type_opr(row):
    # Логика группировки на основе синергии ведущих факторов (Summary Plot)

    # 1. Тяжелый социально-экономический кризис, демпфируемый медициной
    if row['status_unemployment'] in ['Критический шок', 'Глубокий кризис'] and row[
        'status_hospital_beds'] == 'Избыток (Низкий SHAP)':
        return 'Тип I: Структурно-кризисные регионы (Избыточная инфраструктура компенсирует рыночные шоки)'

    # 2. Высокое благополучие как внутренней среды, так и внешнего окружения
    elif row['status_lag_opzh'] == 'Оптимальный кластер' and row['status_unemployment'] in ['Естественный минимум',
                                                                                            'Макроэкономическая норма']:
        return 'Тип II: Регионы макроэкономического благополучия (Сильный синергетический эффект среды)'

    # 3. Двойное инфраструктурное и социальное давление (дефицит коек на фоне слабого окружения)
    elif row['status_hospital_beds'] == 'Дефицит (Высокий SHAP)' and row['status_lag_opzh'] == 'Депрессивное окружение':
        return 'Тип III: Инфраструктурно-депрессивные регионы (Зона двойного системного дефицита)'

    # 4. Полная сбалансированность всех макропоказателей
    elif row['status_unemployment'] == 'Макроэкономическая норма' and row['status_hospital_beds'] == 'Линейная норма':
        return 'Тип IV: Сбалансированные стабильные регионы (Медиана устойчивого развития)'

    # 5. Регионы, находящиеся в процессе трансформации или имеющие уникальные сочетания
    else:
        return 'Тип V: Транзитные регионы со смешанным профилем факторов'


df_typology['Финальный_Тип_Региона'] = df_typology.apply(type_opr, axis=1)

# =====================================================================
# 5. ВЫВОД СТАТИСТИКИ ДЛЯ НАУЧНОГО ОТЧЕТА / СТАТЬИ
# =====================================================================
print(f"Всего обработано регионов в выборке: {n_regions}\n")
print("--- СТРУКТУРНОЕ РАСПРЕДЕЛЕНИЕ СУБЪЕКТОВ ПО ТИПАМ ---")
print(df_typology['Финальный_Тип_Региона'].value_counts())

# =====================================================================
# 6. ВИЗУАЛИЗАЦИЯ ИТОГОВОЙ ТИПОЛОГИИ
# =====================================================================
plt.figure(figsize=(12, 6))
sns.countplot(
    data=df_typology,
    y='Финальный_Тип_Региона',
    palette='magma',
    edgecolor='black',
    order=df_typology['Финальный_Тип_Regиона'].value_counts().index if 'Финальный_Тип_Regиона' in df_typology else None
)
plt.title('Комплексная типология регионов по результатам сегментированного SHAP-анализа (Без living_wage)', fontsize=12, pad=15)
plt.xlabel('Количество субъектов РФ в тестовой выборке', fontsize=10)
plt.ylabel('')
plt.grid(axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
# endregion


