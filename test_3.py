import pandas as pd
import geopandas as gpd
import libpysal as lps
from libpysal.weights import Queen

mapping_regions = {
    "Adygey": "Республика Адыгея",
    "Altay": "Алтайский край",
    "Amur": "Амурская область",
    "Arkhangel'sk": "Архангельская область",
    "Astrakhan'": "Астраханская область",
    "Bashkortostan": "Республика Башкортостан",
    "Belgorod": "Белгородская область",
    "Bryansk": "Брянская область",
    "Buryat": "Республика Бурятия",
    "Chechnya": "Чеченская Республика",
    "Chelyabinsk": "Челябинская область",
    "Chukot": "Чукотский автономный округ",
    "Chuvash": "Чувашская Республика",
    "City of St. Petersburg": "г. Санкт-Петербург",
    "Dagestan": "Республика Дагестан",
    "Gorno-Altay": "Республика Алтай",
    "Ingush": "Республика Ингушетия",
    "Irkutsk": "Иркутская область",
    "Ivanovo": "Ивановская область",
    "Kabardin-Balkar": "Кабардино-Балкарская Республика",
    "Kaliningrad": "Калининградская область",
    "Kalmyk": "Республика Калмыкия",
    "Kaluga": "Калужская область",
    "Kamchatka": "Камчатский край",
    "Karachay-Cherkess": "Карачаево-Черкесская Республика",
    "Karelia": "Республика Карелия",
    "Kemerovo": "Кемеровская область",
    "Khabarovsk": "Хабаровский край",
    "Khakass": "Республика Хакасия",
    "Khanty-Mansiy": "Ханты-Мансийский автономный округ - Югра",
    "Kirov": "Кировская область",
    "Komi": "Республика Коми",
    "Kostroma": "Костромская область",
    "Krasnodar": "Краснодарский край",
    "Krasnoyarsk": "Красноярский край",
    "Kurgan": "Курганская область",
    "Kursk": "Курская область",
    "Leningrad": "Ленинградская область",
    "Lipetsk": "Липецкая область",
    "Maga Buryatdan": "Магаданская область",
    "Mariy-El": "Республика Марий Эл",
    "Mordovia": "Республика Мордовия",
    "Moscow City": "г. Москва",
    "Moskva": "Московская область",
    "Murmansk": "Мурманская область",
    "Nenets": "Ненецкий автономный округ",
    "Nizhegorod": "Нижегородская область",
    "North Ossetia": "Республика Северная Осетия - Алания",
    "Novgorod": "Новгородская область",
    "Novosibirsk": "Новосибирская область",
    "Omsk": "Омская область",
    "Orel": "Орловская область",
    "Orenburg": "Оренбургская область",
    "Penza": "Пензенская область",
    "Perm'": "Пермский край",
    "Primor'ye": "Приморский край",
    "Pskov": "Псковская область",
    "Rostov": "Ростовская область",
    "Ryazan'": "Рязанская область",
    "Sakha": "Республика Саха (Якутия)",
    "Sakhalin": "Сахалинская область",
    "Samara": "Самарская область",
    "Saratov": "Саратовская область",
    "Smolensk": "Смоленская область",
    "Stavropol'": "Ставропольский край",
    "Sverdlovsk": "Свердловская область",
    "Tambov": "Тамбовская область",
    "Tatarstan": "Республика Татарстан",
    "Tomsk": "Томская область",
    "Tula": "Тульская область",
    "Tuva": "Республика Тыва",
    "Tver'": "Тверская область",
    "Tyumen'": "Тюменская область",
    "Udmurt": "Удмуртская Республика",
    "Ul'yanovsk": "Ульяновская область",
    "Vladimir": "Владимирская область",
    "Volgograd": "Волгоградская область",
    "Vologda": "Вологодская область",
    "Voronezh": "Воронежская область",
    "Yamal-Nenets": "Ямало-Ненецкий автономный округ",
    "Yaroslavl'": "Ярославская область",
    "Yevrey": "Еврейская автономная область",
    "Zabaykal'ye": "Забайкальский край"
}

df = pd.read_csv('dataframes.csv')  # путь к вашей таблице
# print(df.info())
# print(df.head())
# print(df.isnull().sum().sum())  # общее количество пропусков, должно быть 0

df = pd.read_csv(r"dataframes.csv")
zip_path = r"C:/Users/semen/Desktop/Похожие работы/rus_adm_gadm_2022_v03.gdb"
gdf = gpd.read_file(zip_path, layer='rus_admbnda_adm2_gadm_2022_v02')
# gdf_names = gdf['ADM2_EN'].unique()

# region old
# gdf['region_name_ru'] = gdf['ADM2_EN'].map(mapping_regions)
# # print(gdf[['ADM1_EN', 'ADM2_EN', 'region_name_ru']].head())
# df['indexes'] = range(len(df))
# df_combined = gdf.merge(df, left_on='region_name_ru', right_on='region', how='inner')
# # print(df_combined[['ADM2_EN','ADM2_PCODE', 'Shape_Area', 'region', 'year', 'opzh']])
# w = lps.weights.Queen.from_dataframe(df_combined, use_index=False)
# w.transform = 'r'
# df_combined = df_combined.sort_values('indexes').drop(columns=['indexes'])
# years = df_combined['year'].unique()
# list_of_dfs = []
# end region

gdf['region_name_ru'] = gdf['ADM2_EN'].map(mapping_regions)
gdf = gdf.dropna(subset=['region_name_ru']).sort_values('region_name_ru').reset_index(drop=True)

df['indexes'] = range(len(df))


df_combined = gdf.merge(df, left_on='region_name_ru', right_on='region', how='inner')

gdf_unique_regions = df_combined.drop_duplicates(subset=['region']).copy()
gdf_unique_regions = gdf_unique_regions.sort_values('region').reset_index(drop=True)
print(gdf_unique_regions)

# Использовал метод KNN
w = lps.weights.KNN.from_dataframe(gdf_unique_regions, k=5)
w.transform = 'r'

df_combined = df_combined.sort_values('indexes').drop(columns=['indexes'])
print(df_combined)

years = df_combined['year'].unique()
list_of_dfs = []

for year in years:
    df_year = df_combined[df_combined['year'] == year].copy()

    y = df_year['opzh'].values
    if len(y) != w.n:
        print(f"Пропуск {year} года: в данных {len(y)} регионов, а в матрице весов {w.n}")
        continue
    lag = lps.weights.lag_spatial(w, y)
    df_year['lag_opzh'] = lag
    list_of_dfs.append(df_year)

final_df = pd.concat(list_of_dfs)
print("ФИНАЛ", final_df)

csv = final_df.to_csv("dataframe_v2.csv")
excel = final_df.to_excel("dataframe_excel_v2.xlsx")