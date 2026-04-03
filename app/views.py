import json
import requests
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import Skills, Project, ContactMessage, SiteSettings

logger = logging.getLogger(__name__)


def send_telegram_message(name, email, message):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        return
    text = f"📩 *Yangi xabar!*\n\n👤 *Ism:* {name}\n📧 *Email:* {email}\n📝 *Xabar:* {message}"
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
        email = request.POST.get("email", "").strip()
        msg = request.POST.get("message", "").strip()

        if name and email and msg:
            ContactMessage.objects.create(name=name, email=email, message=msg)
            send_telegram_message(name, email, msg)
            messages.success(request, "Xabaringiz muvaffaqiyatli yuborildi! Tez orada bog'lanaman.")
            return redirect('home')

    return render(request, 'home5.html', {
        'projects': projects,
        'skills': skills,
        'site': site,
        'typing_phrases_json': json.dumps(typing_phrases),
        'about_tags': about_tags,
    })

