from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.db.models.deletion import ProtectedError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.templatetags.static import static
from django.urls import reverse


class ImageSource(models.Model):
    """An image bundled with the template, optionally replaced by an upload."""
    image_asset = models.CharField('مسیر تصویر قالب', max_length=200, blank=True)
    image_upload = models.ImageField('تصویر بارگذاری‌شده', upload_to='images/', blank=True)
    image_alt = models.CharField('متن جایگزین تصویر', max_length=250, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        if not self.image_asset and not self.image_upload:
            raise ValidationError('یک تصویر قالب یا تصویر بارگذاری‌شده انتخاب کنید.')

    @property
    def image_url(self):
        if self.image_upload:
            return self.image_upload.url
        return static(self.image_asset) if self.image_asset else ''


class Project(ImageSource):
    class Category(models.TextChoices):
        COMMERCIAL = 'commercial', 'تجاری'
        OFFICE = 'office', 'اداری'
        RESIDENTIAL = 'residential', 'مسکونی'
        OTHER = 'other', 'سایر'

    title = models.CharField('عنوان', max_length=160)
    slug = models.SlugField('شناسهٔ نشانی', max_length=160, unique=True, allow_unicode=True)
    category = models.CharField('نوع پروژه', max_length=20, choices=Category.choices)
    location = models.CharField('موقعیت', max_length=100)
    year_text = models.CharField('سال اجرا', max_length=30, blank=True)
    area_text = models.CharField('متراژ', max_length=100, blank=True)
    body_html = models.TextField('متن و HTML شرح پروژه', blank=True)
    order = models.PositiveIntegerField('ترتیب نمایش', default=0)
    featured_order = models.PositiveSmallIntegerField('جایگاه صفحهٔ اصلی', null=True, blank=True)
    is_published = models.BooleanField('منتشر شده', default=True)

    class Meta:
        ordering = ['order', 'pk']
        verbose_name = 'پروژه'
        verbose_name_plural = 'پروژه‌ها'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[self.slug])


class ProjectImage(ImageSource):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='gallery', verbose_name='پروژه')
    position = models.PositiveSmallIntegerField('ترتیب', default=0)

    class Meta:
        ordering = ['position', 'pk']
        verbose_name = 'تصویر گالری'
        verbose_name_plural = 'تصاویر گالری'

    def __str__(self):
        return f'{self.project} — {self.position}'


class ArticleCategory(models.Model):
    name = models.CharField('نام', max_length=100, unique=True)
    slug = models.SlugField('شناسه', max_length=100, unique=True, allow_unicode=True)
    position = models.PositiveSmallIntegerField('ترتیب نمایش', default=100)

    class Meta:
        ordering = ['position', 'pk']
        verbose_name = 'دسته‌بندی مقاله'
        verbose_name_plural = 'دسته‌بندی‌های مقاله'

    def __str__(self):
        return self.name


def get_other_category_id():
    category, _ = ArticleCategory.objects.get_or_create(
        slug='other', defaults={'name': 'سایر', 'position': 999}
    )
    return category.pk


@receiver(pre_delete, sender=ArticleCategory)
def protect_other_category(sender, instance, **kwargs):
    if instance.slug == 'other':
        raise ProtectedError('دسته‌بندی «سایر» قابل حذف نیست.', [instance])


class Article(ImageSource):

    title = models.CharField('عنوان', max_length=200)
    slug = models.SlugField('شناسهٔ نشانی', max_length=180, unique=True, allow_unicode=True)
    category = models.ForeignKey(
        ArticleCategory, on_delete=models.SET(get_other_category_id),
        default=get_other_category_id, related_name='articles', verbose_name='دسته‌بندی',
    )
    jalali_date = models.CharField(
        'تاریخ شمسی برای مرتب‌سازی (YYYY-MM-DD)', max_length=10,
        validators=[RegexValidator(r'^\d{4}-\d{2}-\d{2}$', 'قالب تاریخ باید YYYY-MM-DD باشد.')],
    )
    date_display = models.CharField('تاریخ نمایشی', max_length=50)
    reading_minutes = models.PositiveSmallIntegerField('زمان مطالعه (دقیقه)', default=5)
    body_html = models.TextField('متن و HTML مقاله', blank=True)
    download_file = models.FileField(
        'فایل دانلود مقاله', upload_to='downloads/', blank=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'odt'])],
    )
    is_published = models.BooleanField('منتشر شده', default=True)

    class Meta:
        ordering = ['-jalali_date', '-pk']
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقاله‌ها'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.slug])


class TeamMember(ImageSource):
    name = models.CharField('نام', max_length=100)
    role = models.CharField('سمت', max_length=100)
    position = models.PositiveSmallIntegerField('ترتیب', default=0)
    is_active = models.BooleanField('نمایش در سایت', default=True)

    class Meta:
        ordering = ['position', 'pk']
        verbose_name = 'عضو تیم'
        verbose_name_plural = 'اعضای تیم'

    def __str__(self):
        return self.name


class Consultation(models.Model):
    class Subject(models.TextChoices):
        CONSTRUCTION = 'اجرای ساختمان', 'اجرای ساختمان'
        DESIGN = 'طراحی ساختمان', 'طراحی ساختمان'
        MAINTENANCE = 'نگهداری', 'نگهداری'
        PARTNERSHIP = 'مشارکت در ساخت', 'مشارکت در ساخت'
        OTHER = 'سایر', 'سایر'

    class Status(models.TextChoices):
        NEW = 'new', 'جدید'
        CONTACTED = 'contacted', 'تماس گرفته شد'
        CLOSED = 'closed', 'بسته شد'

    name = models.CharField('نام', max_length=120)
    phone = models.CharField('شماره تماس', max_length=20)
    subject = models.CharField('موضوع', max_length=30, choices=Subject.choices)
    message = models.TextField('توضیحات', blank=True)
    status = models.CharField('وضعیت', max_length=20, choices=Status.choices, default=Status.NEW)
    admin_notes = models.TextField('یادداشت داخلی', blank=True)
    created_at = models.DateTimeField('زمان ثبت', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'درخواست مشاوره'
        verbose_name_plural = 'درخواست‌های مشاوره'

    def __str__(self):
        return f'{self.name} — {self.phone}'


class SiteSettings(models.Model):
    address = models.CharField('نشانی', max_length=200, default='تهران، خیابان ولیعصر')
    phone_display = models.CharField('شمارهٔ نمایشی', max_length=50, default='۰۲۱–۸۸۰۰ ۰۰۰۰')
    phone_href = models.CharField('شمارهٔ تماس بین‌المللی', max_length=30, default='+982188000000')
    email = models.EmailField('ایمیل', default='hello@paksarakaren.example')

    class Meta:
        verbose_name = 'اطلاعات تماس سایت'
        verbose_name_plural = 'اطلاعات تماس سایت'

    def __str__(self):
        return 'اطلاعات تماس سایت'
