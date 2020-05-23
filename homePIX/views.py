from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from blog.models import ThumbnailBase, Comment, Directory, PictureFile, Keywords, Album, AlbumContent
from django.utils import timezone
from blog.forms import DirectoryForm, PictureForm, CommentForm, AlbumForm, AlbumAddForm, AlbumContentForm

from django.views.generic import (
                            TemplateView,
                            DetailView,
                            CreateView,
                            DeleteView,
                            ListView,
                            UpdateView
                            )

from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from logging import getLogger
from .tasks import bulk_saver
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.db.models import Q
from pprint import pprint
from itertools import chain
from os import path

import json
import datetime
import pytz
import re
# import traceback

logger = getLogger(__name__)
no_file = open( settings.MEDIA_ROOT + '/no_file.jpg', 'rb' ).read() 

@csrf_exempt
def tasks(request):
    if request.method == 'POST':
        return _post_tasks(request)
    else:
        return _get_tasks(request)

def _get_tasks(request):
    message = json.dumps( request.GET )
    pprint( '_get_tasks' )
    pprint( message )
    logger.debug('calling demo_task. message={0}'.format(message))
    bulk_saver( settings.MEDIA_ROOT )
    return redirect( '/folders/' )

def _post_tasks(request):
    message = request.POST['message']
    pprint( '_post_tasks' )
    logger.debug('calling demo_task. message={0}'.format(message))
    demo_task(message)
    return JsonResponse({}, status=302)

def background_view( TemplateView ):
    pprint( 'background_view' )
    bulk_saver( settings.MEDIA_ROOT )
    return HttpResponse( "Hello world" )

class AboutView( TemplateView ):
    template_name = 'about.html'

class PhotoListView( ListView ):

    object_list = None
    paginate_by = 100
    sortkey = "Default"
    direction = "asc"
    startDate = datetime.datetime( 1966, 1, 28, 0, 0, 0, tzinfo=pytz.UTC )
    endDate   = datetime.datetime.now()


    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        paginator = Paginator( self.object_list, self.paginate_by )

        page = self.request.GET.get( 'page' )

        if page == None:
            page = 1

        sort = self.request.GET.get( 'sort' )

        if sort == None:
            sort = "Default"

        self.sortkey = sort

        Items = None

        try:
            Items = paginator.page(page)
        except PageNotAnInteger:
            Items = paginator.page(1)
        except EmptyPage:
            Items = paginator.page(paginator.num_pages)

        context[ 'Items' ] = Items
        context[ 'ForItemCount' ] = paginator.num_pages
        context[ 'page' ] = int( page )
        context[ 'sort' ] = self.sortkey
        context[ 'sort_options' ] = [ "Default", "Title", "Filename", "Date", "Size", "Aspect Ratio" ]
        context[ 'date_range' ] = [ self.startDate, self.endDate ]
        context[ 'order' ] = self.direction

        return context

    def getqueryset( self, objects, filter_key, ret, index ):

        search = None

        try:
            search = self.request.GET.get( 'search', None )
        except:
            search = None

        if not search == None:
            self.object_list =  self.search_queryset( search, ret )
        else:
            self.object_list =  ret( objects, { filter_key: self.getfilter( index ) } )
            print( self.object_list )

        try:
            self.direction = self.request.GET.get( 'direction', None )
        except:
            self.direction = None

        return self.object_list

    def getfilter( self, index ):
        pass

    def search_queryset( self, search, ret ):
        pass

class AlbumView( PhotoListView ):

    model = Album

    def getfilter( self, index ):
        return '.*' 

    def get_queryset( self ):
        ret = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                              select_related( 'thumbnail' ).
                                              extra( select={'lower_name': 'lower(name)'} ).order_by('lower_name')
                                        )
        return super().getqueryset( self.model.objects, 'name__regex', ret, 0 )

    def search_queryset( self, search, ret ):
        return ret( objects, { 'path__icontains': search } )

    def form_valid( self, form ):
        return redirect( 'albumcontent', pk = post.slug  )

