"""
Management command: python manage.py load_orders

mock_orders.json faylidan buyurtmalarni bazaga yuklaydi.
50 000 ₸ dan oshgan buyurtmalar uchun Telegram bildirishnomasi yuboriladi.
"""
import json
import os
from decimal import Decimal
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from app.models import Order


MOCK_FILE = Path(settings.BASE_DIR) / 'gbc-analytics-dashboard' / 'mock_orders.json'


def _send_telegram(order):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        return
    text = (
        f"🛒 *Katta buyurtma keldi!*\n\n"
        f"👤 *Mijoz:* {order.first_name} {order.last_name}\n"
        f"📞 *Telefon:* {order.phone}\n"
        f"🏙️ *Shahar:* {order.city or '—'}\n"
        f"📦 *Mahsulotlar:* {order.product_names or '—'}\n"
        f"💰 *Summa:* {order.total_price:,.0f} ₸\n"
        f"🔗 *Manba:* {order.utm_source or 'direct'}"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=5)
    except requests.RequestException:
        pass


class Command(BaseCommand):
    help = 'mock_orders.json dan buyurtmalarni bazaga yuklaydi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Yuklashdan oldin mavjud buyurtmalarni o\'chirish',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = Order.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'{deleted} ta buyurtma o\'chirildi.'))

        if not MOCK_FILE.exists():
            self.stdout.write(self.style.ERROR(f'Fayl topilmadi: {MOCK_FILE}'))
            return

        with open(MOCK_FILE, encoding='utf-8') as f:
            raw_orders = json.load(f)

        created_count = 0
        notified_count = 0

        for data in raw_orders:
            items = data.get('items', [])
            total_price = sum(
                Decimal(str(item.get('initialPrice', 0))) * int(item.get('quantity', 1))
                for item in items
            )
            product_names = ', '.join(
                item.get('productName', '') for item in items if item.get('productName')
            )
            items_count = sum(int(i.get('quantity', 1)) for i in items)

            order = Order.objects.create(
                first_name=data.get('firstName', ''),
                last_name=data.get('lastName', ''),
                phone=data.get('phone', ''),
                email=data.get('email', ''),
                status=data.get('status', 'new'),
                city=data.get('delivery', {}).get('address', {}).get('city', ''),
                utm_source=data.get('customFields', {}).get('utm_source', ''),
                total_price=total_price,
                items_count=items_count,
                product_names=product_names,
            )
            created_count += 1

            if order.total_price > Decimal('50000'):
                _send_telegram(order)
                notified_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  🔔 Telegram: {order.first_name} {order.last_name} — {order.total_price:,.0f} ₸'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ {created_count} ta buyurtma yuklandi. '
                f'{notified_count} ta Telegram bildirishnomasi yuborildi.'
            )
        )
