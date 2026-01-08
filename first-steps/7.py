import csv
import os


def main():

    "Создает единый TXT файл"

    # Файлы
    csv_file = "web_clients_correct.csv"
    txt_file = "customers_descriptions.txt"

    # Проверяем CSV файл
    if not os.path.exists(csv_file):
        print(f" Файл {csv_file} не найден!")
        return

    # Читаем CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        customers = list(reader)

    print(f"Найдено покупателей: {len(customers)}")

    # Создаем TXT файл со всеми описаниями
    with open(txt_file, 'w', encoding='utf-8') as out_file:
        for i, customer in enumerate(customers, 1):
            # Данные
            name = customer.get('name', 'Неизвестно')
            sex = customer.get('sex', '')
            age = customer.get('age', '')
            device = customer.get('device_type', '')
            browser = customer.get('browser', '')
            bill = customer.get('bill', '0')
            region = customer.get('region', '')

            # Форматирование
            if sex.lower() == 'female':
                gender = 'женского пола'
                verb = 'совершила'
            elif sex.lower() == 'male':
                gender = 'мужского пола'
                verb = 'совершил'
            else:
                gender = 'неизвестного пола'
                verb = 'совершил(а)'

            # Устройство
            device_text = {
                "mobile": 'мобильного',
                'tablet': 'планшета',
                'laptop': 'ноутбука',
                'desktop': 'компьютера'
            }.get(device.lower(), device)

            # Описание
            description = (
                f"Пользователь {name} {gender}, {age} лет {verb} покупку на {bill} у.е. "
                f"с {device_text} браузера {browser}. "
                f"Регион, из которого совершалась покупка: {region}."
            )

            # Записываем в файл
            out_file.write(f"{description}\n\n")

            # Прогресс
            if i % 100 == 0:
                print(f"Записано: {i}/{len(customers)}")

    print(f"Создан единый TXT-файл: {txt_file}")
    print(f"Записано описаний: {len(customers)}")


# Запуск
if __name__ == "__main__":
    main()