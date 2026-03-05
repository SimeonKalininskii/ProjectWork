import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 1. Загрузка страницы
url = "http://rosstat.gov.ru/bgd/regl/B05_14p/IssWWW.exe/Stg/d010/10-01.htm"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'windows-1251'  # кодировка страницы
    response.raise_for_status()
except Exception as e:
    print(f"Ошибка загрузки: {e}")
    exit()

soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table')
rows = table.find_all('tr')

# 2. Определяем индексы столбцов для 2000, 2001, 2002, 2003
header_row = None
for row in rows:
    cells = row.find_all(['td', 'th'])
    # Ищем строку, содержащую хотя бы один нужный год
    if any(cell.get_text().strip() in ('2000','2001','2002','2003') for cell in cells):
        header_row = cells
        break

if not header_row:
    print("Не найдена строка с заголовками годов.")
    exit()

# Составляем словарь {год: индекс_столбца}
years = ['2000','2001','2002','2003']
year_indices = {}
for idx, cell in enumerate(header_row):
    text = cell.get_text().strip()
    if text in years:
        year_indices[text] = idx

# Проверяем, что все годы найдены
if len(year_indices) < 4:
    print("Найдены не все нужные годы в заголовке.")
    # но продолжим с теми, что есть

# 3. Сбор данных по регионам
data_records = []  # список словарей для будущего DataFrame

for row in rows:
    cells = row.find_all('td')
    if len(cells) < 2:  # минимум название + значение
        continue

    # Название региона (первая ячейка)
    region_cell = cells[0]
    # Обрабатываем название: заменяем <br> на пробел, убираем лишние пробелы
    raw_name = region_cell.get_text(separator=' ', strip=True)

    # Пропускаем строки-заголовки, итоги по округам и РФ
    if not raw_name or raw_name.isdigit():
        continue
    lower_name = raw_name.lower()
    if ('федеральный округ' in lower_name or
        'российская федерация' in lower_name or
        'валовой региональный продукт' in lower_name):
        continue

    # Очищаем от приставки "в том числе" (для автономных округов)
    region_name = re.sub(r'в том числе\s*', '', raw_name, flags=re.IGNORECASE).strip()
    if not region_name:
        continue

    # Создаём запись для региона
    record = {'Регион': region_name}

    # Для каждого года пытаемся извлечь значение
    for year, col_idx in year_indices.items():
        if col_idx < len(cells):
            cell = cells[col_idx]
            text_val = cell.get_text(strip=True)
            # Проверяем, что ячейка содержит число (не прочерк, не пусто)
            if text_val and text_val != '...' and re.match(r'^[\d\.,]+$', text_val):
                # Убираем разделители тысяч (запятые) и пробелы, заменяем запятую на точку
                clean = text_val.replace(',', '').replace(' ', '').replace(',', '.')
                try:
                    value = float(clean)
                except ValueError:
                    value = float('nan')
            else:
                value = float('nan')
        else:
            value = float('nan')
        record[year] = value

    data_records.append(record)

# 4. Создаём DataFrame
df = pd.DataFrame(data_records)
df.set_index('Регион', inplace=True)

# Приводим названия столбцов к целым числам (годам) для удобства
df.columns = df.columns.astype(int)

# Сортируем регионы по алфавиту
df.sort_index(inplace=True)

# 5. Вывод результатов
print(f"Собрано данных по {len(df)} регионам.\n")
print(df.head(10))  # первые 10 строк

# Сохраняем в CSV
csv_file = 'trash/vrp_2000_2003.csv'
df.to_csv(csv_file, encoding='utf-8-sig')
print(f"\nДанные сохранены в файл {csv_file}")

# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import re
#
# # 1. Загружаем новую страницу
# url = "https://rosstat.gov.ru/bgd/regl/B11_14p/IssWWW.exe/Stg/d01/11-01.htm"
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# }
#
# try:
#     response = requests.get(url, headers=headers, verify=False)
#     response.encoding = 'windows-1251'  # Кодировка страницы
#     response.raise_for_status()
# except Exception as e:
#     print(f"Ошибка загрузки: {e}")
#     exit()
#
# soup = BeautifulSoup(response.text, 'html.parser')
# table = soup.find('table')
# rows = table.find_all('tr')
#
# # 2. Определяем индексы столбцов для 2004, 2005, 2006, 2007, 2008, 2009
# header_row = None
# for row in rows:
#     cells = row.find_all(['td', 'th'])
#     # Ищем строку, содержащую хотя бы один нужный год
#     if any(cell.get_text().strip() in ('2004','2005','2006','2007','2008','2009') for cell in cells):
#         header_row = cells
#         break
#
# if not header_row:
#     print("Не найдена строка с заголовками годов.")
#     exit()
#
# # Составляем словарь {год: индекс_столбца}
# years = ['2004','2005','2006','2007','2008','2009']
# year_indices = {}
# for idx, cell in enumerate(header_row):
#     text = cell.get_text().strip()
#     if text in years:
#         year_indices[text] = idx
#
# # Проверяем, что все нужные годы найдены
# found_years = list(year_indices.keys())
# print(f"Найдены столбцы для годов: {found_years}")
# if len(year_indices) < 6:
#     print(f"Внимание: Найдены не все годы. Будем работать с {found_years}")
#
# # 3. Сбор данных по регионам
# data_records = []  # список словарей для будущего DataFrame
#
# for row in rows:
#     cells = row.find_all('td')
#     if len(cells) < 2:  # минимум название + значение
#         continue
#
#     # Название региона (первая ячейка)
#     region_cell = cells[0]
#     # Обрабатываем название: заменяем <br> на пробел, убираем лишние пробелы
#     raw_name = region_cell.get_text(separator=' ', strip=True)
#
#     # Пропускаем строки-заголовки, итоги по округам и РФ
#     if not raw_name or raw_name.isdigit():
#         continue
#     lower_name = raw_name.lower()
#     if ('федеральный округ' in lower_name or
#         'российская федерация' in lower_name or
#         'валовой региональный продукт' in lower_name or
#         'субъектам' in lower_name):  # Добавил для этой страницы
#         continue
#
#     # Очищаем от приставки "в том числе" (для автономных округов)
#     region_name = re.sub(r'в том числе\s*', '', raw_name, flags=re.IGNORECASE).strip()
#     if not region_name:
#         continue
#
#     # Создаём запись для региона
#     record = {'Регион': region_name}
#
#     # Для каждого года пытаемся извлечь значение
#     for year, col_idx in year_indices.items():
#         if col_idx < len(cells):
#             cell = cells[col_idx]
#             text_val = cell.get_text(strip=True)
#             # Проверяем, что ячейка содержит число (не прочерк, не пусто)
#             if text_val and text_val != '...' and re.match(r'^[\d\.,]+$', text_val):
#                 # Убираем разделители тысяч (запятые) и пробелы, заменяем запятую на точку
#                 clean = text_val.replace(',', '').replace(' ', '').replace(',', '.')
#                 try:
#                     value = float(clean)
#                 except ValueError:
#                     value = float('nan')
#             else:
#                 value = float('nan')
#         else:
#             value = float('nan')
#         record[year] = value
#
#     data_records.append(record)
#
# # 4. Создаём DataFrame
# df = pd.DataFrame(data_records)
# df.set_index('Регион', inplace=True)
#
# # Приводим названия столбцов к целым числам (годам) для удобства
# df.columns = df.columns.astype(int)
#
# # Сортируем регионы по алфавиту
# df.sort_index(inplace=True)
#
# # 5. Вывод результатов
# print(f"\nСобрано данных по {len(df)} регионам.\n")
# print(df.head(10))  # первые 10 строк
#
# # Базовая статистика по годам
# print("\nСтатистика по годам (сумма, млн руб.):")
# print(df.sum())
#
# # Сохраняем в CSV
# csv_file = 'vrp_2004_2009.csv'
# df.to_csv(csv_file, encoding='utf-8-sig')
# print(f"\nДанные сохранены в файл {csv_file}")