class AlbumContentView( PhotoListView ):

    model = AlbumContent
    form_class = AlbumContentForm

    def getfilter( self, index ):

        if 'pk' in self.kwargs:

            album = self.kwargs[ 'pk' ]

            queryset = Album.objects.filter( name = album )

            if not queryset is None:
                return queryset[ 0 ].id

        return -1;

    def get_queryset( self ):
        ret = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                              select_related( 'entry' ).
                                              extra( select={'lower_album_id': 'lower(album_id)'} ).order_by('lower_album_id')
                                        )
        return super().getqueryset( self.model.objects, 'album__exact', ret, 0 )

    def search_queryset( self, search, ret ):
        return ret( objects, { 'path__icontains': search } )
            
class FoldersView( PhotoListView ):

    model = ThumbnailBase
    template_name = 'directory_list.html'

    def getfilter( self, index ):

        if 0 == index:

            if 'pk' in self.kwargs:

                subdir = self.kwargs[ 'pk' ]
                return subdir + '/[^/]*$' 
            else:
                return settings.MEDIA_ROOT + '/[^/]*$' 
        else:
            if 'pk' in self.kwargs:

                subdir = self.kwargs[ 'pk' ]
                return settings.MEDIA_ROOT + '/' + subdir + '$'
            else:
                return settings.MEDIA_ROOT

    def get_queryset( self ):

        ret1 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'thumbnail' ).
                                               extra( select={'lower_path': 'lower(path)'} ).order_by('lower_path')
                                         )
        ret2 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'path' ).
                                               extra( select={'lower_path': 'lower(path)'} ).order_by('lower_path')
                                         )

        collect = PictureFile.objects.none()

        dir_objs = super().getqueryset( Directory.objects,   'path__regex',       ret1, 0 )
        pic_objs = super().getqueryset( PictureFile.objects, 'path__path__regex', ret2, 1 )

        print( "1:")
        if not dir_objs is None:
            if not pic_objs is None:
                collect = chain( dir_objs, pic_objs )
            else:
                collect = dir_objs
        else:
            if not pic_objs is None:
                collect = pic_objs
    
        print( "2:")
        if not collect is None:
            return list( collect )

        print( "3:")
        return self.object_list

    def search_queryset( self, search, ret ):
        return ret( objects, { 'path__icontains': search } )

class KeywordsView( ListView ):

    model = Keywords

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset( self ):
        regex = r'.*'
        return Keywords.objects.filter( path__regex=regex ).order_by( 'keywords' )


class PaperQuestionReorder( ListView ):

    template_name = 'picturefile_organise.html'

    # Ensure we have a CSRF cooke set
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, pk):
        return render(self.request, self.template_name, {'pk': pk, 'questions': Question.objects.filter(paperquestion__paper_id=pk).order_by('paperquestion__order'), 'paper': Paper.objects.get(id=pk)})

    # Process POST AJAX Request
    def post(self, request, pk):
        if request.method == "POST" and request.is_ajax():
            try:
                # Parse the JSON payload
                data = json.loads(request.body)[0]
                # Loop over our list order. The id equals the question id. Update the order and save
                for idx,question in enumerate(data):
                    pq = PaperQuestion.objects.get(paper=pk, question=question['id']) 
                    pq.order = idx + 1
                    pq.save()

            except KeyError:
                HttpResponseServerError("Malformed data!")

            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse({"success": False}, status=400)

