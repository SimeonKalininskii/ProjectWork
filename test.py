import pandas as pd
import numpy as np

# region ОПЖ Предобработка данных
df_life_expectancy = pd.read_excel(r'C:\Users\semen\Desktop\Новая диссертация\Данные\факторы\ОПЖ всех регионов.xlsx', index_col=0, header=0)

# удаление агрегированных строк
exclude_patterns = ['федеральный округ', 'Российская Федерация', 'в том числе: Ханты-Мансийский автономный округ - Югра', 'Ямало-Ненецкий автономный округ']
mask = ~df_life_expectancy.index.str.contains('|'.join(exclude_patterns), case=False, na=False)
df_regions = df_life_expectancy[mask].copy()
print(df_regions.shape)
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
df_vrp = pd.read_excel(r'C:\Users\semen\Desktop\Новая диссертация\Данные\факторы\ВРП за 2000-2023.xlsx', index_col=0, header=0)
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
print(df_vrp_filtered.shape)

# endregion


VRP = pd.read_excel(r'C:\Users\semen\Desktop\Новая диссертация\Данные\факторы\ВРП за 2000-2023.xlsx', index_col=0)
