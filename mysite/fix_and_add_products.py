"""
fix_and_add_products.py
------------------------
Всё-в-одном скрипт:
1. Исправляет неправильные связи Category/SubCategory/Product (баг
   старого seed_data.py, из-за которого категории показывали чужие
   товары).
2. Для категорий без подкатегорий (Beauty, Garden, Pets, Music, Tools,
   Jewelry, Food) создаёт по 2 настоящих тематических подкатегории.
3. Добавляет по 15 товаров в каждую категорию — с настоящими
   названиями товаров (не "Category Item 1"), описанием и ценой.
   Фото НЕ генерируются — вы добавите их сами через Django admin.
4. Добавляет отзывы/оценки (звёзды + комментарий) на каждый новый
   товар от случайных существующих пользователей.

Скрипт безопасно перезапускать: он не создаёт дубликаты (проверяет
по названию товара/подкатегории через get_or_create).

Ничего не удаляет: пользователи, корзины, старые заказы не трогаются.

КАК ЗАПУСТИТЬ
Положите этот файл рядом с manage.py (туда же, где seed_data.py):
    C:\\Users\\user\\PycharmProjects\\AvitoSait\\mysite\\fix_and_add_products.py

Затем (venv активирован):
    python fix_and_add_products.py
"""
import os
import random
import sys
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402
from django.db.models import Max  # noqa: E402

from avito_app.models import Category, Product, Review, SubCategory, UserProfile  # noqa: E402


# ---------------------------------------------------------------------------
# Часть 1: исправление неправильных связей (по названиям, не по id)
# ---------------------------------------------------------------------------
SUBCATEGORY_TO_CATEGORY = {
    'Smartphones': 'Electronics',
    'Laptops': 'Electronics',
    'Sofas': 'Furniture',
    'Tables': 'Furniture',
    'T-Shirts': 'Clothing',
    'Jeans': 'Clothing',
    'Cars': 'Vehicles',
    'Motorcycles': 'Vehicles',
    'Apartments': 'Real Estate',
    'Houses': 'Real Estate',
    'Fiction': 'Books',
    'Textbooks': 'Books',
    'Bicycles': 'Sports',
    'Fitness': 'Sports',
    'Board Games': 'Toys',
}

PRODUCT_TO_SUBCATEGORY = {
    'iPhone 15 Pro': 'Smartphones',
    'MacBook Air M2': 'Laptops',
    'IKEA Klippan Sofa': 'Sofas',
    'Oak Dining Table': 'Tables',
    'Cotton T-Shirt': 'T-Shirts',
    'Slim Fit Jeans': 'Jeans',
    'Toyota Camry 2022': 'Cars',
    'Yamaha MT-07': 'Motorcycles',
    '2-Room Apartment': 'Apartments',
    'Country House': 'Houses',
    'The Great Gatsby': 'Fiction',
    'Calculus Textbook': 'Textbooks',
    'Mountain Bicycle': 'Bicycles',
    'Yoga Mat': 'Fitness',
    'Chess Set': 'Board Games',
}


def fix_links():
    fixed_sub = 0
    for sub_name, cat_name in SUBCATEGORY_TO_CATEGORY.items():
        category = Category.objects.filter(category_name=cat_name).first()
        if not category:
            continue
        updated = SubCategory.objects.filter(subcategory_name=sub_name).exclude(
            category_id=category.id
        ).update(category_id=category.id)
        fixed_sub += updated

    fixed_prod = 0
    for prod_name, sub_name in PRODUCT_TO_SUBCATEGORY.items():
        subcategory = SubCategory.objects.filter(subcategory_name=sub_name).first()
        if not subcategory:
            continue
        updated = Product.objects.filter(product_name=prod_name).exclude(
            subcategory_id=subcategory.id
        ).update(subcategory_id=subcategory.id)
        fixed_prod += updated

    print(f'Исправлено подкатегорий: {fixed_sub}, товаров: {fixed_prod}')


# ---------------------------------------------------------------------------
# Часть 2: настоящие подкатегории для категорий без них
# ---------------------------------------------------------------------------
NEW_SUBCATEGORIES = {
    'Beauty': [('Skincare', 'Уход за кожей'), ('Makeup', 'Макияж')],
    'Garden': [('Garden Tools', 'Садовый инвентарь'), ('Plants', 'Растения')],
    'Pets': [('Pet Food', 'Корм для животных'), ('Pet Toys', 'Игрушки для животных')],
    'Music': [('Musical Instruments', 'Музыкальные инструменты'), ('Vinyl Records', 'Виниловые пластинки')],
    'Tools': [('Power Tools', 'Электроинструменты'), ('Hand Tools', 'Ручные инструменты')],
    'Jewelry': [('Rings', 'Кольца'), ('Necklaces', 'Ожерелья')],
    'Food': [('Snacks', 'Снеки'), ('Beverages', 'Напитки')],
}