# import csv
# import re
#
# # Содержимое файла VRP_s_1998 (1).xlsx в виде многострочной строки
# # (в реальности следует загрузить файл или скопировать сюда полный текст)
# data = "r\C:\Users\semen\Downloads\VRP_s_1998 (1).xlsx"  # здесь должен быть полный текст из задания
#
# # Разделяем на листы по маркеру "> metadata.sheet_name:"
# sheets_raw = re.split(r'> metadata\.sheet_name:.*\n', data)
# # Лист 1 (1998-2015) — индекс 2 (после "Содержание")
# # Лист 2 (2016-2023) — индекс 3
# sheet1 = sheets_raw[2]
# sheet2 = sheets_raw[3]
#
#
# def parse_sheet(text, start_year, end_year):
#     """
#     Парсит лист с данными по регионам.
#     Возвращает словарь {регион: [значения по годам]}
#     """
#     lines = text.strip().split('\n')
#     # Ищем строку с годами (первая строка данных после заголовка)
#     header_line = None
#     for i, line in enumerate(lines):
#         if line.strip().startswith('| 1998 |') or line.strip().startswith('| 2016 |'):
#             header_line = i
#             break
#     if header_line is None:
#         return {}
#
#     # Определяем столбцы для нужных годов
#     years = [col.strip() for col in lines[header_line].split('|')[1:-1]]
#     year_indices = {str(y): i for i, y in enumerate(years, start=1)}  # индекс столбца (1-based в split)
#     needed_years = [str(y) for y in range(start_year, end_year + 1)]
#     col_indices = [year_indices[y] for y in needed_years if y in year_indices]
#
#     # Парсим строки с регионами (начиная с header_line+1)
#     regions = {}
#     skip_patterns = [
#         'федеральный округ',
#         'Российская Федерация',
#         'без Ненецкого авт.округа',
#         'без Ханты-Мансийского',
#         'без Ямало-Ненецкого',
#         'Содержание',
#         'К содержанию',
#         'Ответственный исполнитель',
#         'Обновлено:'
#     ]
#
#     for line in lines[header_line + 1:]:
#         if not line.startswith('|'):
#             continue
#         parts = [p.strip() for p in line.split('|')[1:-1]]
#         if len(parts) < 2:
#             continue
#         region_name = parts[0]
#         # Пропускаем служебные строки
#         if any(pat in region_name for pat in skip_patterns):
#             continue
#         # Извлекаем значения для нужных годов
#         values = []
#         for idx in col_indices:
#             if idx < len(parts):
#                 val = parts[idx].strip()
#                 # Заменяем пустые/пропуски на None
#                 if val in ('', '…', '...', '-', '—'):
#                     val = None
#                 else:
#                     # Преобразуем число: убираем пробелы, заменяем запятую на точку, обрабатываем экспоненту
#                     val = val.replace(' ', '').replace(',', '.')
#                     if 'e' in val.lower():
#                         try:
#                             val = float(val)
#                         except:
#                             val = None
#                     else:
#                         try:
#                             val = float(val)
#                         except:
#                             val = None
#                 values.append(val)
#             else:
#                 values.append(None)
#         regions[region_name] = values
#     return regions
#
#
# # Парсим листы
# data_2010_2015 = parse_sheet(sheet1, 2010, 2015)
# data_2016_2023 = parse_sheet(sheet2, 2016, 2023)
#
# # Объединяем данные по регионам
# all_regions = sorted(set(data_2010_2015.keys()) | set(data_2016_2023.keys()))
# years = list(range(2010, 2024))
#
# # Записываем в CSV
# with open('vrp_regions_2010_2023.csv', 'w', newline='', encoding='utf-8-sig') as f:
#     writer = csv.writer(f, delimiter=';')
#     writer.writerow(['Регион'] + years)
#     for region in all_regions:
#         row = [region]
#         # Для каждого года берём значение из соответствующего листа
#         for year in years:
#             if year <= 2015:
#                 val = data_2010_2015.get(region, [None] * 6)[year - 2010] if region in data_2010_2015 else None
#             else:
#                 val = data_2016_2023.get(region, [None] * 8)[year - 2016] if region in data_2016_2023 else None
#             row.append(val)
#         writer.writerow(row)
#
# print("Готово. Файл vrp_regions_2010_2023.csv создан.")