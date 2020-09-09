from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from requests.api import request
from .models import Post, Comments
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy

# Create your views here.

# CBV for the about page
class AboutView(TemplateView):
    template_name = 'about.html'

# CBV for the displaying the blogposts as a list
class PostListView(ListView):
    model = Post

    # the follwing queryset is for displaying all the blogpost based on their published date and filtering out all the unpublished blogposts
    # Almost like writing a SQL query on the models
    def get_queryset(self):
        return Post.objects.filter(published_date__lte = timezone.now()).order_by('-published_date')
        # __lte means less than or equal to
        # -published date is for ordering them by descending based on the published date

# on clicking a blogpost it shows the view for the detailed view of the post
class PostDetailView(DetailView):
    model = Post

# this CBV is for creating a new blogpost
class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

# The following CBV is for the updating the existing blogpost
class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

# CBV for deleting a blogpost
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    # reverse_lazy waits until the deletion of the post is a success
    success_url = reverse_lazy('post_list')

# CBV for displaying the list of unpublished or draft of the blogpost
class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'
    model = Post
    # this following queryset is for filtering out all unpublished blogposts
    def get_queryset(self):
        return Post.objects.filter(published_date__isnull = True).order_by('created_date')

# -----------------------------------------------------------------------------------------------------------------------

# FBV for publishing the post
@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

# FBV for adding a comment to the blogpost
@login_required
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html',context={'form': form})

# FBV for comment approval 
@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comments, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

# FBV for comment removal
@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comments, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)