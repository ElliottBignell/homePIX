from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from homePIX.models import ThumbnailBase, Comment, CSVEntry, Directory, PictureFile, Keywords, Album, AlbumContent
from homePIX.forms import CSVImportForm, CSVImportIntegrateForm, DirectoryForm, PictureForm, CommentForm, AlbumContentForm

from django.views.generic import (
                            TemplateView,
                            DetailView,
                            CreateView,
                            DeleteView,
                            ListView,
                            UpdateView
                            )

from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.utils.formats import localize
from logging import getLogger
from .tasks import bulk_saver
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.db.models import Q
from pprint import pprint
from itertools import chain
from os import path
from dateutil.relativedelta import relativedelta

import json
import csv
import requests
import datetime
import pytz
import re

from homePIX import settings as home_settings

# import traceback

logger = getLogger(__name__)
no_file = open( settings.MEDIA_ROOT + '/../homePIX/static/no_file.jpg', 'rb' ).read()

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
    template_name = 'homePIX/about.html'

class PhotoListView( ListView ):

    object_list = None
    paginate_by = 100
    sortkey = "Default"
    direction = "asc"
    startDate = datetime.datetime( 1966, 1, 28, 0, 0, 0, tzinfo=pytz.UTC )
    endDate   = datetime.datetime.now() - relativedelta( years=1 )

    class Meta:
        abstract = True

    def getDateRange( self ):

        startDate = datetime.datetime( 1966, 1, 28, 0, 0, 0, tzinfo=pytz.UTC )
        endDate   = datetime.datetime.now()

        #try:
        date = self.request.GET.get( 'fromDate', None )

        if date:
            startDate = datetime.datetime.strptime( date, "%Y-%m-%d" )
        #except:
        #    pass

        #try:
        date = self.request.GET.get( 'toDate', None )

        if date:
            endDate = datetime.datetime.strptime( date, "%Y-%m-%d" )
        #except:
        #    pass
        print( startDate )
        print( endDate )

        return startDate, endDate

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

        self.startDate, self.endDate = self.getDateRange()

        print( "get_context_data: " + localize( self.startDate ) + " : " +  localize( self.endDate ) )

        context[ 'Items' ] = Items
        context[ 'ForItemCount' ] = paginator.num_pages
        context[ 'page' ] = int( page )
        context[ 'sort' ] = self.sortkey
        context[ 'sort_options' ] = [ "Default", "Title", "Filename", "Date", "Size", "Aspect Ratio" ]
        context[ 'link_params' ] = self.getlink_params()
        context[ 'date_range' ] = [ self.startDate, self.endDate ]
        context[ 'order' ] = self.direction

        print( self.startDate )

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

        try:
            self.direction = self.request.GET.get( 'direction', None )
        except:
            self.direction = None

        return self.object_list

    def getfilter( self, index ):
        pass

    def getlink_params( self ):
        pass

    def search_queryset( self, search, ret ):
        pass

    def form_valid( self, form ):
        return redirect( 'picture_list/?fromDate=2014-09-01&toDate=2017-06-01', pk = post.slug  )

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

    def getlink_params( self ):
        return 'AlbumID=0&AlbumKey=0&'


class AlbumContentView( PhotoListView ):

    model = AlbumContent
    form_class = AlbumContentForm

    def getfilter( self, index ):
        return -1;

    def get_queryset( self ):

        if 'pk' in self.kwargs:

            album = self.kwargs[ 'pk' ]

            queryset = Album.objects.filter( name = album )

            if not queryset is None and queryset.count() > 0:

                query = "select * from (( homePIX_albumcontent INNER JOIN homePIX_picturefile ON homePIX_picturefile.id=homePIX_albumcontent.entry_id) INNER JOIN homePIX_album ON homePIX_album.id=homePIX_albumcontent.album_id) WHERE album_id=" + str( queryset[ 0 ].id )

                objs = AlbumContent.objects.raw( query )

                return objs

        return AlbumContent.objects.none()

    def search_queryset( self, search, ret ):
        return ret( objects, { 'path__icontains': search } )

    def getlink_params( self ):
        return 'AlbumID=0&AlbumKey=0&'

