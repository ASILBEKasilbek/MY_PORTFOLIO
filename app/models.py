from django.db import models


class SiteSettings(models.Model):
    # SEO
    site_title = models.CharField(max_length=200, default="Asilbek Sadullayev | Portfolio")
    site_description = models.TextField(default="Asilbek Sadullayev - Backend dasturchi, Django va Python mutaxassisi")
    site_keywords = models.TextField(default="Django, Python, Backend Developer, Portfolio")

    # Rasmlar
    profile_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Profil rasmi")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Favicon (browser tab rasmi)")
    og_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="OG rasmi (Google/ijtimoiy tarmoq preview)")
    preloader_bg = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Kirish sahifasi fon rasmi (preloader)")

    # Shaxsiy
    full_name = models.CharField(max_length=100, default="Asilbek Sadullayev")
    first_name = models.CharField(max_length=50, default="Asilbek")
    job_title = models.CharField(max_length=200, default="Backend Dasturchi & API Mutaxassisi")
    typing_phrases = models.TextField(
        default="Backend Dasturchi\nDjango Mutaxassisi\nPython Ishqibozi\nREST API Yaratuvchi\nTelegram Bot Developer",
        help_text="Har bir qator alohida jumla (typing animatsiyasi uchun)"
    )
    hero_description = models.TextField(
        default="Samarali va xavfsiz backend yechimlar yarataman. Django, Python, REST API va Telegram botlar ishlab chiqishda tajribam bor."
    )
    ready_badge = models.CharField(max_length=100, default="Ishlashga tayyor")

    # Men haqimda
    about_subtitle = models.CharField(max_length=200, default="Backend Dasturchi & API Mutaxassisi")
    about_text_1 = models.TextField(
        default="Men Django va Python texnologiyalarida ixtisoslashgan backend dasturchi. Web dasturlar, REST API va Telegram botlar ishlab chiqishda 2+ yil tajribaga egaman."
    )
    about_text_2 = models.TextField(
        default="Maqsadim — ishonchli, tezkor va optimallashtirilgan backend yechimlarini taqdim etish. Har bir proyektda kod sifati va xavfsizligiga alohida e'tibor beraman."
    )
    about_tags = models.TextField(
        default="Python\nDjango\nREST API\nPostgreSQL\nDocker\nTelegram Bot\nGit\nLinux",
        help_text="Har bir qator alohida tag (texnologiya nomi)"
    )

    # Statistika
    stat_experience = models.CharField(max_length=20, default="2+", verbose_name="Yil tajriba")
    stat_projects = models.CharField(max_length=20, default="15+", verbose_name="Loyihalar soni")
    stat_clients = models.CharField(max_length=20, default="10+", verbose_name="Mijozlar soni")
    stat_quality = models.CharField(max_length=20, default="100%", verbose_name="Sifat ko'rsatkichi")

    # Aloqa
    phone = models.CharField(max_length=30, default="+998 88 864 88 07")
    contact_email = models.EmailField(default="asilbek.sadullayev000@gmail.com", verbose_name="Aloqa email")
    location = models.CharField(max_length=100, default="Toshkent, O'zbekiston")

    # Ijtimoiy tarmoqlar
    github_url = models.URLField(blank=True, default="https://github.com/ASILBEKasilbek")
    linkedin_url = models.URLField(blank=True, default="https://www.linkedin.com/in/asilbek-sadullayev-4066a3333/")
    telegram_url = models.URLField(blank=True, default="https://t.me/dasturch1_asilbek")
    upwork_url = models.URLField(blank=True, default="https://www.upwork.com/freelancers/~01b6f006f65cc81bac")
    instagram_url = models.URLField(blank=True, default="https://instagram.com/asilbek_.dev")

    # Resume/CV
    resume_file = models.FileField(upload_to='site/', blank=True, null=True, verbose_name="CV/Resume fayl")

    class Meta:
        verbose_name = "Sayt sozlamalari"
        verbose_name_plural = "Sayt sozlamalari"

    def __str__(self):
        return "Sayt sozlamalari"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Project(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='project_images/')
    content = models.TextField()
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"


class Skills(models.Model):
    title = models.CharField(max_length=100)
    percent = models.PositiveIntegerField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Ko'nikma"
        verbose_name_plural = "Ko'nikmalar"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('approved', 'Tasdiqlangan'),
        ('assembling', 'Yig\'ilmoqda'),
        ('shipped', 'Yuborilgan'),
        ('delivered', 'Yetkazilgan'),
        ('cancelled', 'Bekor qilingan'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    city = models.CharField(max_length=100, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    items_count = models.PositiveIntegerField(default=1)
    product_names = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.total_price} ₸"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']
        ordering = ['-created_at']