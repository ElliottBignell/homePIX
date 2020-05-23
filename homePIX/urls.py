from django.conf.urls import url
from django.conf import settings
from blog import views
from django.urls import path, re_path
from django.conf.urls.static import static
from django.contrib.auth import views as dca_views

urlpatterns = [
    re_path( r'^$', views.PictureListView.as_view(), name = 'picture_list' ),
    re_path( r'^pictures/(?P<pk>.+)$', views.PictureDetailView.as_view(), name = 'picturefile_detail' ),
    re_path( r'^pictures/(?P<pk>.+\.[jJ][pP][gG])$', views.PictureDetailView.as_view(), name = 'picturefile_detail' ),
    re_path( r'^organise/.*$', views.PictureOrqaniseView.as_view(), name = 'picturefile_organiser' ),
    re_path( r'^folders/$', views.FoldersView.as_view(), name = 'paths' ),
    re_path( r'^folders/(?P<pk>.+)$', views.FoldersView.as_view(), name = 'paths' ),
    re_path( r'^about/', views.AboutView.as_view(), name = 'about' ),
    re_path( r'^tasks/', views.tasks, name = 'tasks' ),
    re_path( r'^albums/$', views.AlbumView.as_view(), name = 'album_list' ),
    re_path( r'^albums/add/(?P<id>\d+)$', views.add_picture_to_album, name = 'add_picture_to_album' ),
    re_path( r'^albums/(?P<pk>.+)$', views.AlbumContentView.as_view(), name = 'albumcontent' ),
    re_path( r'^albums/<slug:slug>/$', views.AlbumContentView.as_view(), name = 'albumcontent' ),
    re_path( r'^folder/new/', views.CreateDirectoryView.as_view(), name = 'directory_new' ),
    re_path( r'^picture/new/', views.CreatePictureView.as_view(), name = 'picture_new' ),
    re_path( r'^keywords/add/(?P<pk>\d+)$', views.add_keywords, name = 'add_keywords' ),
    re_path( r'^keywords/remove/(?P<pk>\d+)$', views.remove_keywords, name = 'remove_keywords' ),
    re_path( r'^keywords/change/(?P<pk>\d+)$', views.picture_change, name = 'picture_change' ),
    re_path( r'^post/(?P<pk>\d+)/edit/$', views.PictureUpdateView.as_view(), name = 'post_edit' ),
    re_path( r'^post/(?P<pk>\d+)/remove/$', views.PictureDeleteView.as_view(), name = 'post_remove' ),
    re_path( r'^drafts/$', views.DraftListView.as_view(), name = 'post_draft_list' ),
    re_path( r'^post/(?P<pk>\d+)/publish/$', views.post_publish, name = 'post_publish' ),
    re_path( r'^post/(?P<pk>\d+)/comment/$', views.add_comment_to_post, name = 'add_comment_to_post' ),
    re_path( r'^comment/(?P<pk>\d+)/approve/$', views.comment_approve, name = 'comment_approve' ),
    re_path( r'^comment/(?P<pk>\d+)/remove/$', views.comment_remove, name = 'comment_remove' ),
    re_path( r'^.*\.[jJ][pP][gG]$', views.compress_view, name='jpeg_image'),
    re_path( r'^accounts/login/', dca_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    re_path( r'^accounts/logout/', dca_views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    # re_path( r'^(?P<search>.+)$', views.PictureListView.as_view(), name = 'picture_list' ),
]
urlpatterns += static(  'pics/', document_root=settings.MEDIA_ROOT )