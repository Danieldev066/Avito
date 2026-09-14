"""
seed_data.py
------------
Скрипт для заполнения базы данных проекта AvitoSait тестовыми данными:
по 15 записей на каждую модель (UserProfile, Category, SubCategory,
Product, ProductImage, Review), включая переводы EN/RU для полей,
зарегистрированных через django-modeltranslation.

КАК ЗАПУСТИТЬ
1. Положите этот файл рядом с manage.py, т.е. в:
   C:\\Users\\user\\PycharmProjects\\AvitoSait\\mysite\\seed_data.py

2. Активируйте venv (если ещё не активирован) и запустите:
   python seed_data.py

   Скрипт сам настроит Django (DJANGO_SETTINGS_MODULE) и выполнит сидинг
   внутри одной транзакции. При повторном запуске старые тестовые данные
   (кроме суперпользователей) будут удалены и созданы заново.

ПРИМЕЧАНИЕ ПРО ПЕРЕВОДЫ
Скрипт не знает точно, какие поля зарегистрированы в вашем
avito_app/translation.py. Поэтому используется вспомогательная функция
set_translated(), которая проверяет наличие полей `<field>_en` /
`<field>_ru` через hasattr и заполняет их, если они есть, а также всегда
заполняет базовое поле (на случай, если modeltranslation не подключен
к этому полю). Работает независимо от точного содержимого translation.py.

ПРИМЕЧАНИЕ ПРО ИЗОБРАЖЕНИЯ
Поля ImageField (avatar, category_image, subcategory_image,
product_image) обязательны (не blank/null), поэтому для каждой записи
генерируется небольшая JPEG-заглушка "на лету" через Pillow и
сохраняется в MEDIA_ROOT через ContentFile — реальные файлы на диск не
нужны.
"""

import io
import os
import random
import sys
from decimal import Decimal
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Настройка Django, чтобы скрипт можно было запускать как обычный .py файл
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django  # noqa: E402

django.setup()

from django.core.files.base import ContentFile  # noqa: E402
from django.db import transaction  # noqa: E402
from PIL import Image  # noqa: E402

from avito_app.models import (  # noqa: E402
    Category,
    Product,
    ProductImage,
    Review,
    SubCategory,
    UserProfile,
)

N = 15  # количество записей на каждую модель


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------
def make_image_file(name: str, color: tuple) -> ContentFile:
    """Генерирует простое JPEG-изображение 100x100 нужного цвета в памяти."""
    buffer = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=color)
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return ContentFile(buffer.read(), name=name)


def random_color(seed: int) -> tuple:
    random.seed(seed)
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def set_translated(obj, field: str, en_value: str, ru_value: str) -> None:
    """
    Заполняет поле с учётом django-modeltranslation: если существуют
    `<field>_en` / `<field>_ru`, заполняет их. В любом случае заполняет
    базовое поле `field` значением на английском (язык по умолчанию).
    """
    if hasattr(obj, f"{field}_en"):
        setattr(obj, f"{field}_en", en_value)
    if hasattr(obj, f"{field}_ru"):
        setattr(obj, f"{field}_ru", ru_value)
    setattr(obj, field, en_value)


# ---------------------------------------------------------------------------
# Данные для заполнения (EN / RU)
# ---------------------------------------------------------------------------
CATEGORY_NAMES = [
    ("Electronics", "Электроника"),
    ("Furniture", "Мебель"),
    ("Clothing", "Одежда"),
    ("Vehicles", "Транспорт"),
    ("Real Estate", "Недвижимость"),
    ("Books", "Книги"),
    ("Sports", "Спорт"),
    ("Toys", "Игрушки"),
    ("Beauty", "Красота"),
    ("Garden", "Сад"),
    ("Pets", "Животные"),
    ("Music", "Музыка"),
    ("Tools", "Инструменты"),
    ("Jewelry", "Ювелирные изделия"),
    ("Food", "Продукты"),
]

