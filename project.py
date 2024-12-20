import os  # Импортируем модуль os для работы с файловой системой
import csv  # Импортируем модуль csv для работы с CSV файлами


class PriceMachine:

    def __init__(self):
        self.data = []  # Инициализируем список для хранения загруженных данных

    def load_prices(self, file_path='docs'):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт

            Допустимые названия для столбца с ценой:
                розница
                цена

            Допустимые названия для столбца с весом (в кг.):
                вес
                масса
                фасовка
        '''
        price_files = []  # Создаем пустой список для хранения файлов с прайсами
        for filename in os.listdir(file_path):  # Перебираем все файлы в указанной директории
            if 'price' in filename.lower():  # Проверяем, содержит ли имя файла слово "price"
                price_files.append(os.path.join(file_path, filename))  # Если да, добавляем файл в список

        for file in price_files:  # Перебираем найденные файлы
            with open(file, "r", encoding='utf-8') as file:  # Открываем файл для чтения
                reader = [row for row in csv.reader(file, delimiter=',')]  # Читаем файл как CSV и создаем список строк
                if not reader:  # Проверяем, пуст ли файл
                    print(f"Предупреждение: Файл {file} пуст")  # Если пустой, выводим предупреждение
                    continue  # Переходим к следующему файлу

            headers = reader[0]  # Получаем заголовки столбцов из первой строки
            name_index, price_index, weight_index = self._search_product_price_weight(
                headers)  # Получаем индексы нужных столбцов

            for row in reader[1:]:  # Перебираем строки с данными, пропуская заголовок
                name = row[name_index].lower().strip()  # Получаем наименование товара, приводим к нижнему регистру и убираем пробелы
                price = float(row[price_index])  # Получаем цену как вещественное число
                weight = float(row[weight_index])  # Получаем вес как вещественное число
                filename = file.name  # Сохраняем имя файла
                price_kg = round(price / weight,
                                 1)  # Рассчитываем цену за килограмм и округляем до одного знака после запятой

                self.data.append([name, price, weight, filename, price_kg])  # Добавляем данные в общий список

    def _search_product_price_weight(self, headers):
        '''
            Возвращает номера столбцов для названия, цены и веса
        '''
        name = ['название', 'продукт', 'товар', 'наименование']  # Возможные заголовки для названия товара
        price = ['цена', 'розница']  # Возможные заголовки для цены
        weight = ['фасовка', 'масса', 'вес']  # Возможные заголовки для веса

        # Находим индекс столбца с названием товара
        name_col = next((i for i, header in enumerate(headers) if header.lower() in name), None)
        # Находим индекс столбца с ценой
        price_col = next((i for i, header in enumerate(headers) if header.lower() in price), None)
        # Находим индекс столбца с весом
        weight_col = next((i for i, header in enumerate(headers) if header.lower() in weight), None)

        return name_col, price_col, weight_col  # Возвращаем индексы найденных колонок

    def export_to_html(self, fname='output.html'):
        # Начинаем формирование HTML-кода для таблицы с результатами
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for index, product in enumerate(self.data):  # Перебираем все загруженные продукты
            name, price, weight, filename, price_kg = product  # Распаковываем данные продукта
            result += (f'<tr><td>{index + 1}</td><td>{name}</td><td>{price:.2f}</td><td>{weight:.2f}</td>'
                       f'<td>{filename}</td><td>{price_kg:.2f}</td></tr>\n')  # Формируем строку таблицы
        result += f'</table>\n</body>\n</html>'  # Закрываем теги таблицы и HTML

        with open(fname, 'w', encoding='utf-8') as f:  # Открываем файл для записи в формате HTML
            f.write(result)  # Записываем HTML-код в файл

        return f'HTML сформирован в файле {fname}'  # Возвращаем сообщение о завершении экспорта в HTML

    def find_text(self):
        '''
            Получает текст из консоли и возвращает список позиций, содержащий этот текст в названии продукта
        '''
        while True:  # Начинаем бесконечный цикл для поиска
            text = input(
                "Введите название продукта для поиска: ").strip().lower()  # Запрашиваем ввод от пользователя и обрабатываем текст
            if text == 'exit':  # Проверяем, не ввел ли пользователь 'exit'
                break  # Если да, выходим из цикла

            positions = []  # Создаем пустой список для хранения найденных позиций
            for index, product in enumerate(self.data[1:], start=1):  # Перебираем все продукты, начиная с 1, так как 0 - это заголовки
                name = product[0].strip().lower()  # Получаем наименование продукта, приводим к нижнему регистру и убираем пробелы
                price_kg = product[4]  # Получаем цену за килограмм из заранее рассчитанного поля
                if text in name:  # Проверяем, содержится ли введенный текст в названии продукта
                    positions.append([index, int(price_kg)])  # Если да, добавляем индекс и цену за кг. в список позиций

            # Сортируем список найденных позиций по возрастанию цены за кг.
            for i in range(1, len(positions)):  # Начинаем сортировку с второго элемента
                key = positions[i]  # Сохраняем текущий элемент для сравнения
                j = i - 1  # Устанавливаем индекс для сравнения с предыдущим элементом
                while j >= 0 and key[1] < positions[j][
                    1]:  # Пока индекс j не выходит за пределы и цена текущего меньше цены предыдущего
                    positions[j + 1] = positions[j]  # Сдвигаем элемент на одну позицию вправо
                    j -= 1  # Уменьшаем индекс для следующего сравнения
                positions[j + 1] = key  # Вставляем сохраненный элемент на его правильное место

            # Печатаем результаты поиска
            if positions:  # Проверяем, есть ли найденные позиции
                print(f'{"№":<4} {"Наименование":<40} {"Цена":<6} '  # Заголовки таблицы
                      f'{"Вес":<6} {"Файл":<20} {"Цена за кг.":<6}')
                for index, i in enumerate(positions):  # Перебираем найденные позиции
                    i = i[0]  # Получаем индекс продукта
                    print(
                        f'{index + 1:<4} {self.data[i][0]:<40} {self.data[i][1]:<6} '  # Печатаем наименование, цену, вес и файл
                        f'{self.data[i][2]:<6} {self.data[i][3]:<20} {self.data[i][4]:<6}')
                print(f'Поиск завершен.')  # Выводим сообщение о завершении поиска
            else:
                print(f'Не найдено ни одного совпадения.')  # Если ничего не найдено, выводим соответствующее сообщение


if __name__ == "__main__":
    pm = PriceMachine()
    pm.load_prices()
    pm.find_text()
    print('the end')
    pm.export_to_html()