class PhotoListViewBase( PhotoListView ):

    model = PictureFile
    context_object_name = 'users'
    queryset = None
    filter_standard = r'.*/(DCIM|[0-9]*ND300|DCIM/[0-9]*ND300)' # TODO: Stop-gap measure

    sorts ={
        "Default"      : "taken_on", 
        "Title"        : "title", 
        "Filename"     : "file", 
        "Date"         : "taken_on", 
        "Size"         : "taken_on", 
        "Aspect Ratio" : "taken_on"
    }

    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_queryset( self ):

        search = None

        try:
            search = self.request.GET.get( 'search', None )
        except:
            search = None

        self.direction = self.request.GET.get( 'direction' )

        if self.direction == None:
            self.direction = "asc"

        self.sortkey = self.request.GET.get( 'sort' )

        if self.sortkey == None:
            self.sortkey = "Default"

        self.startDate = datetime.datetime( 1966, 1, 28, 0, 0, 0, tzinfo=pytz.UTC )
        self.endDate   = datetime.datetime.now()

        try:
            date = self.request.GET.get( 'fromDate', None )

            if date:
                self.startDate = date
        except:
            pass

        try:
            date = self.request.GET.get( 'toDate', None )

            if date:
                self.endDate = date
        except:
            pass

        pprint( self.startDate )
        pprint( self.endDate )

        self.queryset = PictureFile.objects.select_related( 'path' 
                            ).exclude( path__path__iregex=self.filter_standard 
                            ).filter( taken_on__range=( self.startDate, self.endDate ) )

        if not search == None:
           self.queryset = self.search_queryset( search, None )

        for item in self.queryset:
            item.thumb_size = 200

        if self.direction == "desc":
            return self.queryset.order_by( '-' + self.sorts[ self.sortkey ] )
        else:
            return self.queryset.order_by(       self.sorts[ self.sortkey ] )

    def search_queryset( self, search, ret ):

        return self.queryset.select_related( 'keywords' ).filter( 
                        Q( file__icontains=search ) 
                      | Q( title__icontains=search ) 
                      | Q( path__path__icontains=search ) 
                      | Q( keywords__keywords__icontains=search )
                    ).order_by( 'path' )

        # return PictureFile.objects.order_by( 'title' )

class PictureListView( PhotoListViewBase ):

    template_name = 'picturefile_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PictureOrqaniseView( PhotoListViewBase ):

    template_name = 'picturefile_organise.html'
    form_class = DirectoryForm

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        keyword_set = set()

        for obj in Keywords.objects.all():

            words = str( obj ).lower().split( ',' )

            for word in words:

                if word:
                    keyword_set.add( word )

        context[ 'sidebar' ] = sorted( keyword_set )

        return context

def compress_view( request ):

    from blog.exifdata import reduce_file

    filename = request.path
    newfilename = request.path

    m = re.match( r'/pics/(.*/)\.([^/]+)_[0-9]+(\.[jJ][pP][gG])$', filename )

    if m:

        newfilename = m.group( 1 ) + m.group( 2 ) + m.group( 3 )
        reduce_file( filename, newfilename, settings.MEDIA_ROOT, 98 )

    else:

        m = re.search( r'/pics/(.*/)\.([^/]+)_[0-9]+_[0-9]+pc(\.[jJ][pP][gG])$', filename )

        if m:

            newfilename = m.group( 1 ) + m.group( 2 ) + m.group( 3 )
            reduce_file( filename, newfilename, settings.MEDIA_ROOT, 15 )
        else:

            m = re.search( r'/pics/(.*)$', filename )

            if m:
                newfilename = m.group( 1 )
                reduce_file( filename, newfilename, settings.MEDIA_ROOT, 15 )
            else:
                print( "Compression failed for " + filename )

    if not path.exists( settings.MEDIA_ROOT + '/' + newfilename ):
        return HttpResponse( no_file, content_type="image/jpeg" )

    compressed_file = open( settings.MEDIA_ROOT + '/' + newfilename, 'rb' ).read() 

    if compressed_file:
        return HttpResponse( compressed_file, content_type="image/jpeg" )
    else:
        print( "Failed to open " + newfilename )
        return HttpResponseNotFound()

class CompressView( DetailView ):

    model = PictureFile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PictureDetailView( DetailView ):

    model = PictureFile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CreateDirectoryView( LoginRequiredMixin, CreateView ):
    login_url = '/login/' 
    redirect_field_name = 'directory_new.html'

    form_class = DirectoryForm

    model = Directory

class CreatePictureView( LoginRequiredMixin, CreateView ):
    login_url = '/login/' 
    redirect_field_name = 'picture_new.html'

    form_class = PictureForm

    model = PictureFile