class FoldersView( PhotoListView ):

    model = ThumbnailBase
    template_name = 'homePIX/directory_list.html'
    subdir = ''

    def getfilter( self, index ):

        if 0 == index:

            if 'pk' in self.kwargs:

                subdir = self.kwargs[ 'pk' ]
                return subdir + '/[^/]*$'
            else:
                return settings.MEDIA_ROOT + '/[^/]*$'
        elif 1 == index:

            if 'pk' in self.kwargs:

                subdir = self.kwargs[ 'pk' ]
                return settings.MEDIA_ROOT + '/' + subdir + '$'
            else:
                return settings.MEDIA_ROOT
        elif 2 == index:
            print('https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir )
            return 'https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir
        else:
            print('https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir + '.+$')
            return 'https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir + '.+$'

    def createPictureFile( self, file, dir ):

        pic = PictureFile()
        pic.file = file
        pic.path = dir
        pic.save()

        return pic

    def getQuery( self, cmd, id, key ):

        return requests.get(
            home_settings.REMOTE_URLs[ 0 ] +
            cmd +
            '?' +
            'APIKey=S5fXMcQLW98ZddrcqVZFMsbJ3GfvfS3m&method=' + cmd + '&NickName=elliottbignell' +
            id + key
            )

    def processQuery( self, cmd, param1, param2, method ):

        response = self.getQuery( cmd, param1, param2 )

        if response.status_code == 200:
            method( response.json() )
        elif response.status_code == 404:
            print('Not Found.')
        else:
            print('Something else returned')

    def get_queryset( self ):

        album_id  = 156925099
        album_key = 'bkX94q'
        query_cmd = home_settings.REMOTE_CMDs[ 0 ]

        if self.request.GET.get( 'AlbumID', None ):

            album_id = self.request.GET[ 'AlbumID' ]

            if self.request.GET.get( 'AlbumKey', None ):

                album_key = self.request.GET[ 'AlbumKey' ]
                query_cmd = 'smugmug.images.get'

        ret1 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'thumbnail' ).
                                               extra( select={'lower_path': 'lower(path)'} ).order_by('lower_path')
                                         )
        ret2 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'path' ).
                                               extra( select={'lower_path': 'lower(path)'} ).order_by('lower_path')
                                         )
        ret3 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'path' )
                                         )

        dir = None

        def saveWithThumbnail( js ):

            try:

                nonlocal dir
                dir.thumbnail = pic
                dir.save()
            except:
                print('Failed to save.')

        def getImages( js ):

            print( js )

            images = js[ 'Album' ][ 'Images' ]
            file   = js[ 'Image' ][ 'X3LargeURL' ]

            image_id  = images[ 0 ][ 'id'  ]
            image_key = images[ 0 ][ 'Key' ]

            pics = PictureFile.objects.filter( file=file ).filter( path=dir )

            pic = None

            if not pics is None and pics.count() > 0:
                pic = pics[ 0 ]
            else:
                pic = self.createPictureFile( file, dir )

            js = response.json()

            if js[ 'Album' ][ 'ImageCount' ] > 0:
                self.processQuery( 'smugmug.images.getInfo', '&ImageID=' + str( image_id ), '&ImageKey=' + image_key, saveWithThumbnail )

        def processAllData( js ):

            nonlocal dir
            nonlocal album_id

            if query_cmd == home_settings.REMOTE_CMDs[ 0 ]:

                albums = js[ 'Albums' ]

                for album in albums:

                    pathname = home_settings.REMOTE_URLs[ 0 ] + album[ 'Title' ]
                    dir_query = Directory.objects.filter( path=pathname )

                    if not dir_query:

                        album_id  = album[ 'id'  ]
                        album_key = album[ 'Key' ]

                        dir = Directory()
                        dir.path = pathname
                        dir.remote_id  = album_id
                        dir.remote_key = album_key
                        dir.save()

                        try:
                            self.processQuery( 'smugmug.images.get', '&AlbumID=' + str( album_id ), '&AlbumKey=' + album_key, getImages )
                        except:
                            pass

            else:

                print( "Doing pictures" )

                try:
                    pictures = js[ 'Album' ][ 'Images' ]
                except:
                    return PictureFile.objects.none()

                objs = Directory.objects.filter( remote_id=album_id )

                if not objs is None and objs.count() > 0:
                    self.subdir = path.relpath( objs[ 0 ].path, home_settings.REMOTE_URLs[ 0 ] )

                dir = Directory.objects.filter( remote_id=album_id )

                if not dir is None and dir.count() > 0:

                    for picture in pictures:

                        picture_id  = picture[ 'id'  ]
                        picture_key = picture[ 'Key' ]

                        response = self.getQuery( 'smugmug.images.getInfo', '&ImageID=' + str( picture_id ), '&ImageKey=' + picture_key )

                        if response.status_code == 200:

                            js = response.json()

                            file = js[ 'Image' ][ 'X3LargeURL' ]

                            pics = None

                            try:
                                pics = PictureFile.objects.filter( file=file ).filter( path_id=dir[ 0 ].id )
                            except:
                                continue

                            if not pics:
                                self.createPictureFile( file, dir[ 0 ] )


        self.processQuery( query_cmd, '&AlbumID=' + str( album_id ), '&AlbumKey=' + album_key, processAllData )

        dir_objs     = super().getqueryset( Directory.objects,   'path__regex',       ret1, 0 )
        rem_objs     = super().getqueryset( Directory.objects,   'path__regex',       ret1, 3 )
        pic_objs     = super().getqueryset( PictureFile.objects, 'path__path__regex', ret2, 1 )
        rem_pic_objs = super().getqueryset( PictureFile.objects, 'path__path__regex', ret3, 2 )

        return list( chain( dir_objs, rem_objs, pic_objs, rem_pic_objs ) )

    def search_queryset( self, search, ret ):
        return ret( objects, { 'path__icontains': search } )

    def getlink_params( self ):
        return 'FolderID=0&FolderKey=0&'

