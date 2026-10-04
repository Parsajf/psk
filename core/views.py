from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .forms import ConsultationForm
from .models import Article, ArticleCategory, Project, TeamMember


def home(request):
    featured_projects = Project.objects.filter(
        is_published=True, featured_order__isnull=False
    ).order_by('featured_order', 'pk')[:4]
    return render(request, 'core/index.html', {'featured_projects': featured_projects})


def projects(request):
    return render(request, 'core/projects.html', {
        'projects': Project.objects.filter(is_published=True),
    })


def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related('gallery'), slug=slug, is_published=True
    )
    gallery_images = list(project.gallery.all()) or [project]
    related = Project.objects.filter(is_published=True).exclude(pk=project.pk)[:2]
    return render(request, 'core/project-single.html', {
        'project': project, 'gallery_images': gallery_images,
        'gallery_count': len(gallery_images), 'related_projects': related,
    })


def blog(request):
    return render(request, 'core/blog.html', {
        'articles': Article.objects.filter(is_published=True).select_related('category'),
        'categories': ArticleCategory.objects.all(),
    })


def article_detail(request, slug):
    article = get_object_or_404(Article.objects.select_related('category'), slug=slug, is_published=True)
    related = Article.objects.filter(is_published=True).exclude(pk=article.pk)[:2]
    return render(request, 'core/blog-single.html', {
        'article': article, 'related_articles': related,
    })


def about(request):
    return render(request, 'core/about.html', {
        'team_members': TeamMember.objects.filter(is_active=True),
    })


@require_POST
def consultation(request):
    form = ConsultationForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True, 'message': 'درخواست شما ثبت شد. به‌زودی با شما تماس می‌گیریم.'})
    return JsonResponse({
        'ok': False,
        'message': 'لطفاً اطلاعات فرم را بررسی کنید.',
        'errors': {field: [str(error) for error in errors] for field, errors in form.errors.items()},
    }, status=400)