SUBCATEGORY_NAMES = [
    ("Smartphones", "Смартфоны"),
    ("Laptops", "Ноутбуки"),
    ("Sofas", "Диваны"),
    ("Tables", "Столы"),
    ("T-Shirts", "Футболки"),
    ("Jeans", "Джинсы"),
    ("Cars", "Автомобили"),
    ("Motorcycles", "Мотоциклы"),
    ("Apartments", "Квартиры"),
    ("Houses", "Дома"),
    ("Fiction", "Художественная литература"),
    ("Textbooks", "Учебники"),
    ("Bicycles", "Велосипеды"),
    ("Fitness", "Фитнес"),
    ("Board Games", "Настольные игры"),
]

# (name_en, name_ru, description_en, description_ru, price)
PRODUCT_DATA = [
    ("iPhone 15 Pro", "iPhone 15 Pro",
     "Flagship smartphone with A17 Pro chip and titanium body.",
     "Флагманский смартфон с чипом A17 Pro и титановым корпусом.", "999.99"),
    ("MacBook Air M2", "MacBook Air M2",
     "Lightweight laptop with M2 chip and all-day battery life.",
     "Лёгкий ноутбук с чипом M2 и автономностью на весь день.", "1199.00"),
    ("IKEA Klippan Sofa", "Диван IKEA Klippan",
     "Compact two-seat sofa with easy-to-clean removable covers.",
     "Компактный двухместный диван со съёмными чехлами.", "349.50"),
    ("Oak Dining Table", "Дубовый обеденный стол",
     "Solid oak table that seats six, handcrafted finish.",
     "Стол из массива дуба на шесть персон, ручная работа.", "520.00"),
    ("Cotton T-Shirt", "Хлопковая футболка",
     "100% cotton t-shirt available in multiple colors.",
     "Футболка из 100% хлопка, доступна в разных цветах.", "15.99"),
    ("Slim Fit Jeans", "Джинсы slim fit",
     "Classic denim jeans with a slim fit cut.",
     "Классические джинсы кроя slim fit.", "45.00"),
    ("Toyota Camry 2022", "Toyota Camry 2022",
     "Reliable sedan with low mileage, one owner.",
     "Надёжный седан с небольшим пробегом, один владелец.", "24500.00"),
    ("Yamaha MT-07", "Yamaha MT-07",
     "Sporty naked motorcycle, great for city riding.",
     "Спортивный нейкед-мотоцикл, отлично подходит для города.", "7800.00"),
    ("2-Room Apartment", "2-комнатная квартира",
     "Cozy apartment near the city center, recently renovated.",
     "Уютная квартира рядом с центром города, недавно отремонтирована.", "65000.00"),
    ("Country House", "Загородный дом",
     "Spacious house with a garden, ideal for families.",
     "Просторный дом с садом, идеально подходит для семьи.", "120000.00"),
    ("The Great Gatsby", "Великий Гэтсби",
     "Classic novel by F. Scott Fitzgerald.",
     "Классический роман Фрэнсиса Скотта Фицджеральда.", "9.99"),
    ("Calculus Textbook", "Учебник по мат. анализу",
     "Comprehensive textbook covering calculus fundamentals.",
     "Подробный учебник по основам математического анализа.", "39.90"),
    ("Mountain Bicycle", "Горный велосипед",
     "21-speed mountain bike with an aluminum frame.",
     "Горный велосипед с алюминиевой рамой и 21 скоростью.", "310.00"),
    ("Yoga Mat", "Коврик для йоги",
     "Non-slip yoga mat made of eco-friendly material.",
     "Нескользящий коврик для йоги из экологичного материала.", "22.00"),
    ("Chess Set", "Шахматный набор",
     "Wooden chess set with hand-carved pieces.",
     "Деревянный шахматный набор с резными фигурами.", "34.50"),
]

REVIEW_COMMENTS = [
    "Great product, exactly as described.",
    "Fast delivery and good packaging.",
    "Quality could be better for the price.",
    "Exceeded my expectations, will buy again.",
    "Item arrived damaged, but seller resolved it quickly.",
    "Perfect condition, just as in the photos.",
    "Good value for money.",
    "Not bad, but shipping took longer than expected.",
    "Excellent seller, very responsive.",
    "Works fine, no complaints so far.",
    "A bit smaller than I imagined, but still happy.",
    "Highly recommend this seller.",
    "Average experience, nothing special.",
    "Very satisfied with the purchase.",
    "Would buy from this seller again.",
]