class KeywordsView( ListView ):

    model = Keywords

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset( self ):
        regex = r'.*'
        return Keywords.objects.filter( path__regex=regex ).order_by( 'keywords' )

    def getlink_params( self ):
        return ''

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

        startDate, endDate = self.getDateRange()

        print( "get_queryset: " + localize( startDate ) + " : " +  localize( endDate ) )

        self.queryset = PictureFile.objects.select_related( 'path'
                            ).exclude( path__path__iregex=self.filter_standard
                            ).filter( taken_on__range=[ startDate, endDate ] )

        if not search == None:
           self.queryset = self.search_queryset( search, None )

        for item in self.queryset:
            item.thumb_size = 200

        if self.direction == "desc":
            return self.queryset.order_by( '-' + self.sorts[ self.sortkey ] )
        else:
            return self.queryset.order_by(       self.sorts[ self.sortkey ] )

    def search_queryset( self, search, ret ):

        return self.queryset.order_by( 'path' ).select_related( 'keywords' ).filter(
                        Q( file__icontains=search )
                      | Q( title__icontains=search )
                      | Q( path__path__icontains=search )
                      | Q( keywords__keywords__icontains=search )
                    )

        # return PictureFile.objects.order_by( 'title' )

class PictureListView( PhotoListViewBase ):

    template_name = 'picturefile_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def getlink_params( self ):
        return ''

class PictureOrqaniseView( PhotoListViewBase ):

    template_name = 'picturefile_organise.html'

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

    def getlink_params( self ):
        return ''

class OrganisationView( PhotoListView):

    model = ThumbnailBase
    template_name = 'homePIX/picturefile_organisation.html'
    subdir = ''
    paginate_by = 1000

    def getfilter( self, index ):

        if 0 == index:

            if 'pk' in self.kwargs:

                subdir = self.kwargs[ 'pk' ]
                return subdir + '/[^/]*$'
            else:
                return settings.MEDIA_ROOT + '/[^/]*$'
        elif 1 == index:

            if 'pk' in self.kwargs:

                subdir = self.kwargs[ 'pk' ]
                return settings.MEDIA_ROOT + '/' + subdir + '$'
            else:
                return settings.MEDIA_ROOT
        elif 2 == index:
            print('https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir )
            return 'https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir
        else:
            print('https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir + '.+$')
            return 'https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir + '.+$'

    def get_queryset( self ):

        ret1 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'thumbnail' ).
                                               extra( select={'lower_path': 'lower(path)'} ).order_by('lower_path')
                                         )
        ret2 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'path' ).
                                               extra( select={'lower_path': 'lower(path)'} ).order_by('lower_path')
                                         )
        ret3 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'path' )
                                         )

        dir_objs     = super().getqueryset( Directory.objects,   'path__regex',       ret1, 0 )
        rem_objs     = super().getqueryset( Directory.objects,   'path__regex',       ret1, 3 )
        pic_objs     = super().getqueryset( PictureFile.objects, 'path__path__regex', ret2, 1 )
        rem_pic_objs = super().getqueryset( PictureFile.objects, 'path__path__regex', ret3, 2 )

        return list( chain( dir_objs, rem_objs, pic_objs, rem_pic_objs ) )

    def search_queryset( self, search, ret ):
        return ret( objects, { 'path__icontains': search } )

    def getlink_params( self ):
        return ''

def compress_view( request ):

    from homePIX.exifdata import reduce_file

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
    redirect_field_name = 'homePIX/picturefile_detail.html'

    form_class = PictureForm

    model = PictureFile

class PictureDeleteView( LoginRequiredMixin, DeleteView ):
    model = PictureForm
    success_url = reverse_lazy( 'picture_list' )

class DraftListView( LoginRequiredMixin, ListView ):
    login_url = '/login/'
    redirect_field_name = 'homePIX/picture_list.html'

    model = PictureForm

    def get_queryset( self ):
        return PictureForm.objects.filter( title__isnull = True ).order_by( '-title' )

