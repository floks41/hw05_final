"""Модуль функций отображения Django."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    """Главная страница проекта Yatube."""
    template = 'posts/index.html'

    post_list = Post.objects.order_by('-created')
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_TO_VIEW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Страница записей сообщества."""
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)

    # Извлекаем посты группы, настраиваем постраничный вывод
    post_list = group.posts.order_by('-created')
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_TO_VIEW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Профиль пользователя - все записи автора."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)

    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_TO_VIEW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    following = False
    if request.user.is_authenticated:
        user = get_object_or_404(User, username=request.user.username)
        if Follow.objects.filter(user=user, author=author).exists():
            following = True

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }

    return render(request, template, context)


def post_detail(request, post_id):
    """Просмотр поста c комментариями.

    Если в запросе отправлена форма с комментарием,
    передаем запрос во view-функцию add_comment()
    """
    if request.POST:
        return add_comment(request=request, post_id=post_id)
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)

    # Короткий текст поста для заголовка вкладки браузера по целым словам
    short_text_of_post = ' '.join(
        post.text[:settings.NUMBER_OF_SYMBOLS_TO_VIEW].strip().split(' ')[:-1]
    )
    # Если первое слово поста длинее установленной длины короткого сообщения,
    # оставляем его первые символы в количестве NUMBER_OF_SYMBOLS_TO_VIEW
    if short_text_of_post.strip() == '':
        short_text_of_post = post.text[
            :settings.NUMBER_OF_SYMBOLS_TO_VIEW
        ].strip()

    form = CommentForm()

    context = {
        'short_text_of_post': short_text_of_post,
        'post': post,
        'form': form,
    }
    return render(request, template, context)


def post_edit(request, post_id):
    """Редактировать пост."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id=post.pk)

    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required(redirect_field_name=None)
def post_create(request):
    """Создать пост."""
    template = 'posts/create_post.html'

    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, template, context)


@login_required(redirect_field_name=None)
def add_comment(request, post_id):
    """Создать комментарий."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required(redirect_field_name=None)
def follow_index(request):
    """Подписки на авторов."""
    template = 'posts/follow.html'
    user = get_object_or_404(User, username=request.user.username)

    post_list = Post.objects.filter(
        author__following__user__follower__user=user).distinct()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_TO_VIEW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


@login_required(redirect_field_name=None)
def profile_follow(request, username):
    """Подписаться на автора.

    Проверяем, что подписка не существует и
    пользователь не пытается подписаться сам на себя.
    """
    author = get_object_or_404(User, username=username)

    if request.user.is_authenticated:
        user = get_object_or_404(User, username=request.user.username)
        if not Follow.objects.filter(user=user, author=author).exists():
            if not author == user:
                Follow.objects.create(user=user, author=author)
    return redirect(
        reverse('posts:profile', kwargs={'username': username},))


@login_required(redirect_field_name=None)
def profile_unfollow(request, username):
    """Отменить подписку на автора."""
    author = get_object_or_404(User, username=username)

    if request.user.is_authenticated:
        user = get_object_or_404(User, username=request.user.username)
        if Follow.objects.filter(user=user, author=author).exists():
            Follow.objects.get(user=user, author=author).delete()

    return redirect(
        reverse('posts:profile', kwargs={'username': username},))
