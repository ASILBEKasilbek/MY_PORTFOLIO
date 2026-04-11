import json
import requests
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import Skills, Project, ContactMessage, SiteSettings

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

