import pandas as pd
import numpy as np
from functools import reduce

def life_expectancy():
    df_life_expectancy = pd.read_excel(r'data\ОПЖ всех регионов.xlsx', index_col=0, header=0)

    # удаление агрегированных строк
    exclude_patterns = ['федеральный округ', 'Российская Федерация', 'в том числе: Ханты-Мансийский автономный округ - Югра', 'Ямало-Ненецкий автономный округ', 'в том числе Ненецкий автономный округ']
    mask = ~df_life_expectancy.index.str.contains('|'.join(exclude_patterns), case=False, na=False)
    df_regions = df_life_expectancy[mask].copy()

    #Сброс индексов и колонок
    df_regions.reset_index(inplace=True)
    df_regions.rename(columns={'index': 'region'}, inplace=True)

    df_regions = df_regions.drop(df_regions.columns[[1,2]], axis=1)
    # Преобразование годы из столбцов в строки
    df_long = df_regions.melt(id_vars=['region'], var_name='year', value_name='opzh')

    # Преобразование года в числовой формат
    df_long['year'] = pd.to_numeric(df_long['year'])

    # Линейная интерполяция ставропольского края за 2013 год, данных не было
    stav_2012 = df_long.loc[(df_long['region'] == 'Ставропольский край') & (df_long['year'] == 2012), 'opzh'].item()
    stav_2014 = df_long.loc[(df_long['region'] == 'Ставропольский край') & (df_long['year'] == 2014), 'opzh'].item()
    stav_2013 = (stav_2012 + stav_2014) / 2
    df_long.loc[(df_long['region'] == 'Ставропольский край') & (df_long['year'] == 2013), 'opzh'] = stav_2013

    df_long['opzh'] = df_long['opzh'].astype(str).str.replace('\xa0','', regex=True).str.replace(',','.')
    df_long['opzh'] = pd.to_numeric(df_long['opzh'], errors='coerce')
    print(df_long['opzh'])
    # Проверка на пропуски
    # print(df_long.isnull().sum())
    # Сохранить файл
    df_long.to_csv('opzh_regions_long.csv', index=False)
def VRP():
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
    df_vrp_filtered = df_vrp_filtered.drop(df_vrp_filtered.columns[[1,2]], axis=1)
    # Преобразование формата в длинный
    df_vrp_long = df_vrp_filtered.melt(id_vars=['region'], var_name='year', value_name='vrp')
    # Меняем тип year на numeric
    df_vrp_long['year'] = pd.to_numeric(df_vrp_long['year'])
    df_vrp_long['region'] = df_vrp_long['region'].str.strip()
    df_vrp_long.to_csv('vrp_regions_long.csv', index=False)

def wage():
    df_wage = pd.read_excel(r'data\ср месячная начисленная зп работников.xlsx')
    df_wage.rename(columns={'Unnamed: 0': 'region'}, inplace=True)
    df_wage = df_wage.drop(df_wage.columns[[1,2]], axis=1)
    df_wage_long = df_wage.melt(id_vars=['region'], var_name='year', value_name='real_wage_index')

    df_wage_long['region'] = df_wage_long['region'].str.strip()
    df_wage_long.to_csv('df_wage.csv', index=False)


# df_merged = pd.merge(df_opzh, df_vrp, on=['region', 'year'], how='inner')
# df_merged.to_csv('df_opzh_vrp.csv', index=False)
#

# df_opzh_vrp = pd.read_csv('df_opzh_vrp.csv')
# df_merged = pd.merge(df_opzh_vrp, df_wage, on=['region', 'year'], how='inner')
# df_merged.to_csv('df_opzh_vrp_wage.csv', index=False)

# types = pd.read_csv('df_opzh_vrp_wage.csv')

def unemployment():
    df_unemployment = pd.read_excel(r'data\Уровеь безработицы 2000 2023.xlsx')
    df_unemployment.rename(columns={'регионы': 'region'}, inplace=True)
    df_unemployment = df_unemployment.drop(df_unemployment.columns[[1,2]], axis=1)
    df_unemployment_long = df_unemployment.melt(id_vars=['region'], var_name='year', value_name='unemployment_rate')
    df_unemployment_long['year'] = pd.to_numeric(df_unemployment_long['year'])
    df_unemployment_long.to_csv('df_unemployment_rate.csv', index=False)

