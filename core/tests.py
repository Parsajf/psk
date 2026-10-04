from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from .models import Article, ArticleCategory, Consultation, Project, TeamMember


@override_settings(ALLOWED_HOSTS=['testserver'])
class WebsiteTests(TestCase):
    def test_all_pages_and_admin_login_render(self):
        paths = ['/', '/projects/', '/blog/', '/about/', '/admin/login/']
        paths += [project.get_absolute_url() for project in Project.objects.all()]
        paths += [article.get_absolute_url() for article in Article.objects.all()]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_each_card_points_to_its_own_published_detail(self):
        projects_html = self.client.get('/projects/').content.decode()
        articles_html = self.client.get('/blog/').content.decode()
        for project in Project.objects.all():
            self.assertIn(f'href="{project.get_absolute_url()}"', projects_html)
        for article in Article.objects.all():
            self.assertIn(f'href="{article.get_absolute_url()}"', articles_html)
        self.assertNotIn('href="project-single.html"', projects_html)
        self.assertNotIn('href="blog-single.html"', articles_html)

    def test_unpublished_content_is_hidden(self):
        project = Project.objects.first()
        article = Article.objects.first()
        project.is_published = False
        article.is_published = False
        project.save()
        article.save()
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(article.get_absolute_url()).status_code, 404)
        self.assertNotContains(self.client.get('/projects/'), project.get_absolute_url())
        self.assertNotContains(self.client.get('/blog/'), article.get_absolute_url())

    def test_project_gallery_and_team(self):
        project = Project.objects.get(slug='chenar-villa')
        self.assertEqual(project.gallery.count(), 4)
        self.assertContains(self.client.get(project.get_absolute_url()), 'class="project-slide', count=4)
        self.assertEqual(TeamMember.objects.count(), 5)
        self.assertContains(self.client.get('/about/'), 'team-card', count=5)

    def test_download_button_only_appears_with_a_file(self):
        article = Article.objects.first()
        self.assertNotContains(self.client.get(article.get_absolute_url()), 'article-download-action')
        article.download_file = 'downloads/consultation-form.pdf'
        article.save(update_fields=['download_file'])
        self.assertContains(self.client.get(article.get_absolute_url()), article.download_file.url)
        self.assertTrue(article.download_file.storage.exists(article.download_file.name))
        article.download_file = ''
        article.save(update_fields=['download_file'])
        self.assertNotContains(self.client.get(article.get_absolute_url()), 'article-download-action')

    def test_article_category_creation_and_deletion_in_admin(self):
        user = get_user_model().objects.create_superuser('categoryadmin', 'admin@example.com', 'strong-password-1234')
        self.client.force_login(user)
        response = self.client.post(reverse('admin:core_articlecategory_add'), {
            'name': 'دستهٔ تازه', 'slug': 'new-category', 'position': 50, '_save': 'ذخیره',
        })
        self.assertEqual(response.status_code, 302)
        category = ArticleCategory.objects.get(slug='new-category')
        article = Article.objects.first()
        article.category = category
        article.save(update_fields=['category'])
        self.assertContains(self.client.get('/blog/'), 'data-blog-category="new-category"')
        self.assertContains(self.client.get(article.get_absolute_url()), category.name)

        response = self.client.post(
            reverse('admin:core_articlecategory_delete', args=[category.pk]), {'post': 'yes'}
        )
        self.assertEqual(response.status_code, 302)
        article.refresh_from_db()
        self.assertEqual(article.category.slug, 'other')
        self.assertFalse(ArticleCategory.objects.filter(pk=category.pk).exists())
        self.assertNotContains(self.client.get('/blog/'), 'data-blog-category="new-category"')

    def test_other_category_is_default_and_protected(self):
        other = ArticleCategory.objects.get(slug='other')
        article = Article.objects.create(
            title='نمونه', slug='example', jalali_date='1404-01-01',
            date_display='۱ فروردین ۱۴۰۴', image_asset='assets/images/stone-villa.jpg',
        )
        self.assertEqual(article.category, other)
        with self.assertRaises(ProtectedError):
            with transaction.atomic():
                other.delete()
        with self.assertRaises(ProtectedError):
            with transaction.atomic():
                ArticleCategory.objects.filter(pk=other.pk).delete()

    def test_project_categories_and_existing_classification(self):
        self.assertEqual(
            [choice[1] for choice in Project._meta.get_field('category').choices],
            ['تجاری', 'اداری', 'مسکونی', 'سایر'],
        )
        self.assertEqual(Project.objects.get(slug='aftab-office').category, 'office')
        self.assertEqual(Project.objects.get(slug='sepid-garden-house').category, 'other')

    def test_consultation_validation_and_persistence(self):
        response = self.client.post(reverse('consultation'), {
            'name': 'سارا احمدی', 'phone': '۰۹۱۲ ۱۲۳ ۴۵۶۷',
            'subject': 'طراحی ساختمان', 'message': 'یک خانهٔ کوچک',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        inquiry = Consultation.objects.get()
        self.assertEqual(inquiry.phone, '09121234567')
        self.assertEqual(inquiry.message, 'یک خانهٔ کوچک')
        invalid = self.client.post(reverse('consultation'), {
            'name': 'س', 'phone': '123', 'subject': 'نامعتبر', 'message': '',
        })
        self.assertEqual(invalid.status_code, 400)
        self.assertFalse(invalid.json()['ok'])
        self.assertEqual(Consultation.objects.count(), 1)
        self.assertEqual(self.client.get(reverse('consultation')).status_code, 405)

    def test_consultation_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        page = client.get('/')
        self.assertEqual(page.status_code, 200)
        payload = {
            'name': 'سارا احمدی', 'phone': '09121234567',
            'subject': 'طراحی ساختمان', 'message': '',
        }
        self.assertEqual(client.post(reverse('consultation'), payload).status_code, 403)
        token = client.cookies['csrftoken'].value
        self.assertEqual(client.post(reverse('consultation'), payload, HTTP_X_CSRFTOKEN=token).status_code, 200)

    def test_admin_content_and_inquiries_accessible_to_superuser(self):
        user = get_user_model().objects.create_superuser('siteadmin', 'admin@example.com', 'strong-password-1234')
        self.client.force_login(user)
        for model in ('project', 'article', 'articlecategory', 'teammember', 'consultation', 'sitesettings'):
            self.assertEqual(self.client.get(f'/admin/core/{model}/').status_code, 200)
