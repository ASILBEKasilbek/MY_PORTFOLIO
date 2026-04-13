import json
import requests
import logging
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Skills, Project, ContactMessage, SiteSettings, Order

logger = logging.getLogger(__name__)


def send_telegram_message(name, phone, message):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        return
    text = f"📩 *Yangi xabar!*\n\n👤 *Ism:* {name}\n📞 *Telefon:* {phone}\n📝 *Xabar:* {message}"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        logger.info(f"Telegram: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Telegram xato: {e}")


def home(request):
    projects = Project.objects.all().order_by('-created_at')
    skills = Skills.objects.all().order_by('-percent')
    site = SiteSettings.get_settings()
    typing_phrases = [p.strip() for p in site.typing_phrases.split('\n') if p.strip()]
    about_tags = [t.strip() for t in site.about_tags.split('\n') if t.strip()]

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        msg = request.POST.get("message", "").strip()

        if name and phone and msg:
            ContactMessage.objects.create(name=name, phone=phone, message=msg)
            send_telegram_message(name, phone, msg)
            messages.success(request, "Xabaringiz muvaffaqiyatli yuborildi! Tez orada bog'lanaman.")
            return redirect('home')

    return render(request, 'home5.html', {
        'projects': projects,
        'skills': skills,
        'site': site,
        'typing_phrases_json': json.dumps(typing_phrases),
        'about_tags': about_tags,
    })


def resume(request):
    skill_categories = [
        {'name': 'Backend', 'icon': 'fa fa-server', 'skills': ['Python', 'Django', 'Django REST Framework']},
        {'name': "Ma'lumotlar bazasi", 'icon': 'fa fa-database', 'skills': ['PostgreSQL', 'MSSQL', 'SQLite']},
        {'name': 'Real-time', 'icon': 'fa fa-bolt', 'skills': ['WebSocket', 'Celery', 'Django Channels', 'Redis']},
        {'name': 'Frontend', 'icon': 'fa fa-palette', 'skills': ['HTML5', 'CSS3', 'Django Templates']},
        {'name': 'DevOps / CI/CD', 'icon': 'fab fa-docker', 'skills': ['Docker', 'Docker Compose', 'GitHub Actions', 'Bash']},
        {'name': 'Telegram Bot', 'icon': 'fab fa-telegram', 'skills': ['Python', 'Aiogram 3']},
        {'name': 'AI / ML', 'icon': 'fa fa-brain', 'skills': ['NumPy', 'OpenAI API (GPT-4)']},
        {'name': 'Versiya nazorati', 'icon': 'fab fa-git-alt', 'skills': ['Git', 'GitHub', 'GitLab']},
        {'name': 'Sinov', 'icon': 'fa fa-vial', 'skills': ['Postman', 'Swagger', 'Pytest']},
    ]
    return render(request, 'resume.html', {'skill_categories': skill_categories})


# ─── Dashboard (/topshiriq) ─────────────────────────────────────────

def send_order_telegram_notification(order):
    """Buyurtma 50,000 ₸ dan oshsa Telegram'ga xabar yuborish."""
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
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        logger.info(f"Order Telegram notification: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Order Telegram xato: {e}")


def topshiriq_dashboard(request):
    orders = Order.objects.all()
    total_orders = orders.count()
    total_revenue = orders.aggregate(s=Sum('total_price'))['s'] or 0
    big_orders = orders.filter(total_price__gt=50000).count()
    avg_order = (total_revenue / total_orders) if total_orders else 0

    # Chart: buyurtmalar manbasi bo'yicha (utm_source)
    by_source = list(
        orders.values('utm_source').annotate(cnt=Count('id')).order_by('-cnt')
    )
    source_labels = [x['utm_source'] or 'direct' for x in by_source]
    source_data = [x['cnt'] for x in by_source]

    # Chart: shahar bo'yicha daromad
    by_city = list(
        orders.values('city').annotate(rev=Sum('total_price')).order_by('-rev')[:8]
    )
    city_labels = [x['city'] or 'Noma\'lum' for x in by_city]
    city_data = [float(x['rev'] or 0) for x in by_city]

    # Chart: status bo'yicha
    by_status = list(
        orders.values('status').annotate(cnt=Count('id')).order_by('-cnt')
    )
    status_labels = [x['status'] for x in by_status]
    status_data = [x['cnt'] for x in by_status]

    recent_orders = orders[:20]

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'big_orders': big_orders,
        'avg_order': avg_order,
        'source_labels': json.dumps(source_labels),
        'source_data': json.dumps(source_data),
        'city_labels': json.dumps(city_labels),
        'city_data': json.dumps(city_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def topshiriq_add_order(request):
    """Yangi buyurtma qo'shish API — POST /topshiriq/api/orders/"""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    items = data.get('items', [])
    total_price = sum(
        Decimal(str(item.get('initialPrice', 0))) * int(item.get('quantity', 1))
        for item in items
    )
    product_names = ', '.join(
        item.get('productName', '') for item in items if item.get('productName')
    )

    order = Order.objects.create(
        first_name=data.get('firstName', ''),
        last_name=data.get('lastName', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        status=data.get('status', 'new'),
        city=data.get('delivery', {}).get('address', {}).get('city', ''),
        utm_source=data.get('customFields', {}).get('utm_source', ''),
        total_price=total_price,
        items_count=sum(int(i.get('quantity', 1)) for i in items),
        product_names=product_names,
    )

    if order.total_price > 50000:
        send_order_telegram_notification(order)

    return JsonResponse({'id': order.id, 'total_price': float(order.total_price)}, status=201)

