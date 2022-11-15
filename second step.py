import requests
from bs4 import BeautifulSoup
import json
import csv

"""Сайт для парсинга"""
URL = 'https://calorizator.ru/product'

headers= {
    'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                  'Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.79',
}       #Обозначения юзера, чтобы сайт не подумал, что мы бот
req = requests.get(URL, headers=headers)
src = req.text          #html страницы
print(src)

with open('index.html', 'w', encoding='UTF-8') as file:       #сохраняем в файл, чтобы при получении бана или стоппера - ничего не потерять
    file.write(src)

with open('index.html', encoding='UTF-8') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')

all_categories_dict = {}
reduce = ['product/all', 'product/choice', 'product/pix', 'product/brand', '/cabinet']      # Выкидываем ненужные ссылки
for product_elem in soup.find_all('ul', class_='product'):
    for a_tag in product_elem.find_all('a'):                    #! Цикл для обращения к детям тегов в find_all
        a_tag_text = a_tag.text
        a_tag_href = 'https://calorizator.ru/' + a_tag['href']  #! Важно добавить доменное имя
        if a_tag['href'] in reduce:
            pass
        else:
            all_categories_dict[a_tag_text] = a_tag_href

with open('Second_step_all_categories_dict.json', 'w', encoding='UTF-8') as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)        # Записать в формате JSON "что", "куда" indent - отступ, ensure_ascii - для кириллицы

with open('Second_step_all_categories_dict.json', encoding='UTF-8') as file:
    all_categories = json.load(file)

page_count = int(len(all_categories))
count = 0
print(f'Всего итераций: {page_count}')
for category_name, category_href in all_categories.items():

    replace_symbols = ['-', ' ']        # Создаем список символов
    for item in replace_symbols:        # Запускаем цикл по символам
        if item in category_name:       # Проверка на вхождение символа
            category_name = category_name.replace(item, '_')     # Перезаписываем название с _

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    """Записываем ссылки и категории в html"""
    with open(f'data_second_step/{count}_{category_name}.html', 'w', encoding='UTF-8') as file:
        file.write(src)

    """Открываем файл"""
    with open(f'data_second_step/{count}_{category_name}.html',encoding='UTF-8') as file:     # Читаем файл
        src = file.read()

    """Создаем объект, чтобы парсить"""
    soup = BeautifulSoup(src, 'lxml')

    """Находим нужный нам тег таблицы, чтобы достать продукты и виды граммовок"""
    table_head = soup.find(class_='sticky-enabled').find('tr').find_all('a')
    product = table_head[0].text
    proteins = table_head[1].text
    fats = table_head[2].text
    ugl = table_head[3].text
    kkal = table_head[4].text

    """Записываем в CSV файл"""
    with open(f'data_second_step/{count}_{category_name}.csv', 'w', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                product,
                proteins,
                fats,
                ugl,
                kkal,
            )
        )

    products_data = soup.find(class_='sticky-enabled').find('tbody').find_all('tr')

    """Передаем список значений в списке словарей"""
    product_info = []
    for item in products_data:
        products_tds = item.find_all('td')

        title = products_tds[1].find('a').text
        proteins = products_tds[2].text
        fats = products_tds[3].text
        ugl = products_tds[4].text
        kkal = products_tds[5].text

        product_info.append({
            'Title': title,
            'Proteins': proteins,
            'Fats': fats,
            'Ugl': ugl,
            'Kkal': kkal
        })
        """Записываем информацию в csv файл"""
        with open(f'data_second_step/{count}_{category_name}.csv', 'a', encoding='UTF-8') as file_1:
            writer_1 = csv.writer(file_1)
            writer_1.writerow((title, proteins, fats, ugl, kkal))

    with open(f'data_second_step/{count}_{category_name}.json', 'w', encoding='UTF-8') as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f'Итерация {count}. {category_name} записан...')
    page_count -= 1
    print(f'Осталось итераций: {page_count}')
