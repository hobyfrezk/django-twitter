"""twitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from accounts.api import views as account_views
from tweets.api import views as tweets_views
from friendships.api import views as friendships_views
from newsfeeds.api import  views as newsfeeds_views
from comments.api import views as comments_views

router = routers.DefaultRouter()
router.register(r'api/users', account_views.UserViewSet)
router.register(r'api/accounts', account_views.AccountViewSet, basename='accounts')
router.register(r'api/tweets', tweets_views.TweetViewSet, basename='tweets')
router.register(r'api/friendships', friendships_views.FriendshipViewSet, basename='friendships')
router.register(r'api/newsfeeds', newsfeeds_views.NewsFeedViewSet, basename='newsfeeds')
router.register(r'api/comments', comments_views.CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