# df = pd.read_csv('df_unemployment_rate.csv', nrows=76)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# print(df['region'])

import pandas as pd
import numpy as np
from scipy import stats


def living_wage():
    df_living_wage = pd.read_excel(r'data\Величина пм в 4 квартал по субъектам.xlsx', sheet_name='Лист1', header=0)
    df_living_wage.rename(columns={'Регионы': 'region'}, inplace=True)
    df_living_wage = df_living_wage.drop(df_living_wage.columns[[1, 2]], axis=1)
    df_living_wage_long = df_living_wage.melt(id_vars=['region'], var_name='year', value_name='living_wage')
    df_living_wage_long = df_living_wage_long[df_living_wage_long['region'].notna()]
    df_living_wage_long.to_csv('df_living_wage.csv', index=False)

def capture_of_air_pollutants():
    df_capture_of_air_pollutants = pd.read_excel(r'data\Улавливание загрязняющих атмосферу веществ, отходящих от стационарных источников.xlsx', header=0)
    df_capture_of_air_pollutants.rename(columns={'Регион': 'region'}, inplace=True)
    df_capture_of_air_pollutants = df_capture_of_air_pollutants.drop(df_capture_of_air_pollutants.columns[[1,2]],axis=1) #Удалание данных за 2000
    df_capture_of_air_pollutants_long = df_capture_of_air_pollutants.melt(id_vars=['region'], var_name='year', value_name='capture_mass_level')
    df_capture_of_air_pollutants_long['capture_mass_level'] = df_capture_of_air_pollutants_long['capture_mass_level'].astype(float)
    df_capture_of_air_pollutants_long['year'] = pd.to_numeric(df_capture_of_air_pollutants_long['year'])
    df_capture_of_air_pollutants_long.to_csv('df_capture_of_air_pollutants_long.csv', index=False)

def emissions_of_pollutants():
    df_emission_of_pollutants = pd.read_excel(r'data\Выбросы загр веществ в атмосферных воздух, отходящих от стац источников.xlsx', header=0)
    df_emission_of_pollutants.rename(columns={'Регион': 'region'}, inplace=True)
    df_emission_of_pollutants = df_emission_of_pollutants.drop(df_emission_of_pollutants.columns[[1,2]], axis=1)
    df_emission_of_pollutants_long = df_emission_of_pollutants.melt(id_vars=['region'], var_name='year', value_name='emissions_mass_level')
    df_emission_of_pollutants_long['year'] = pd.to_numeric(df_emission_of_pollutants_long['year'])
    df_emission_of_pollutants_long.to_csv('df_emission_of_pollutants_long.csv', index=False)

life_expectancy()
VRP()
wage()
unemployment()
living_wage()
capture_of_air_pollutants()
emissions_of_pollutants()
#
df_opzh = pd.read_csv('opzh_regions_long.csv', index_col=0)
df_vrp = pd.read_csv('vrp_regions_long.csv', index_col=0)
df_wage =pd.read_csv('df_wage.csv', index_col=0)
df_unemployment = pd.read_csv('df_unemployment_rate.csv', index_col=0)
df_living_wage = pd.read_csv('df_living_wage.csv', index_col=0)
df_capture_of_air_pollutants = pd.read_csv('df_capture_of_air_pollutants_long.csv', index_col=0)
df_emission_of_pollutants_long = pd.read_csv('df_emission_of_pollutants_long.csv', index_col=0)
#
dataframes = [df_opzh, df_vrp, df_wage, df_unemployment, df_living_wage, df_capture_of_air_pollutants, df_emission_of_pollutants_long]
df_merged = reduce(lambda left, right: pd.merge(left, right, on=['region', 'year'], how='inner'), dataframes)
df_merged.to_csv('dataframes.csv')
df_merged.to_excel('dataframe_excel.xlsx')