# ---------------------------------------------------------------------------
# Часть 3: настоящие названия товаров по каждой категории (15 шт.)
# ---------------------------------------------------------------------------
CATEGORY_PRODUCTS = {
    'Electronics': [
        ('Samsung Galaxy S24', 'Samsung Galaxy S24'),
        ('iPad Air 5th Gen', 'iPad Air 5-го поколения'),
        ('Sony WH-1000XM5 Headphones', 'Наушники Sony WH-1000XM5'),
        ('Dell XPS 13 Laptop', 'Ноутбук Dell XPS 13'),
        ('Apple Watch Series 9', 'Apple Watch Series 9'),
        ('Samsung 55" QLED TV', 'Телевизор Samsung QLED 55"'),
        ('Canon EOS R50 Camera', 'Фотоаппарат Canon EOS R50'),
        ('Nintendo Switch OLED', 'Nintendo Switch OLED'),
        ('JBL Flip 6 Speaker', 'Колонка JBL Flip 6'),
        ('Logitech MX Master 3S Mouse', 'Мышь Logitech MX Master 3S'),
        ('Asus ROG Gaming Laptop', 'Игровой ноутбук Asus ROG'),
        ('Amazon Echo Dot', 'Умная колонка Amazon Echo Dot'),
        ('GoPro Hero 12', 'Экшн-камера GoPro Hero 12'),
        ('Xiaomi Redmi Note 13', 'Xiaomi Redmi Note 13'),
        ('Bose QuietComfort Earbuds', 'Наушники Bose QuietComfort'),
    ],
    'Furniture': [
        ('IKEA Malm Bed Frame', 'Кровать IKEA Malm'),
        ('La-Z-Boy Recliner Chair', 'Кресло-реклайнер La-Z-Boy'),
        ('Herman Miller Aeron Office Chair', 'Офисное кресло Herman Miller Aeron'),
        ('West Elm Bookshelf', 'Книжный шкаф West Elm'),
        ('Wayfair Coffee Table', 'Журнальный столик Wayfair'),
        ('IKEA Poäng Armchair', 'Кресло IKEA Poäng'),
        ('Ashley Furniture Sectional Sofa', 'Угловой диван Ashley Furniture'),
        ('Rustic Wood TV Stand', 'ТВ-тумба из массива дерева'),
        ('Modern Bar Stools (Set of 2)', 'Барные стулья, набор 2 шт.'),
        ('Wardrobe Closet Organizer', 'Шкаф-органайзер для одежды'),
        ('Glass Dining Table Set', 'Обеденный стол со стеклом, комплект'),
        ('Ottoman Storage Bench', 'Банкетка-пуф с ящиком для хранения'),
        ('Bunk Bed for Kids', 'Двухъярусная кровать для детей'),
        ('Standing Desk Converter', 'Приставка для стоячей работы'),
        ('Outdoor Patio Set', 'Комплект уличной мебели'),
    ],
    'Clothing': [
        ("Levi's 501 Original Jeans", "Джинсы Levi's 501 Original"),
        ('Nike Air Max Sneakers', 'Кроссовки Nike Air Max'),
        ('Adidas Hoodie', 'Худи Adidas'),
        ('North Face Winter Jacket', 'Зимняя куртка The North Face'),
        ('Zara Summer Dress', 'Летнее платье Zara'),
        ('H&M Denim Jacket', 'Джинсовая куртка H&M'),
        ('Uniqlo Down Vest', 'Пуховый жилет Uniqlo'),
        ('Polo Ralph Lauren Shirt', 'Рубашка-поло Ralph Lauren'),
        ('Calvin Klein Underwear Set', 'Комплект белья Calvin Klein'),
        ('Champion Sweatpants', 'Спортивные штаны Champion'),
        ('Puma Running Shorts', 'Шорты для бега Puma'),
        ('Wool Winter Scarf', 'Шерстяной зимний шарф'),
        ('Leather Belt', 'Кожаный ремень'),
        ('Baseball Cap', 'Бейсболка'),
        ('Silk Necktie', 'Шёлковый галстук'),
    ],
    'Vehicles': [
        ('Honda Civic 2021', 'Honda Civic 2021'),
        ('Tesla Model 3', 'Tesla Model 3'),
        ('Ford F-150 Pickup', 'Пикап Ford F-150'),
        ('BMW 3 Series', 'BMW 3 серии'),
        ('Volkswagen Golf', 'Volkswagen Golf'),
        ('Mercedes-Benz C-Class', 'Mercedes-Benz C-Class'),
        ('Kia Sportage SUV', 'Kia Sportage'),
        ('Harley-Davidson Sportster', 'Мотоцикл Harley-Davidson Sportster'),
        ('Suzuki GSX-R750', 'Мотоцикл Suzuki GSX-R750'),
        ('Vespa Scooter', 'Скутер Vespa'),
        ('Mountain E-Bike', 'Электровелосипед горный'),
        ('Cargo Trailer for Towing', 'Прицеп для перевозки грузов'),
        ('Jeep Wrangler', 'Jeep Wrangler'),
        ('Hyundai Elantra', 'Hyundai Elantra'),
        ('Chevrolet Camaro', 'Chevrolet Camaro'),
    ],
    'Real Estate': [
        ('Studio Apartment Downtown', 'Студия в центре города'),
        ('3-Bedroom Family House', 'Дом на 3 спальни для семьи'),
        ('Penthouse with City View', 'Пентхаус с видом на город'),
        ('Cottage Near the Lake', 'Коттедж у озера'),
        ('Commercial Office Space', 'Коммерческое офисное помещение'),
        ('Suburban Townhouse', 'Таунхаус в пригороде'),
        ('Duplex for Sale', 'Дуплекс на продажу'),
        ('Countryside Villa', 'Загородная вилла'),
        ('Loft Apartment', 'Лофт-апартаменты'),
        ('Beachfront Condo', 'Кондоминиум у пляжа'),
        ('Land Plot for Construction', 'Земельный участок под застройку'),
        ('Garage for Rent', 'Гараж в аренду'),
        ('Renovated Studio', 'Студия после ремонта'),
        ('Farmhouse with Land', 'Фермерский дом с землёй'),
        ('New Construction Apartment', 'Квартира в новостройке'),
    ],
    'Books': [
        ('To Kill a Mockingbird', '«Убить пересмешника»'),
        ('1984 by George Orwell', '«1984» Джордж Оруэлл'),
        ("Harry Potter and the Sorcerer's Stone", '«Гарри Поттер и философский камень»'),
        ('The Lord of the Rings', '«Властелин колец»'),
        ('Pride and Prejudice', '«Гордость и предубеждение»'),
        ('Introduction to Algorithms', '«Введение в алгоритмы»'),
        ('Clean Code', '«Чистый код»'),
        ('Atomic Habits', '«Атомные привычки»'),
        ('Sapiens: A Brief History of Humankind', '«Sapiens. Краткая история человечества»'),
        ('The Da Vinci Code', '«Код да Винчи»'),
        ('Physics Textbook Grade 10', 'Учебник физики, 10 класс'),
        ('English Grammar in Use', 'Учебник English Grammar in Use'),
        ('World History Encyclopedia', 'Энциклопедия всемирной истории'),
        ('Cooking for Beginners Cookbook', 'Кулинарная книга для начинающих'),
        ('Python Crash Course', '«Python Crash Course»'),
    ],
    'Sports': [
        ('Wilson Tennis Racket', 'Теннисная ракетка Wilson'),
        ('Spalding Basketball', 'Баскетбольный мяч Spalding'),
        ('Adidas Soccer Ball', 'Футбольный мяч Adidas'),
        ('Yoga Mat Premium', 'Коврик для йоги Premium'),
        ('Adjustable Dumbbells Set', 'Разборные гантели, набор'),
        ('Treadmill Home Gym', 'Беговая дорожка для дома'),
        ('Trek Mountain Bike', 'Горный велосипед Trek'),
        ('Swimming Goggles', 'Очки для плавания'),
        ('Boxing Gloves', 'Боксёрские перчатки'),
        ('Skateboard Complete', 'Скейтборд в сборе'),
        ('Camping Tent 4-Person', 'Палатка туристическая на 4 человека'),
        ('Fishing Rod Set', 'Набор удочек для рыбалки'),
        ('Golf Club Set', 'Набор клюшек для гольфа'),
        ('Hiking Backpack 40L', 'Туристический рюкзак 40л'),
        ('Resistance Bands Set', 'Набор резинок для фитнеса'),
    ],
    'Toys': [
        ('LEGO Star Wars Set', 'LEGO Star Wars набор'),
        ('Monopoly Board Game', 'Настольная игра «Монополия»'),
        ('Barbie Dreamhouse', 'Дом мечты Barbie'),
        ('Hot Wheels Track Set', 'Трек Hot Wheels'),
        ("Rubik's Cube", 'Кубик Рубика'),
        ('Nerf Blaster', 'Бластер Nerf'),
        ('Play-Doh Kit', 'Набор пластилина Play-Doh'),
        ('Jigsaw Puzzle 1000 Pieces', 'Пазл на 1000 деталей'),
        ('Remote Control Car', 'Машинка на радиоуправлении'),
        ('Action Figure Set', 'Набор фигурок-героев'),
        ('Checkers Board Game', 'Настольная игра «Шашки»'),
        ('Building Blocks Set', 'Конструктор блочный'),
        ('Plush Teddy Bear', 'Плюшевый медведь'),
        ('Drone for Kids', 'Детский квадрокоптер'),
        ('Science Experiment Kit', 'Набор для научных опытов'),
    ],
    'Beauty': [
        ('Maybelline Mascara', 'Тушь Maybelline'),
        ('La Mer Moisturizer', 'Увлажняющий крем La Mer'),
        ('Nivea Body Lotion', 'Лосьон для тела Nivea'),
        ('MAC Lipstick', 'Помада MAC'),
        ('Neutrogena Face Wash', 'Гель для умывания Neutrogena'),
        ('Olaplex Hair Treatment', 'Уход для волос Olaplex'),
        ('Dyson Airwrap Styler', 'Стайлер Dyson Airwrap'),
        ('CeraVe Moisturizing Cream', 'Увлажняющий крем CeraVe'),
        ('The Ordinary Serum', 'Сыворотка The Ordinary'),
        ('Revlon Hair Dryer', 'Фен Revlon'),
        ('Chanel No. 5 Perfume', 'Духи Chanel №5'),
        ('Eyeshadow Palette', 'Палетка теней для век'),
        ('Electric Facial Cleansing Brush', 'Электрическая щётка для чистки лица'),
        ('Nail Polish Set', 'Набор лаков для ногтей'),
        ('Sunscreen SPF 50', 'Солнцезащитный крем SPF 50'),
    ],
    'Garden': [
        ('Fiskars Garden Shears', 'Садовые ножницы Fiskars'),
        ('Wheelbarrow Heavy Duty', 'Садовая тачка усиленная'),
        ('Garden Hose 50ft', 'Садовый шланг 15м'),
        ('Ceramic Flower Pot Set', 'Керамические горшки, набор'),
        ('Electric Lawn Mower', 'Электрическая газонокосилка'),
        ('Garden Gloves', 'Садовые перчатки'),
        ('Watering Can', 'Лейка для полива'),
        ('Tomato Seeds Pack', 'Семена томатов'),
        ('Outdoor Solar Lights', 'Уличные светильники на солнечных батареях'),
        ('Compost Bin', 'Компостер садовый'),
        ('Garden Rake', 'Садовые грабли'),
        ('Greenhouse Kit', 'Комплект теплицы'),
        ('Bird Feeder', 'Кормушка для птиц'),
        ('Hedge Trimmer', 'Кусторез'),
        ('Potting Soil Bag', 'Мешок грунта для рассады'),
    ],
    'Pets': [
        ('Pedigree Dog Food', 'Корм для собак Pedigree'),
        ('Whiskas Cat Food', 'Корм для кошек Whiskas'),
        ('Pet Carrier Bag', 'Сумка-переноска для животных'),
        ('Dog Leash and Collar Set', 'Поводок и ошейник, комплект'),
        ('Cat Scratching Post', 'Когтеточка для кошки'),
        ('Aquarium Fish Tank', 'Аквариум для рыбок'),
        ('Bird Cage', 'Клетка для птиц'),
        ('Hamster Cage Kit', 'Клетка для хомяка, набор'),
        ('Dog Chew Toys Set', 'Игрушки-грызунки для собак, набор'),
        ('Cat Litter Box', 'Лоток для кошачьего туалета'),
        ('Pet Bed Cushion', 'Лежанка для животного'),
        ('Dog Training Clicker', 'Кликер для дрессировки собак'),
        ('Aquarium Filter', 'Фильтр для аквариума'),
        ('Rabbit Hutch', 'Клетка для кролика'),
        ('Pet Grooming Kit', 'Набор для груминга животных'),
    ],
    'Music': [
        ('Fender Stratocaster Guitar', 'Гитара Fender Stratocaster'),
        ('Yamaha Digital Piano', 'Цифровое пианино Yamaha'),
        ('Roland Electronic Drum Kit', 'Электронная ударная установка Roland'),
        ('Vinyl Record Player', 'Проигрыватель виниловых пластинок'),
        ('Shure SM58 Microphone', 'Микрофон Shure SM58'),
        ('Ukulele Beginner Set', 'Укулеле, набор для начинающих'),
        ('Violin Full Size', 'Скрипка полноразмерная'),
        ('DJ Mixer Controller', 'DJ-контроллер/микшер'),
        ('Acoustic Guitar Case', 'Чехол для акустической гитары'),
        ('Foldable Music Stand', 'Складной пюпитр для нот'),
        ('Harmonica Set', 'Набор губных гармошек'),
        ('Studio Headphones', 'Студийные наушники'),
        ('Bluetooth Karaoke Machine', 'Караоке-система с Bluetooth'),
        ('Alto Saxophone', 'Саксофон альт'),
        ('Guitar Amplifier', 'Гитарный усилитель'),
    ],
    'Tools': [
        ('DeWalt Power Drill', 'Дрель DeWalt'),
        ('Bosch Circular Saw', 'Циркулярная пила Bosch'),
        ('Stanley Tool Set', 'Набор инструментов Stanley'),
        ('Milwaukee Impact Wrench', 'Ударный гайковёрт Milwaukee'),
        ('Craftsman Tool Box', 'Ящик для инструментов Craftsman'),
        ('Angle Grinder', 'Угловая шлифмашина (болгарка)'),
        ('Cordless Screwdriver Set', 'Аккумуляторная отвёртка, набор'),
        ('Measuring Tape 25ft', 'Рулетка измерительная 7.5м'),
        ('Adjustable Wrench Set', 'Набор разводных ключей'),
        ('Steel Claw Hammer', 'Молоток стальной'),
        ('Socket Wrench Set', 'Набор торцевых ключей'),
        ('Workbench with Vise', 'Верстак с тисками'),
        ('Electric Sander', 'Электрическая шлифмашина'),
        ('Aluminum Ladder 6ft', 'Алюминиевая стремянка 1.8м'),
        ('Digital Multimeter', 'Цифровой мультиметр'),
    ],
    'Jewelry': [
        ('Gold Wedding Ring', 'Золотое обручальное кольцо'),
        ('Silver Necklace Pendant', 'Серебряное колье с подвеской'),
        ('Diamond Stud Earrings', 'Серьги-гвоздики с бриллиантами'),
        ('Pearl Bracelet', 'Браслет из жемчуга'),
        ("Men's Leather Watch", 'Мужские часы с кожаным ремешком'),
        ('Rose Gold Ring', 'Кольцо из розового золота'),
        ('Sapphire Pendant Necklace', 'Колье с сапфировой подвеской'),
        ('Charm Bracelet', 'Браслет с шармами'),
        ('Cufflinks Set', 'Набор запонок'),
        ('Anklet Chain', 'Цепочка на щиколотку'),
        ('Birthstone Ring', 'Кольцо с камнем по месяцу рождения'),
        ('Titanium Wedding Band', 'Обручальное кольцо из титана'),
        ('Vintage Brooch', 'Винтажная брошь'),
        ('Tissot Wristwatch', 'Наручные часы Tissot'),
        ('Gemstone Earrings', 'Серьги с самоцветами'),
    ],
    'Food': [
        ('Organic Honey Jar', 'Банка органического мёда'),
        ('Extra Virgin Olive Oil', 'Оливковое масло Extra Virgin'),
        ('Ground Coffee Beans', 'Молотый кофе в зёрнах'),
        ('Green Tea Box', 'Зелёный чай, упаковка'),
        ('Dark Chocolate Bar', 'Плитка тёмного шоколада'),
        ('Italian Pasta Pack', 'Итальянские макароны, упаковка'),
        ('Basmati Rice 5kg', 'Рис Басмати 5кг'),
        ('Canned Tomatoes', 'Томаты консервированные'),
        ('Mixed Nuts Pack', 'Ореховая смесь'),
        ('Maple Syrup Bottle', 'Кленовый сироп, бутылка'),
        ('Spice Set Variety Pack', 'Набор специй ассорти'),
        ('Sparkling Water Case', 'Газированная вода, упаковка'),
        ('Peanut Butter Jar', 'Арахисовая паста, банка'),
        ('Family Size Cereal Box', 'Хлопья для завтрака, семейная упаковка'),
        ('Red Wine Bottle', 'Бутылка красного вина'),
    ],
}