# ---------------------------------------------------------------------------
# Функции создания записей
# ---------------------------------------------------------------------------
def create_users():
    statuses = ["gold", "silver", "bronze", "simple"]
    users = []
    for i in range(1, N + 1):
        user = UserProfile(
            username=f"user{i}",
            email=f"user{i}@example.com",
            age=random.randint(16, 90),
            phone_number=f"+996700{i:06d}",
            status=statuses[i % len(statuses)],
        )
        user.set_password("password123")
        user.avatar.save(
            f"avatar_{i}.jpg",
            make_image_file(f"avatar_{i}.jpg", random_color(i)),
            save=False,
        )
        user.save()
        users.append(user)
    print(f"Создано пользователей: {len(users)}")
    return users


def create_categories():
    categories = []
    for i, (en, ru) in enumerate(CATEGORY_NAMES, start=1):
        cat = Category()
        set_translated(cat, "category_name", en, ru)
        cat.category_image.save(
            f"category_{i}.jpg",
            make_image_file(f"category_{i}.jpg", random_color(i + 100)),
            save=False,
        )
        cat.save()
        categories.append(cat)
    print(f"Создано категорий: {len(categories)}")
    return categories


def create_subcategories(categories):
    subcategories = []
    for i, (en, ru) in enumerate(SUBCATEGORY_NAMES, start=1):
        sub = SubCategory(category=categories[i % len(categories)])
        set_translated(sub, "subcategory_name", en, ru)
        sub.subcategory_image.save(
            f"subcategory_{i}.jpg",
            make_image_file(f"subcategory_{i}.jpg", random_color(i + 200)),
            save=False,
        )
        sub.save()
        subcategories.append(sub)
    print(f"Создано подкатегорий: {len(subcategories)}")
    return subcategories


def create_products(subcategories):
    products = []
    for i, (name_en, name_ru, desc_en, desc_ru, price) in enumerate(PRODUCT_DATA, start=1):
        product = Product(
            subcategory=subcategories[i % len(subcategories)],
            price=Decimal(price),
            article_number=1_000_000 + i,
            product_type=bool(i % 2),
        )
        set_translated(product, "product_name", name_en, name_ru)
        set_translated(product, "description", desc_en, desc_ru)
        product.save()
        products.append(product)
    print(f"Создано товаров: {len(products)}")
    return products


def create_product_images(products):
    images = []
    for i, product in enumerate(products, start=1):
        pi = ProductImage(product=product)
        pi.product_image.save(
            f"product_{i}.jpg",
            make_image_file(f"product_{i}.jpg", random_color(i + 300)),
            save=False,
        )
        pi.save()
        images.append(pi)
    print(f"Создано изображений товаров: {len(images)}")
    return images


def create_reviews(users, products):
    reviews = []
    for i in range(1, N + 1):
        review = Review(
            user=users[i % len(users)],
            product=products[i % len(products)],
            stars=random.randint(1, 5),
            comment=REVIEW_COMMENTS[i - 1],
        )
        review.save()
        reviews.append(review)
    print(f"Создано отзывов: {len(reviews)}")
    return reviews


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------
def clear_old_data():
    Review.objects.all().delete()
    ProductImage.objects.all().delete()
    Product.objects.all().delete()
    SubCategory.objects.all().delete()
    Category.objects.all().delete()
    UserProfile.objects.filter(is_superuser=False).delete()


def main():
    with transaction.atomic():
        print("Очистка старых тестовых данных...")
        clear_old_data()

        users = create_users()
        categories = create_categories()
        subcategories = create_subcategories(categories)
        products = create_products(subcategories)
        create_product_images(products)
        create_reviews(users, products)

    print("\nГотово! По 15 записей создано для каждой модели (с переводами EN/RU).")


if __name__ == "__main__":
    main()