class PictureUpdateView( LoginRequiredMixin, UpdateView ):
    login_url = '/login/' 
    redirect_field_name = 'blog/picturefile_detail.html'

    form_class = PictureForm

    model = PictureFile

class PictureDeleteView( LoginRequiredMixin, DeleteView ):
    model = PictureForm
    success_url = reverse_lazy( 'picture_list' )

class DraftListView( LoginRequiredMixin, ListView ):
    login_url = '/login/' 
    redirect_field_name = 'blog/picture_list.html'

    model = PictureForm

    def get_queryset( self ):
        return PictureForm.objects.filter( title__isnull = True ).order_by( '-title' )

 ################################################################################################

@login_required
def post_publish( request, pk ):

    post = get_object_or_404( PictureForm, pk = pk ) 
    post.publish()

    return redirect( 'post_detail', pk = post.pk )

def key_from_request( request, pk ):

    vocab = request.GET.get('vocabulary', None)

    pic = PictureFile.objects.select_related( 'keywords' ).get(id=pk)
    key = pic.keywords

    if key is None:
        key = Keywords()

    return pic, key, vocab

def response_from_keywords( pic, key ):

    pic.keywords = key
    pic.save()

    data = {}
    data[ 'keywords' ] = key.keywords.split( ',' )
    return JsonResponse( data )

@login_required
def add_keywords( request, pk ):

    pic, key, vocab = key_from_request( request, pk )

    new_keywords = ','.join(sorted([ x for x in set((key.keywords + ',' + vocab).split( ',' ) ) if x != '' ] ) ) 

    words_query = Keywords.objects.filter( keywords = new_keywords )
    words = None

    if not words_query is None and words_query.count() > 0:
        words = words_query[ 0 ]

    if words is None:

        words = Keywords()
        words.keywords = new_keywords
        words.save()

    return response_from_keywords( pic, words )

@login_required
def remove_keywords( request, pk ):

    pic, key, vocab = key_from_request( request, pk )

    keys = set( ( key.keywords ).split( ',' ) )
    keys.discard( vocab )

    key.keywords = ','.join( sorted( keys ) )
    key.save()

    return response_from_keywords( pic, key )

@login_required
def picture_change( request, pk ):

    key = request.GET.get( 'key',   None )
    val = request.GET.get( 'value', None )

    pic = PictureFile.objects.select_related( 'keywords' ).get(id=pk)

    data = {}

    if pic:

        print( "Was" + pic.title )
        print( "Changing" + key + ':' + val )

        pic.title = val
        pic.save()

        data[ 'key' ] = pic.title
    else:
        data[ 'change' ] = 'rejected'

    return JsonResponse( data )

@login_required
def add_picture_to_album( request, id ):

   if request.method == 'GET':

        album = request.GET.get( 'add_to_album', None )
        queryset = Album.objects.filter( name = album )

        if not queryset is None:

            newentry = AlbumContent()
            newentry.album = queryset[ 0 ]

            newpic = PictureFile.objects.get( id = id)

            if not newpic is None:

                newentry.entry = newpic
                newentry.save()

                return redirect( 'albumcontent', pk = album)

   return render( request, 'blog/albumcontent_list.html', { 'form': form} )

@login_required
def add_comment_to_post( request, pk):

   post = get_object_or_404( PictureForm, pk = pk ) 

   if request.method == 'POST':

        form = CommentForm( request.POST )

        if form.is_valid():

            album = form.save( commit = False )
            album.post = post
            album.save()

            return redirect( 'albumcontent', pk = 'Fred' )
   else:
       form = CommentForm()

   return render( request, 'blog/comment_form.html', { 'form': form} )

@login_required
def comment_approve( request, pk ):

    comment = get_object_or_404( Comment, pk = pk )
    comment.approve()

    return redirect( 'post_detail', pk = comment.post.pk )

@login_required
def comment_remove( request, pk ):

    comment = get_object_or_404( Comment, pk = pk )
    post_pk = comment.post.pk
    comment.delete()

    return redirect( 'post_detail', pk = comment.post.pk )
