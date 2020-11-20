from django.conf import settings
from homePIX import views
from django.urls import re_path
from django.conf.urls.static import static
from django.contrib.auth import views as dca_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path( r'^$',                                                          views.WelcomeView.as_view(),         name = 'welcome' ),
    re_path( r'^collection/',                                                views.PictureListView.as_view(),     name = 'picture_list' ),
    re_path( r'^item/(?P<pk>\d+)/?.*$',                                      views.PictureDetailView.as_view(),   name = 'picturefile_detail' ),
    re_path( r'^pictures/item/(?P<pk>\d+)/?.*$',                             views.PictureDetailView.as_view(),   name = 'picturefile_detail' ),
    re_path( r'^pictures/(?P<pk>.+\.[jJ][pP][gG])$',                         views.PictureDetailView.as_view(),   name = 'picturefile_detail' ),
    re_path( r'^organise/',                                                  views.PictureOrqaniseView.as_view(), name = 'picturefile_organise' ),
    re_path( r'^folders/(?P<id>\d+)/item/(?P<pk>\d+)/.*$',                   views.PictureDetailView.as_view(),   name = 'picturefile_detail' ),
    re_path( r'^folders/(?P<album_id>\d+)/make_thumbnail/(?P<pic_id>\d+)/$', views.set_folder_thumb,              name = 'make_folder_thumbnail' ),
    re_path( r'^folders/$',                                                  views.FoldersView.as_view(),         name = 'paths' ),
    re_path( r'^folders/(?P<pk>\d+)/.*$',                                    views.FoldersView.as_view(),         name = 'paths' ),
    re_path( r'^organisation/bubble/(?P<pic_ids>\d+(,\d+)*,*)/$',            views.organisation_bubble_ids,       name = 'organisation_bubble_ids' ),
    re_path( r'^organisation/$',                                             views.OrganisationView.as_view(),    name = 'organisation' ),
    re_path( r'^organisation/?album=(?P<album_id>\d+)$',                     views.OrganisationView.as_view(),    name = 'organisation_album' ),
    re_path( r'^organisation/?directory=(?P<dir_id>\d+)$',                   views.OrganisationView.as_view(),    name = 'organisation_album' ),
    re_path( r'^about/',                                                     views.AboutView.as_view(),           name = 'about' ),
    re_path( r'^welcome/',                                                   views.WelcomeView.as_view(),         name = 'welcome' ),
    re_path( r'^webgl/',                                                     views.WebGLView.as_view(),           name = 'webgl' ),
    re_path( r'^tasks/',                                                     views.tasks,                         name = 'tasks' ),
    re_path( r'^albums/$',                                                   views.AlbumView.as_view(),           name = 'album_list' ),
    re_path( r'^albums_new/.*$',                                             views.new_album,                     name = 'new_album' ),
    re_path( r'^albums/make_thumbnail/(?P<album_id>\d+)/(?P<pic_id>\d+)/$',  views.set_album_thumb,               name = 'make_album_thumbnail' ),
    re_path( r'^albums/add/(?P<id>\d+)$',                                    views.add_picture_to_album,          name = 'add_picture_to_album' ),
    re_path( r'^albums/add/(?P<album_id>\d+)/(?P<pic_id>\d+)/$',             views.add_id_to_album,               name = 'add_id_to_album' ),
    re_path( r'^albums/add_multiple/(?P<album_id>\d+)/(?P<pic_id>\d+(,\d+)*,*)/$', views.add_ids_to_album,        name = 'add_ids_to_album' ),
    re_path( r'^albums/del_multiple/(?P<album_id>\d+)/(?P<pic_id>\d+(,\d+)*,*)/$', views.del_ids_from_album,      name = 'del_ids_from_album' ),
    re_path( r'^albums/delete/(?P<album_id>\d+)/(?P<pic_id>\d+)/$',          views.delete_id_from_album,          name = 'delete_id_from_album' ),
    re_path( r'^albums/(?P<album_id>\d+)/item/(?P<pic_id>\d+)/comment/$',    views.add_comment_to_post,           name = 'add_comment_to_post' ),
    re_path( r'^albums/(?P<album_id>\d+)/item/(?P<pic_id>\d+)/publish/$',    views.add_comment_to_post,           name = 'post_publish' ),
    re_path( r'^albums/(?P<album_id>\d+)/item/(?P<pk>\d+)/?.*$',             views.AlbumContentDetailView.as_view(), name = 'albumcontent_entry_detail' ),
    re_path( r'^albums/(?P<pk>\d+)/?.*$',                                    views.AlbumContentView.as_view(),    name = 'albumcontent' ),
    re_path( r'^albums/(?P<pk>.+)?ID=(?P<album_id>\d+)$',                    views.AlbumContentView.as_view(),    name = 'albumcontent' ),
    re_path( r'^albums/(?P<pk>.+)$',                                         views.AlbumContentView.as_view(),    name = 'albumcontent' ),
    re_path( r'^albums/<slug:slug>/$',                                       views.AlbumContentView.as_view(),    name = 'albumcontent' ),
    re_path( r'^folder/new/',                                                views.CreateDirectoryView.as_view(), name = 'directory_new' ),
    re_path( r'^picture/new/',                                               views.CreatePictureView.as_view(),   name = 'picture_new' ),
    re_path( r'^keywords/add/(?P<pk>\d+)$',                                  views.add_keywords,                  name = 'add_keywords' ),
    re_path( r'^keywords/remove/(?P<pk>\d+)$',                               views.remove_keywords,               name = 'remove_keywords' ),
    re_path( r'^keywords/change/(?P<pk>\d+)$',                               views.picture_change,                name = 'picture_change' ),
    re_path( r'^import/csv/',                                                views.CSVImportView.as_view(),       name = 'csv_import' ),
    re_path( r'^import/integrate/',                                          views.CSVImportIntegrateView.as_view(), name = 'csv_integrate' ),
    re_path( r'^post/(?P<pk>\d+)/edit/$',                                    views.PictureUpdateView.as_view(),   name = 'post_edit' ),
    re_path( r'^post/(?P<pk>\d+)/remove/$',                                  views.PictureDeleteView.as_view(),   name = 'post_remove' ),
    re_path( r'^drafts/$',                                                   views.DraftListView.as_view(),       name = 'post_draft_list' ),
    re_path( r'^post/(?P<pk>\d+)/publish/$',                                 views.post_publish,                  name = 'post_publish' ),
    re_path( r'^post/(?P<pk>\d+)/comment/$',                                 views.add_comment_to_post,           name = 'add_comment_to_post' ),
    re_path( r'^comment/(?P<pk>\d+)/approve/$',                              views.comment_approve,               name = 'comment_approve' ),
    re_path( r'^comment/(?P<pk>\d+)/remove/$',                               views.comment_remove,                name = 'comment_remove' ),
    re_path( r'^.*\.[jJ][pP][gG]$',                                          views.compress_view,                 name='jpeg_image'),
    re_path( r'^accounts/login/',                                            dca_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    re_path( r'^accounts/logout/',                                           dca_views.LogoutView.as_view(),      name='logout', kwargs={'next_page': '/'}),
    re_path( r'favicon\.ico',                                                RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico')))
    # re_path( r'^(?P<search>.+)$', views.PictureListView.as_view(), name = 'picture_list' ),
]
urlpatterns += static( 'static/', document_root=settings.STATIC_ROOT )
urlpatterns += static( 'pics/',   document_root=settings.MEDIA_ROOT  )
