from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView
from django.views.generic.edit import UpdateView

from blog.constants import PAGINATE_BY, DEFAULT_PAGE
from blog.forms import CommentForm, PostForm, ProfileEditForm
from blog.models import Category, Comment, Post

User = get_user_model()


def get_paginated_queryset(queryset, request, per_page=PAGINATE_BY):
    """Helper : retourne une page paginée avec valeur par défaut."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page', DEFAULT_PAGE)
    return paginator.get_page(page_number)


class PublishedPostsMixin:
    """Mixin pour filtrer les posts publiés avec catégorie valide."""

    def get_published_posts(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )


class IndexView(PublishedPostsMixin, ListView):
    """Vue principale : liste des posts publiés (CBV)."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return self.get_published_posts().order_by('-pub_date')


def category_posts(request, category_slug):
    """Vue : posts d'une catégorie spécifique."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.filter(
        is_published=True,
        category=category,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
    page_obj = get_paginated_queryset(posts, request)
    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj}
    )


def post_detail(request, post_id):
    """Vue : détail d'un post avec commentaires."""
    post = get_object_or_404(Post, id=post_id)

    # Guard clause : vérification des permissions d'accès
    if request.user != post.author:
        if (not post.is_published
                or not post.category.is_published
                or post.pub_date > timezone.now()):
            raise Http404()

    comments = post.comments.order_by('created_at')
    return render(
        request,
        'blog/post_detail.html',
        {'post': post, 'comments': comments, 'form': CommentForm()}
    )


@login_required
def create_post(request):
    """Vue : création d'un nouveau post."""
    form = PostForm(request.POST or None, request.FILES or None)
    if not form.is_valid():  # Guard clause
        return render(request, 'blog/create.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.is_published = True
    if not post.pub_date:
        post.pub_date = timezone.now()
    post.save()
    return redirect('blog:profile', username=request.user.username)


@login_required
def edit_post(request, post_id):
    """Vue : édition d'un post existant."""
    post = get_object_or_404(Post, id=post_id)

    # Guard clause : vérification de l'auteur
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    if not form.is_valid():  # Guard clause
        return render(
            request,
            'blog/create.html',
            {'form': form, 'post': post}
        )
    form.save()
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def delete_post(request, post_id):
    """Vue : suppression d'un post."""
    post = get_object_or_404(Post, id=post_id)

    # Guard clause : vérification de l'auteur
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    # Guard clause : traitement uniquement sur POST
    if request.method != 'POST':
        return render(
            request,
            'blog/post_confirm_delete.html',
            {'post': post}
        )
    post.delete()
    return redirect('blog:profile', username=request.user.username)


@login_required
def add_comment(request, post_id):
    """Vue : ajout d'un commentaire."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)  # Correction : or None
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Vue : édition d'un commentaire."""
    comment = get_object_or_404(Comment, id=comment_id)

    # Guard clause : vérification de l'auteur
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if not form.is_valid():  # Guard clause
        return render(
            request,
            'blog/comment.html',
            {'form': form, 'comment': comment}
        )
    form.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def delete_comment(request, post_id, comment_id):
    """Vue : suppression d'un commentaire."""
    comment = get_object_or_404(Comment, id=comment_id)

    # Guard clause : vérification de l'auteur
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    # Guard clause : traitement uniquement sur POST
    if request.method != 'POST':
        return render(
            request,
            'blog/comment_confirm_delete.html',
            {'comment': comment}
        )
    comment.delete()
    return redirect('blog:post_detail', post_id=post_id)


class ProfileView(PublishedPostsMixin, ListView):
    """Vue : profil utilisateur avec ses posts."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATE_BY
    context_object_name = 'page_obj'

    def get_queryset(self):
        username = self.kwargs['username']
        self.profile_user = get_object_or_404(User, username=username)
        if self.request.user == self.profile_user:
            return Post.objects.filter(
                author=self.profile_user
            ).order_by('-pub_date')
        return self.get_published_posts().filter(
            author=self.profile_user
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        context['is_owner'] = self.request.user == self.profile_user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Vue : édition du profil utilisateur."""

    model = User
    form_class = ProfileEditForm
    template_name = 'blog/edit_profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )
