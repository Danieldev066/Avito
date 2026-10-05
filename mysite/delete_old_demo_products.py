"""
delete_old_demo_products.py
----------------------------
Удаляет ТОЛЬКО старые товары с "ненастоящими" автосгенерированными
названиями (вида "Category Item 1", "Premium Electronics #1" и т.п.),
которые могли появиться, если запускались более ранние версии
fix_and_add_products.py.

НЕ трогает:
- 15 оригинальных товаров из seed_data.py (iPhone 15 Pro, MacBook Air
  M2 и т.д.)
- товары с настоящими названиями из последней версии
  fix_and_add_products.py (Samsung Galaxy S24, Tesla Model 3 и т.д.)
- пользователей, корзины и т.д.

При удалении товара автоматически удаляются связанные с ним отзывы
(они были созданы тем же скриптом для этих же "ненастоящих" товаров).

КАК ЗАПУСТИТЬ
Положите рядом с manage.py:
    C:\\Users\\user\\PycharmProjects\\AvitoSait\\mysite\\delete_old_demo_products.py

Затем (venv активирован):
    python delete_old_demo_products.py
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django  # noqa: E402

django.setup()

from avito_app.models import Product  # noqa: E402


# Оригинальные 15 товаров из seed_data.py — их не трогаем.
ORIGINAL_NAMES = {
    'iPhone 15 Pro', 'MacBook Air M2', 'IKEA Klippan Sofa', 'Oak Dining Table',
    'Cotton T-Shirt', 'Slim Fit Jeans', 'Toyota Camry 2022', 'Yamaha MT-07',
    '2-Room Apartment', 'Country House', 'The Great Gatsby', 'Calculus Textbook',
    'Mountain Bicycle', 'Yoga Mat', 'Chess Set',
}

# Настоящие названия из последней версии fix_and_add_products.py —
# их тоже не трогаем (на случай, если она уже успела отработать).
REAL_NAMES = {
    'Samsung Galaxy S24', 'iPad Air 5th Gen', 'Sony WH-1000XM5 Headphones',
    'Dell XPS 13 Laptop', 'Apple Watch Series 9', 'Samsung 55" QLED TV',
    'Canon EOS R50 Camera', 'Nintendo Switch OLED', 'JBL Flip 6 Speaker',
    'Logitech MX Master 3S Mouse', 'Asus ROG Gaming Laptop', 'Amazon Echo Dot',
    'GoPro Hero 12', 'Xiaomi Redmi Note 13', 'Bose QuietComfort Earbuds',
    'IKEA Malm Bed Frame', 'La-Z-Boy Recliner Chair', 'Herman Miller Aeron Office Chair',
    'West Elm Bookshelf', 'Wayfair Coffee Table', 'IKEA Poäng Armchair',
    'Ashley Furniture Sectional Sofa', 'Rustic Wood TV Stand', 'Modern Bar Stools (Set of 2)',
    'Wardrobe Closet Organizer', 'Glass Dining Table Set', 'Ottoman Storage Bench',
    'Bunk Bed for Kids', 'Standing Desk Converter', 'Outdoor Patio Set',
    "Levi's 501 Original Jeans", 'Nike Air Max Sneakers', 'Adidas Hoodie',
    'North Face Winter Jacket', 'Zara Summer Dress', 'H&M Denim Jacket',
    'Uniqlo Down Vest', 'Polo Ralph Lauren Shirt', 'Calvin Klein Underwear Set',
    'Champion Sweatpants', 'Puma Running Shorts', 'Wool Winter Scarf',
    'Leather Belt', 'Baseball Cap', 'Silk Necktie',
    'Honda Civic 2021', 'Tesla Model 3', 'Ford F-150 Pickup', 'BMW 3 Series',
    'Volkswagen Golf', 'Mercedes-Benz C-Class', 'Kia Sportage SUV',
    'Harley-Davidson Sportster', 'Suzuki GSX-R750', 'Vespa Scooter',
    'Mountain E-Bike', 'Cargo Trailer for Towing', 'Jeep Wrangler',
    'Hyundai Elantra', 'Chevrolet Camaro',
    'Studio Apartment Downtown', '3-Bedroom Family House', 'Penthouse with City View',
    'Cottage Near the Lake', 'Commercial Office Space', 'Suburban Townhouse',
    'Duplex for Sale', 'Countryside Villa', 'Loft Apartment', 'Beachfront Condo',
    'Land Plot for Construction', 'Garage for Rent', 'Renovated Studio',
    'Farmhouse with Land', 'New Construction Apartment',
    'To Kill a Mockingbird', '1984 by George Orwell',
    "Harry Potter and the Sorcerer's Stone", 'The Lord of the Rings',
    'Pride and Prejudice', 'Introduction to Algorithms', 'Clean Code',
    'Atomic Habits', 'Sapiens: A Brief History of Humankind', 'The Da Vinci Code',
    'Physics Textbook Grade 10', 'English Grammar in Use', 'World History Encyclopedia',
    'Cooking for Beginners Cookbook', 'Python Crash Course',
    'Wilson Tennis Racket', 'Spalding Basketball', 'Adidas Soccer Ball',
    'Yoga Mat Premium', 'Adjustable Dumbbells Set', 'Treadmill Home Gym',
    'Trek Mountain Bike', 'Swimming Goggles', 'Boxing Gloves', 'Skateboard Complete',
    'Camping Tent 4-Person', 'Fishing Rod Set', 'Golf Club Set',
    'Hiking Backpack 40L', 'Resistance Bands Set',
    'LEGO Star Wars Set', 'Monopoly Board Game', 'Barbie Dreamhouse',
    'Hot Wheels Track Set', "Rubik's Cube", 'Nerf Blaster', 'Play-Doh Kit',
    'Jigsaw Puzzle 1000 Pieces', 'Remote Control Car', 'Action Figure Set',
    'Checkers Board Game', 'Building Blocks Set', 'Plush Teddy Bear',
    'Drone for Kids', 'Science Experiment Kit',
    'Maybelline Mascara', 'La Mer Moisturizer', 'Nivea Body Lotion', 'MAC Lipstick',
    'Neutrogena Face Wash', 'Olaplex Hair Treatment', 'Dyson Airwrap Styler',
    'CeraVe Moisturizing Cream', 'The Ordinary Serum', 'Revlon Hair Dryer',
    'Chanel No. 5 Perfume', 'Eyeshadow Palette', 'Electric Facial Cleansing Brush',
    'Nail Polish Set', 'Sunscreen SPF 50',
    'Fiskars Garden Shears', 'Wheelbarrow Heavy Duty', 'Garden Hose 50ft',
    'Ceramic Flower Pot Set', 'Electric Lawn Mower', 'Garden Gloves', 'Watering Can',
    'Tomato Seeds Pack', 'Outdoor Solar Lights', 'Compost Bin', 'Garden Rake',
    'Greenhouse Kit', 'Bird Feeder', 'Hedge Trimmer', 'Potting Soil Bag',
    'Pedigree Dog Food', 'Whiskas Cat Food', 'Pet Carrier Bag',
    'Dog Leash and Collar Set', 'Cat Scratching Post', 'Aquarium Fish Tank',
    'Bird Cage', 'Hamster Cage Kit', 'Dog Chew Toys Set', 'Cat Litter Box',
    'Pet Bed Cushion', 'Dog Training Clicker', 'Aquarium Filter', 'Rabbit Hutch',
    'Pet Grooming Kit',
    'Fender Stratocaster Guitar', 'Yamaha Digital Piano', 'Roland Electronic Drum Kit',
    'Vinyl Record Player', 'Shure SM58 Microphone', 'Ukulele Beginner Set',
    'Violin Full Size', 'DJ Mixer Controller', 'Acoustic Guitar Case',
    'Foldable Music Stand', 'Harmonica Set', 'Studio Headphones',
    'Bluetooth Karaoke Machine', 'Alto Saxophone', 'Guitar Amplifier',
    'DeWalt Power Drill', 'Bosch Circular Saw', 'Stanley Tool Set',
    'Milwaukee Impact Wrench', 'Craftsman Tool Box', 'Angle Grinder',
    'Cordless Screwdriver Set', 'Measuring Tape 25ft', 'Adjustable Wrench Set',
    'Steel Claw Hammer', 'Socket Wrench Set', 'Workbench with Vise',
    'Electric Sander', 'Aluminum Ladder 6ft', 'Digital Multimeter',
    'Gold Wedding Ring', 'Silver Necklace Pendant', 'Diamond Stud Earrings',
    'Pearl Bracelet', "Men's Leather Watch", 'Rose Gold Ring',
    'Sapphire Pendant Necklace', 'Charm Bracelet', 'Cufflinks Set', 'Anklet Chain',
    'Birthstone Ring', 'Titanium Wedding Band', 'Vintage Brooch',
    'Tissot Wristwatch', 'Gemstone Earrings',
    'Organic Honey Jar', 'Extra Virgin Olive Oil', 'Ground Coffee Beans',
    'Green Tea Box', 'Dark Chocolate Bar', 'Italian Pasta Pack', 'Basmati Rice 5kg',
    'Canned Tomatoes', 'Mixed Nuts Pack', 'Maple Syrup Bottle',
    'Spice Set Variety Pack', 'Sparkling Water Case', 'Peanut Butter Jar',
    'Family Size Cereal Box', 'Red Wine Bottle',
}

KEEP_NAMES = ORIGINAL_NAMES | REAL_NAMES


def main():
    to_delete = Product.objects.exclude(product_name__in=KEEP_NAMES)
    count = to_delete.count()

    if count == 0:
        print('Старых "ненастоящих" товаров не найдено — удалять нечего.')
        return

    print(f'Найдено {count} старых товаров с автосгенерированными названиями:')
    for name in to_delete.values_list('product_name', flat=True)[:20]:
        print(f'  - {name}')
    if count > 20:
        print(f'  ... и ещё {count - 20}')

    answer = input('\nУдалить эти товары (и их отзывы)? Введите "да" для подтверждения: ')
    if answer.strip().lower() not in ('да', 'yes', 'y'):
        print('Отменено, ничего не удалено.')
        return

    deleted, details = to_delete.delete()
    print(f'\nУдалено объектов всего: {deleted}')
    for model, n in details.items():
        print(f'  {model}: {n}')


if __name__ == '__main__':
    main()