class CSVImportView( LoginRequiredMixin, CreateView ):

    login_url = '/login/'
    redirect_field_name = 'homePIX/csventry_list.html'
    success_url = reverse_lazy( 'picture_list' )

    form_class = CSVImportForm

    model = CSVEntry

    def run_import( self, filename ):

      with open( filename ) as csvfile:

        reader = csv.reader( csvfile )

        next( reader )

        for row in reader:

            numPeople = 0

            try:
              numPeople = int( '0' + row[ 9 ] )
            except:
              pass

            date = '1966-01-28'

            if len( row[ 8 ] ) > 0:
                date = re.sub( '([0-9]{2})/([0-9]{2})/([0-9]{4})', '\\3-\\2-\\1', row[ 8 ])

            _, created = CSVEntry.objects.get_or_create(
                filename          = row[  0 ],
                imageRef          = row[  1 ],
                caption           = row[  2 ],
                tags              = row[  3 ],
                licenseType       = row[  4 ],
                userName          = row[  5 ],
                superTags         = row[  6 ],
                location          = row[  7 ],
                dateTaken         = date,
                numberOfPeople    = numPeople,
                modelRelease      = row[ 10 ],
                isThereProperty   = row[ 11 ],
                propertyRelease   = row[ 12 ],
                primaryCategory   = row[ 13 ],
                secondaryCategory = row[ 14 ],
                imageType         = row[ 15 ],
                exclusiveToAlamy  = row[ 16 ],
                additionalInfo    = row[ 17 ],
                status            = row[ 18 ]
                )

    def form_valid(self, form):

      if 'import.csv' == self.request.POST[ 'filename' ]:

        self.run_import( 'homePIX/homePIX/templates/homePIX/' + self.request.POST[ 'filename' ] )

        return HttpResponseRedirect( '../../' )
      else:
        return HttpResponseNotFound()


class CSVImportIntegrateView( LoginRequiredMixin, CreateView ):

    login_url = '/login/'
    redirect_field_name = 'homePIX/csventryintegrate.html'
    success_url = reverse_lazy( 'picture_list' )

    form_class = CSVImportIntegrateForm

    model = CSVEntry

    def run_linkage( self, filename ):

        print( 'Linking import to pictures' )

        query = 'CREATE TABLE imports AS select * from homePIX_picturefile JOIN homePIX_csventry ON homePIX_picturefile.file LIKE ( \'%/\' || replace( homePIX_csventry.filename, \'.jpg\', \'-X3.jpg\' ) )'
        PictureFile.objects.raw( query )

        query = 'UPDATE homePIX_picturefile SET taken_on=(select imports.dateTaken from imports INNER JOIN homePIX_csventry ON homePIX_csventry.id = imports."id:1");'
        # query = 'U_IPDATE homePIX_picturefile SET taken_on=(select imports.dateTaken from imports INNER JOIN homePIX_csventry ON homePIX_csventry.id = imports."id:1" WHERE imports.dateTaken BETWEEN "2017-01-01" AND "2017-03-01");'
        PictureFile.objects.raw( query )

    def form_valid(self, form):

      if 'run' == self.request.POST[ 'filename' ]:

        self.run_linkage( "" )

        return HttpResponseRedirect( '../../' )
      else:
        return HttpResponseNotFound()

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

            newpic = PictureFile.objects.get( id = id)

            if not newpic is None:

                selected_album = None

                if queryset.first():
                    selected_album = queryset.first()
                else:
                    selected_album = Album()
                    selected_album.name = album

                selected_album.thumbnail = newpic
                selected_album.save()

                newentry = AlbumContent()
                newentry.album = selected_album
                newentry.entry = newpic
                newentry.save()

                return redirect( 'albumcontent', pk = album)

   return render( request, 'homePIX/albumcontent_list.html', { 'form': form} )

@login_required
def set_album_thumb( request, album_id, pic_id ):

    print( "Album: " + str( album_id ) )
    print( "Picture: " + str( pic_id ) )

    album = get_object_or_404(   Album,       id = int( album_id ) )
    picture = get_object_or_404( PictureFile, id = int( pic_id ) )

    album.thumbnail = picture
    album.save()

    return redirect( '/albums/' )

@login_required
def set_folder_thumb( request, album_id, pic_id ):

    folder = get_object_or_404(  Directory,   remote_id = int( album_id ) )
    picture = get_object_or_404( PictureFile, id = int( pic_id ) )

    folder.thumbnail = picture
    folder.save()

    return redirect( '/folders/' )

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

   return render( request, 'homePIX/comment_form.html', { 'form': form} )

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
