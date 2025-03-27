from itertools import chain
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Followers, LikePost, Post, Profile, Comment
from django.db.models import Q
from .forms import CommentForm
from django.utils.html import strip_tags
from django.contrib.auth import views as auth_views
from django.urls import reverse, reverse_lazy

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post


def signup(request):
    try:
        if request.method == 'POST':
            fnm = request.POST.get('fnm')
            emailid = request.POST.get('emailid')
            pwd = request.POST.get('pwd')
            print(fnm, emailid, pwd)
            my_user = User.objects.create_user(fnm, emailid, pwd)
            my_user.save()
            user_model = User.objects.get(username=fnm)
            new_profile = Profile.objects.create(
                user=user_model, id_user=user_model.id)
            new_profile.save()
            if my_user is not None:
                login(request, my_user)
                return redirect('/')
            return redirect('/loginn')
    except:
        invalid = "User already exists"
        return render(request, 'signup.html', {'invalid': invalid})

    return render(request, 'signup.html')


def loginn(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')
        pwd = request.POST.get('pwd')
        print(fnm, pwd)
        userr = authenticate(request, username=fnm, password=pwd)
        if userr is not None:
            login(request, userr)
            return redirect('/')

        invalid = "Invalid Credentials"
        return render(request, 'loginn.html', {'invalid': invalid})

    return render(request, 'loginn.html')


@login_required(login_url='/loginn')
def logoutt(request):
    logout(request)
    return redirect('/loginn')


@login_required(login_url='/loginn')
def home(request):
    following_users = Followers.objects.filter(
        follower=request.user.username).values_list('user', flat=True)
    post = Post.objects.filter(Q(user=request.user.username) | Q(
        user__in=following_users)).order_by('-created_at')
    profile = Profile.objects.get(user=request.user)

    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'main.html', context)


@login_required(login_url='/loginn')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='/loginn')
def likes(request, id):
    if request.method == 'GET':
        username = request.user.username
        post = get_object_or_404(Post, id=id)

        like_filter = LikePost.objects.filter(
            post_id=id, username=username).first()

        if like_filter is None:
            new_like = LikePost.objects.create(post_id=id, username=username)
            post.no_of_likes = post.no_of_likes + 1
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1

        post.save()

        return redirect('/#' + id)


@login_required(login_url='/loginn')
def explore(request):
    post = Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)

    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'explore.html', context)


@login_required(login_url='/loginn')
def profile(request, id_user):
    user_object = User.objects.get(username=id_user)
    profile = Profile.objects.get(user=request.user)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=id_user).order_by('-created_at')
    user_post_length = len(user_posts)

    follower = request.user.username
    user = id_user

    if Followers.objects.filter(follower=follower, user=user).first():
        follow_unfollow = 'Unfollow'
    else:
        follow_unfollow = 'Follow'

    user_followers = len(Followers.objects.filter(user=id_user))
    user_following = len(Followers.objects.filter(follower=id_user))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'profile': profile,
        'follow_unfollow': follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    if request.user.username == id_user:
        if request.method == 'POST':
            if request.FILES.get('image') == None:
                image = user_profile.profileimg
                bio = request.POST['bio']
                location = request.POST['location']

                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
            if request.FILES.get('image') != None:
                image = request.FILES.get('image')
                bio = request.POST['bio']
                location = request.POST['location']

                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()

            return redirect('/profile/' + id_user)
        else:
            return render(request, 'profile.html', context)
    return render(request, 'profile.html', context)


@login_required(login_url='/loginn')
def delete(request, id):
    post = Post.objects.get(id=id)
    post.delete()

    return redirect('/profile/' + request.user.username)


@login_required(login_url='/loginn')
def search_results(request):
    query = request.GET.get('q')

    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)

    context = {
        'query': query,
        'users': users,
        'posts': posts,
    }
    return render(request, 'search_user.html', context)


def home_post(request, id):
    post = Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'main.html', context)


@login_required(login_url='/loginn')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower=follower, user=user).first():
            delete_follower = Followers.objects.get(
                follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            new_follower = Followers.objects.create(
                follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')


@login_required(login_url='/loginn')
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            # Redirect to the profile page
            return redirect('profile', id_user=post.user)
    else:
        form = CommentForm()
    return render(request, 'profile.html', {'form': form, 'post': post})


@login_required(login_url='/loginn')
def search_results(request):
    query = request.GET.get('q')

    # Fetch users matching the query
    users = Profile.objects.filter(user__username__icontains=query)

    # Prepare additional context for each user
    user_details = []
    for user_profile in users:
        # Count posts for this user
        post_count = Post.objects.filter(
            user=user_profile.user.username).count()

        # Count followers for this user
        follower_count = Followers.objects.filter(
            user=user_profile.user.username).count()

        user_details.append({
            'profile': user_profile,
            'post_count': post_count,
            'follower_count': follower_count
        })

    posts = Post.objects.filter(caption__icontains=query)

    context = {
        'query': query,
        'user_details': user_details,
        'posts': posts,
    }
    return render(request, 'search_user.html', context)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "post_confirm_delete.html"  # Create this template
    # Redirect to user profile after deletion
    success_url = reverse_lazy('profile')

    def get_queryset(self):
        """Ensure users can only delete their own posts."""
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


# @login_required
# def profile(request, username):
#     user = get_object_or_404(User, username=username)
#     user_posts = Post.objects.filter(user=user)  # Ensure posts are fetched

#     return render(request, 'profile.html', {'user': user, 'user_posts': user_posts})
