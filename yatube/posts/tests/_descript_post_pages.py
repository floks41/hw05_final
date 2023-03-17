"""Создание описаний страниц приложения Posts для целей тестирования."""


from typing import Dict

from django import forms
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Group, Post
from .page_description import PageDescription

User = get_user_model()


def set_post_pages_description_batch(self) -> Dict[str, PageDescription]:
    """Создает описания страниц приложения Posts для целей тестирования."""
    pages = {}
    pages['index'] = PageDescription(
        url='/',
        reverse_name=reverse('posts:index'),
        template='posts/index.html',
        has_paginator=True,
    )

    pages['group_list'] = PageDescription(
        url=f'/group/{self.group.slug}/'
            if hasattr(self, 'group') else None,
        reverse_name=reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug})
        if hasattr(self, 'group') else None,
        reverse_second=reverse(
            'posts:group_posts',
            kwargs={'slug': self.second_group.slug})
        if hasattr(self, 'second_group') else None,
        template='posts/group_list.html',
        has_paginator=True,
        has_additional_objects=True,
        additional_objects={'group': Group, },
    )

    pages['profile'] = PageDescription(
        url=f'/profile/{self.user.username}/'
        if hasattr(self, 'user') else None,
        reverse_name=reverse(
            'posts:profile',
            kwargs={'username': self.user.username})
        if hasattr(self, 'user') else None,
        reverse_second=reverse(
            'posts:profile',
            kwargs={'username': self.second_user.username})
        if hasattr(self, 'second_user') else None,
        template='posts/profile.html',
        has_paginator=True,
        has_additional_objects=True,
        additional_objects={'author': User, 'following': bool},
    )

    pages['post_detail'] = PageDescription(
        url=f'/posts/{self.post.pk}/'
            if hasattr(self, 'post') else '/posts/1/',
        reverse_name=reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk
                    if hasattr(self, 'post') else '1'}),
        succses_redirect_url=reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk
                    if hasattr(self, 'post') else '1'}),
        template='posts/post_detail.html',
        has_additional_objects=True,
        additional_objects={
            'post': Post,
            'short_text_of_post': str,
            'form': CommentForm, },
        has_form=True,
        form_fields={'text': forms.fields.CharField, },
    )
    pages['post_edit'] = PageDescription(
        url=f'/posts/{self.post.pk}/edit/'
            if hasattr(self, 'post') else '/posts/1/edit/',
        reverse_name=reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk
                    if hasattr(self, 'post') else '1'}),
        succses_redirect_url=reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk
                    if hasattr(self, 'post') else '1'}),
        template='posts/create_post.html',
        is_login_required=True,
        guest_redirect_url=f'/posts/{self.post.pk}/'
                           if hasattr(self, 'post') else '/posts/1/',
        has_additional_objects=True,
        additional_objects={'post': Post, 'form': PostForm, 'is_edit': bool},
        has_form=True,
        form_fields={
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}
    )
    pages['post_create'] = PageDescription(
        url='/create/',
        reverse_name=reverse('posts:post_create'),
        template='posts/create_post.html',
        is_login_required=True,
        guest_redirect_url='/auth/login/',
        succses_redirect_url=reverse(
            'posts:profile',
            kwargs={'username': self.user.username}),
        has_additional_objects=True,
        additional_objects={'form': PostForm, 'is_edit': bool},
        form_fields={
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
    )
    pages['add_comment'] = PageDescription(
        url=f'/posts/{self.post.pk}/comment/'
            if hasattr(self, 'post') else '/posts/1/comment/',
        reverse_name=reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk
                    if hasattr(self, 'post') else '1'}),
        succses_redirect_url=reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk
                    if hasattr(self, 'post') else '1'}),
        is_template_test_requred=False,
        is_login_required=True,
        guest_redirect_url='/auth/login/',
    )
    pages['follow_index'] = PageDescription(
        url='/follow/',
        reverse_name=reverse('posts:follow_index'),
        template='posts/follow.html',
        has_paginator=True,
        is_login_required=True,
        guest_redirect_url='/auth/login/',
    )
    pages['profile_follow'] = PageDescription(
        url=f'/profile/{self.user.username}/follow/'
            if hasattr(self, 'user') else None,
        reverse_name=reverse('posts:profile_follow',
                             kwargs={'username': self.user.username})
        if hasattr(self, 'user') else None,
        reverse_second=reverse('posts:profile_follow',
                               kwargs={'username': self.second_user.username})
        if hasattr(self, 'second_user') else None,
        succses_redirect_url=reverse('posts:profile',
                                     kwargs={'username': self.user.username},)
        if hasattr(self, 'user') else None,
        is_template_test_requred=False,
        is_login_required=True,
        guest_redirect_url='/auth/login/',
    )
    pages['profile_unfollow'] = PageDescription(
        url=f'/profile/{self.user.username}/unfollow/'
            if hasattr(self, 'user') else None,
        reverse_name=reverse('posts:profile_unfollow',
                             kwargs={'username': self.user.username})
        if hasattr(self, 'user') else None,
        reverse_second=reverse('posts:profile_unfollow',
                               kwargs={'username': self.second_user.username})
        if hasattr(self, 'second_user') else None,
        succses_redirect_url=reverse('posts:profile',
                                     kwargs={'username': self.user.username},)
        if hasattr(self, 'user') else None,
        is_template_test_requred=False,
        is_login_required=True,
        guest_redirect_url='/auth/login/',
    )

    return pages
