import core.models
import django.db.models.deletion
from django.db import migrations, models


ARTICLE_CATEGORIES = (
    ('residential', 'معماری مسکونی', 1),
    ('interior', 'طراحی داخلی', 2),
    ('landscape', 'محوطه‌سازی', 3),
    ('workplace', 'فضاهای کاری', 4),
    ('public', 'فضاهای عمومی', 5),
    ('other', 'سایر', 999),
)


def move_existing_categories(apps, schema_editor):
    alias = schema_editor.connection.alias
    category_model = apps.get_model('core', 'ArticleCategory')
    article_model = apps.get_model('core', 'Article')
    project_model = apps.get_model('core', 'Project')

    category_ids = {}
    for slug, name, position in ARTICLE_CATEGORIES:
        category, _ = category_model.objects.using(alias).get_or_create(
            slug=slug, defaults={'name': name, 'position': position}
        )
        category_ids[slug] = category.pk

    for slug, category_id in category_ids.items():
        article_model.objects.using(alias).filter(category=slug).update(category_new_id=category_id)
    article_model.objects.using(alias).filter(category_new_id__isnull=True).update(
        category_new_id=category_ids['other']
    )

    project_model.objects.using(alias).filter(
        slug='aftab-office', category='commercial'
    ).update(category='office')
    project_model.objects.using(alias).exclude(
        category__in=['commercial', 'office', 'residential', 'other']
    ).update(category='other')


class Migration(migrations.Migration):
    dependencies = [('core', '0003_alter_article_slug_alter_project_slug')]

    operations = [
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='نام')),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True, verbose_name='شناسه')),
                ('position', models.PositiveSmallIntegerField(default=100, verbose_name='ترتیب نمایش')),
            ],
            options={
                'verbose_name': 'دسته‌بندی مقاله',
                'verbose_name_plural': 'دسته‌بندی‌های مقاله',
                'ordering': ['position', 'pk'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='category_new',
            field=models.ForeignKey(
                null=True, on_delete=models.SET(core.models.get_other_category_id),
                related_name='articles', to='core.articlecategory', verbose_name='دسته‌بندی',
            ),
        ),
        migrations.RunPython(move_existing_categories, migrations.RunPython.noop),
        migrations.RemoveField(model_name='article', name='category'),
        migrations.RenameField(model_name='article', old_name='category_new', new_name='category'),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.ForeignKey(
                default=core.models.get_other_category_id,
                on_delete=models.SET(core.models.get_other_category_id),
                related_name='articles', to='core.articlecategory', verbose_name='دسته‌بندی',
            ),
        ),
        migrations.AlterField(
            model_name='project',
            name='category',
            field=models.CharField(
                choices=[('commercial', 'تجاری'), ('office', 'اداری'), ('residential', 'مسکونی'), ('other', 'سایر')],
                max_length=20, verbose_name='نوع پروژه',
            ),
        ),
    ]
