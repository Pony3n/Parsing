import json
import requests
from bs4 import BeautifulSoup
import csv


def get_data():
    """Открываем файл, куда записываем категории"""
    with open('labirinth/sale_books.csv', 'w', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow((
            'Название',
            'Автор',
            'Издательство',
            'Цена (Новая)',
            'Цена (старая)',
            'Разница',
            'Наличие'
        ))

    url = 'https://www.labirint.ru/search/?discount=1&available=1&order=actd&way=back&paperbooks=1&ebooks=1&otherbooks=1&display=table'
    headers = {
        'accept': '* / *',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.79'
    }

    response = requests.get(url, headers)
    soup = BeautifulSoup(response.text, 'lxml')

    pages_count = int(soup.find('div', class_='pagination-number').find_all('a')[-1].text)      # Количество страниц

    books_list = []     # Список всех книг
    page = 1
    """Цикл по страницам"""
    for i in range(1, pages_count + 1):
        print(f'Смотрим страницу {page}')
        url = f'https://www.labirint.ru/search/?discount=1&available=1&order=actd&way=back&paperbooks=1&ebooks=1&otherbooks=1&display=table&page={i}'

        response = requests.get(url, headers)
        soup = BeautifulSoup(response.text, 'lxml')

        book_list = soup.find('tbody', class_='products-table__body').find_all('tr')
        """Цикл по книгам"""
        for book in book_list:
            book_data = book.find_all('td')

            try:
                book_title = book_data[0].find('a').text
                book_author = book_data[1].find('a').text
                book_publisher = book_data[2].find_all('a')
                book_publisher = ':'.join([bp.text for bp in book_publisher])   # Цикл для добавления 2-х тегов в 1 объект
                book_price_new = int(book_data[3].find('span').text.strip().replace('₽', ''))
                book_price_old = int(book_data[3].find('span', class_='price-gray').text.strip().replace('₽', ''))
                delta_price = round((book_price_new - book_price_old) / book_price_old * 100)
                book_in_place = book_data[5].find('div').text
                books_list.append(
                    {
                        'book_title': book_title,
                        'book-author': book_author,
                        'book_publisher': book_publisher,
                        'book_price_new': book_price_new,
                        'book_price_old': book_price_old,
                        'delta_price': delta_price,
                        'book_in_place': book_in_place
                    }
                )
            except Exception:
                continue

            """Открываем csv файл и записываем туда информацию по категориям"""
            with open('labirinth/sale_books.csv', 'a', encoding='UTF-8') as file:
                writer = csv.writer(file)
                writer.writerow((
                    book_title,
                    book_author,
                    book_publisher,
                    book_price_new,
                    book_price_old,
                    delta_price,
                    book_in_place
                ))
        page += 1
    """Открываем json файл и записываем туда информацию"""
    with open('labirinth/sale_books.json', 'w', encoding='UTF-8') as file:
        json.dump(books_list, file, indent=4, ensure_ascii=False)


def main():
    get_data()

if __name__ == '__main__':
    main()