REVIEW_COMMENTS = [
    'Отличный товар, всё как описано.',
    'Быстрая доставка и хорошая упаковка.',
    'Качество могло быть лучше за эту цену.',
    'Превзошло ожидания, куплю ещё раз.',
    'Идеальное состояние, как на фото.',
    'Хорошее соотношение цены и качества.',
    'Неплохо, но доставка была дольше, чем ожидалось.',
    'Отличный продавец, быстро отвечает.',
    'Работает нормально, пока нет жалоб.',
    'Очень рекомендую этого продавца.',
    'Средний опыт, ничего особенного.',
    'Очень доволен покупкой.',
]


def set_translated(obj, field, en_value, ru_value):
    if hasattr(obj, f'{field}_en'):
        setattr(obj, f'{field}_en', en_value)
    if hasattr(obj, f'{field}_ru'):
        setattr(obj, f'{field}_ru', ru_value)
    setattr(obj, field, en_value)


def ensure_subcategories(category):
    """Возвращает список подкатегорий категории, создавая тематические,
    если их ещё нет."""
    subcategories = list(SubCategory.objects.filter(category=category))
    if subcategories:
        return subcategories

    new_names = NEW_SUBCATEGORIES.get(category.category_name, [('General', 'Разное')])
    created = []
    for name_en, name_ru in new_names:
        sub, was_created = SubCategory.objects.get_or_create(
            category=category,
            subcategory_name=name_en,
        )
        if was_created:
            set_translated(sub, 'subcategory_name', name_en, name_ru)
            sub.save()
            print(f'  + создана подкатегория "{name_en}" для {category}')
        created.append(sub)
    return created


