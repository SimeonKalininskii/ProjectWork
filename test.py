import pandas as pd
import numpy as np

# region ОПЖ Предобработка данных
df_life_expectancy = pd.read_excel(r'data\ОПЖ всех регионов.xlsx', index_col=0, header=0)

# удаление агрегированных строк
exclude_patterns = ['федеральный округ', 'Российская Федерация', 'в том числе: Ханты-Мансийский автономный округ - Югра', 'Ямало-Ненецкий автономный округ', 'в том числе Ненецкий автономный округ']
mask = ~df_life_expectancy.index.str.contains('|'.join(exclude_patterns), case=False, na=False)
df_regions = df_life_expectancy[mask].copy()

#Сброс индексов и колонок
df_regions.reset_index(inplace=True)
df_regions.rename(columns={'index': 'region'}, inplace=True)

# Преобразование годы из столбцов в строки
df_long = df_regions.melt(id_vars=['region'], var_name='year', value_name='opzh')

# Преобразование года в числовой формат
df_long['year'] = pd.to_numeric(df_long['year'])

# Линейная интерполяция ставропольского края за 2013 год, данных не было
stav_2012 = df_long.loc[(df_long['region'] == 'Ставропольский край') & (df_long['year'] == 2012), 'opzh'].item()
stav_2014 = df_long.loc[(df_long['region'] == 'Ставропольский край') & (df_long['year'] == 2014), 'opzh'].item()
stav_2013 = (stav_2012 + stav_2014) / 2
df_long.loc[(df_long['region'] == 'Ставропольский край') & (df_long['year'] == 2013), 'opzh'] = stav_2013


#Проверка на пропуски
# print(df_long.isnull().sum())

#Сохранить файл
# df_long.to_csv('opzh_regions_long.csv', index=False)
# endregion

# region ВРП предобработка данных
df_vrp = pd.read_excel(r'data\ВРП за 2000-2023.xlsx', index_col=0, header=0)
# список паттернов для удаления

exclude_patterns = [
    'в т.ч. Ненецкий АО',
    'Чеченская Республика',
    'Республика Крым',
    'г.Севастополь',
    'Пермский край',
    'в т.ч. Ханты-Мансийский АО-Югра',
    'Ямало-Ненецкий АО',
    'Камчатский край',
    'Забайкальский край',
    'Архангельская область без Ненецкого АО',  # удаляем строку, где только "Архангельская область" (без уточнений)
    'Тюменская область (кроме Ханты-Мансийского АО-Югры и Ямало-Ненецкого АО)',       # удаляем строку, где только "Тюменская область"
]

# Функция для проверки, содержит ли индекс один из паттернов
def should_exclude(name):
    if pd.isna(name):
        return True
    name_str = str(name)
    for pat in exclude_patterns:
        if pat in name_str:
            return True
    return False

mask = ~df_vrp.index.to_series().apply(should_exclude)
df_vrp_filtered = df_vrp[mask].copy()

# Принудительно преобразуем все значения в numeric (ошибки станут NaN)
df_vrp_filtered = df_vrp_filtered.apply(pd.to_numeric, errors='coerce')

# # Выталкиваем index как столбец
df_vrp_filtered.reset_index(inplace=True)

# Переименуем index как region
df_vrp_filtered.rename(columns={'index': 'region'}, inplace=True)

# Преобразование формата в длинный
df_vrp_long = df_vrp_filtered.melt(id_vars=['region'], var_name='year', value_name='vrp')

# Меняем тип year на numeric
df_vrp_long['year'] = pd.to_numeric(df_vrp_long['year'])
df_vrp_long['region'] = df_vrp_long['region'].str.strip()

# df_vrp_long.to_csv('vrp_regions_long.csv', index=False)

# endregion

df_opzh = pd.read_csv('opzh_regions_long.csv')
df_opzh_vrp = pd.read_csv('opzh_vrp_table.csv')

regions_opzh = set(df_opzh['region'].unique())
regions_vrp = set(df_vrp_long['region'].unique())

# df_merged = pd.merge(df_opzh, df_vrp_long, on=['region', 'year'], how='inner')
# df_merged.to_csv('opzh_vrp_table.csv', index=False)

# print(regions_opzh - regions_vrp)
# print(regions_vrp - regions_opzh)

# region среднемесячная начисленная зп работников
df_wage = pd.read_excel(r'data\ср месячная начисленная зп работников.xlsx')
df_wage.rename(columns={'Unnamed: 0': 'region'}, inplace=True)

df_wage_long = df_wage.melt(id_vars=['region'], var_name='year', value_name='real_wage_index')

df_wage_long['region'] = df_wage_long['region'].str.strip()
df_wage_long.to_csv('df_wage.csv', index=False)

df_merged = pd.merge(df_opzh_vrp, df_wage_long, on=['region', 'year'], how='inner')
df_merged.to_csv('df_opzh_vrp_wage', index=False)

# endregion