def add_products_and_reviews():
    categories = list(Category.objects.all().order_by('id'))
    if not categories:
        print('Нет ни одной категории — сначала создайте категории.')
        return

    reviewers = list(UserProfile.objects.all())
    if not reviewers:
        print('Нет ни одного пользователя — отзывы добавлены не будут (только товары).')

    total_products = 0
    total_reviews = 0

    for category in categories:
        subcategories = ensure_subcategories(category)
        names = CATEGORY_PRODUCTS.get(category.category_name, [])

        created_for_category = 0
        for n, (name_en, name_ru) in enumerate(names, start=1):
            if Product.objects.filter(product_name=name_en).exists():
                continue  # уже добавляли — пропускаем, чтобы не дублировать

            subcategory = subcategories[(n - 1) % len(subcategories)]
            article_number = (
                Product.objects.aggregate(m=Max('article_number'))['m'] or 0
            ) + 1

            product = Product(
                subcategory=subcategory,
                price=Decimal(str(round(random.uniform(5, 500), 2))),
                article_number=article_number,
                product_type=bool(n % 2),
            )
            set_translated(product, 'product_name', name_en, name_ru)
            set_translated(
                product, 'description',
                f'{name_en}. Good condition, ready to ship.',
                f'{name_ru}. Хорошее состояние, готов к отправке.',
            )
            # Фото товара намеренно не генерируем — добавите сами через админку.
            product.save()
            created_for_category += 1

            if reviewers:
                review_count = random.randint(2, 5)
                chosen_users = random.sample(reviewers, min(review_count, len(reviewers)))
                for user in chosen_users:
                    Review.objects.create(
                        user=user,
                        product=product,
                        stars=random.randint(2, 5),
                        comment=random.choice(REVIEW_COMMENTS),
                        # review_image тоже не генерируем — необязательно.
                    )
                    total_reviews += 1

        total_products += created_for_category
        print(f'{category}: +{created_for_category} товаров')

    print(f'\nВсего добавлено товаров: {total_products}')
    print(f'Всего добавлено отзывов/оценок: {total_reviews}')


def main():
    with transaction.atomic():
        print('Шаг 1: исправляем связи категорий/подкатегорий/товаров...')
        fix_links()
        print('\nШаг 2: добавляем подкатегории + товары + отзывы...')
        add_products_and_reviews()
    print('\nВСЁ ГОТОВО. Фото товаров/отзывов не создавались — добавьте их через Django admin.')


if __name__ == '__main__':
    main()
