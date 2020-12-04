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
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from logging import getLogger
from .tasks import bulk_saver
from .forms import CaptchaTestForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.db.models import Q
from pprint import pprint
from itertools import chain
import os
from os import path
from dateutil.relativedelta import relativedelta
from calendar import monthrange

import json
import csv
import requests
from datetime import datetime
import pytz
import re

from homePIX import settings as home_settings

# import traceback

logger = getLogger(__name__)
debug_cwd = os.getcwd();
no_file = open( debug_cwd + '/homePIX/static/no_file.jpg', 'rb' ).read()

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

class WebGLView( TemplateView ):
    template_name = 'homePIX/webgl.html'

class PhotoListView( ListView ):

    object_list = None
    paginate_by = 100
    sortkey = "Default"
    direction = "asc"
    startDate = datetime( 1966, 1, 28, 0, 0, 0, tzinfo=pytz.UTC )
    endDate   = datetime.now() - relativedelta( years=1 )

    q_expr = lambda search: Q( file__icontains=search )               \
                          | Q( title__icontains=search )              \
                          | Q( path__path__icontains=search )         \
                          | Q( keywords__keywords__icontains=search )
    q_filter = lambda objects, search, q_expr: objects.order_by( 'path' ).select_related( 'keywords' ).filter( q_expr( search ) )

    class Meta:
        abstract = True

    def getDateRange( self ):

        startDate = datetime.strptime( "1966-01-28", "%Y-%m-%d" )
        d = datetime.now()
        endDate   = datetime(d.year, d.month, d.day)

        #try:
        date = self.request.GET.get( 'fromDate', None )

        if date:
            startDate = datetime.strptime( date, "%Y-%m-%d" )
        #except:
        #    pass

        #try:
        date = self.request.GET.get( 'toDate', None )

        if date:
            endDate = datetime.strptime( date, "%Y-%m-%d" )
        #except:
        #    pass

        return startDate, endDate

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        paginator = Paginator( self.object_list, self.paginate_by )

        page = self.request.GET.get( 'page' )

        if page == None or page == '':
            page = 1

        sort = self.request.GET.get( 'sort' )

        if sort == None or 0 == len( sort ):
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

        context[ 'Items' ] = Items
        context[ 'ForItemCount' ] = paginator.num_pages
        context[ 'page' ] = page
        context[ 'sort' ] = self.sortkey
        context[ 'sort_options' ] = [ "Default", "Title", "Filename", "Date", "Size", "Aspect Ratio" ]
        context[ 'link_params' ] = self.getlink_params()
        context[ 'date_range' ] = [ self.startDate, self.endDate ]
        context[ 'order' ] = self.direction
        context[ 'albums' ] = Album.objects.all()

        return context

    def getqueryset( self, objects, filter_key, ret, index ):

        search = None

        try:
            search = self.request.GET.get( 'search', None )
        except:
            search = None

        try:
            self.direction = self.request.GET.get( 'direction', None )
        except:
            self.direction = None

        ret_set = None

        if not search == None:
            ret_set = self.search_queryset( objects, search, ret )
        else:
            ret_set = ret( objects, { filter_key: self.getfilter( index ) } )

        if  ret_set:

            startDate, endDate = self.getDateRange()

            try:
                ret_set = ret_set.filter( taken_on__range=[ startDate, endDate ] )
            except:
                pass

        return ret_set

    def getfilter( self, index ):
        pass

    def getlink_params( self ):
        pass

    def search_queryset( self, objects, search, ret ):
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
        PhotoListView.object_list = super().getqueryset( self.model.objects, 'name__regex', ret, 0 )
        return PhotoListView.object_list

    def search_queryset( self, objects, search, ret ):
        return ret( objects, { 'name__icontains': search } )

    def form_valid( self, form ):
        return redirect( 'albumcontent', pk = post.slug  )

    def getlink_params( self ):
        return 'ID=0&Key=0&'

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

    def get_client_ip( self ):

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        return ip

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context[ 'sort_options' ] = self.sorts

        return context

    def get_queryset( self ):

        search = None

        try:
            search = self.request.GET.get( 'search', None )
        except:
            search = None

        self.direction = self.request.GET.get( 'direction' )

        if self.direction == None:
            self.direction = "asc"

        PhotoListView.sortkey = self.request.GET.get( 'sort' )

        if PhotoListView.sortkey == None:
            PhotoListView.sortkey = "Default"

        startDate, endDate = self.getDateRange()

        self.queryset = PictureFile.objects.select_related( 'path'
                            ).exclude( path__path__iregex=self.filter_standard
                            ).filter( taken_on__range=[ startDate, endDate ] )

        if search:
            self.queryset = self.search_queryset( self.queryset, search, None )

        key = 'taken_on'

        try:
            key = self.sorts[ PhotoListView.sortkey ]
        except:
            pass

        if self.direction == "desc":
            key = '-' + key

        if self.queryset:

            for item in self.queryset:

                item.thumb_size = 200

            return self.queryset.order_by( key )

        return PictureFile.objects.none()

    def search_queryset( self, objects, search, ret ):
        return PhotoListView.q_filter( objects, search, PhotoListView.q_expr )
        # return objects.order_by( 'path' ).select_related( 'keywords' ).filter( PhotoListView.q_expr( search ) )

class PictureListView( PhotoListViewBase ):

    template_name = 'picturefile_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def getlink_params( self ):

        ret = "";
        keys = [ 'search', 'ID', 'Key', 'fromDate', 'toDate' ]

        for key in keys:

            if self.request.GET.get( key, None ):
                ret += key + '=' + self.request.GET.get( key, None ) +'&'

        return ret

class PictureDetailView( PhotoListViewBase ):

    template_name = 'homePIX/picturefile_detail.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        id = 0

        if 'pk' in self.kwargs:

            id = int( self.kwargs[ 'pk' ] )

            previous = self.object_list[ len( self.object_list ) - 1 ]

            for index, file in enumerate( self.object_list ):

                if file.id == id:

                    context[ 'Item'     ] = file
                    context[ 'next'     ] = self.object_list[ ( index + 1 ) % len( self.object_list ) ]
                    context[ 'previous' ] = previous

                    break

                previous = file

        return context

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
            return 'https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir
        else:
            return 'https://api.smugmug.com/services/api/json/1.3.0/' + self.subdir + '.+$'

    @csrf_protect
    def pretty_request( self, request ):

        headers = ''
        for header, value in request.META.items():
            if not header.startswith('HTTP'):
                continue
            header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
            headers += '{}: {}\n'.format(header, value)

        return (
            '{method} HTTP/1.1\n'
            'Content-Length: {content_length}\n'
            'Content-Type: {content_type}\n'
            '{headers}\n\n'
            '{body}'
        ).format(
            method=request.method,
            content_length=request.META['CONTENT_LENGTH'],
            content_type=request.META['CONTENT_TYPE'],
            headers=headers,
            body=request.body,
        )

    def get_queryset( self ):

        if self.request.GET.get( 'album', None ):

            album = self.request.GET.get( 'album' )

            PhotoListView.object_list = AlbumContent.objects.none()

            queryset = Album.objects.filter( id = album )

            if not queryset is None and queryset.count() > 0:

                query = "select * from (( homePIX_albumcontent INNER JOIN homePIX_picturefile ON homePIX_picturefile.id=homePIX_albumcontent.entry_id) INNER JOIN homePIX_album ON homePIX_album.id=homePIX_albumcontent.album_id) WHERE album_id=" + album + ";"

                PhotoListView.object_list = AlbumContent.objects.raw( query )

            return PhotoListView.object_list

        elif self.request.GET.get( 'directory', None ):

            directory = self.request.GET.get( 'directory' )

            PhotoListView.object_list = PictureFile.objects.none()

            queryset = Directory.objects.filter( id = directory )

            pics = None

            if not queryset is None and queryset.count() > 0:

                try:

                    pics = PictureFile.objects.filter( path_id=queryset[ 0 ].id )
                except:
                    pass

            return pics

        else:

            ret2 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                                   select_related( 'path' ).
                                                   extra( select={'lower_path': 'lower(path)'} ).
                                                   order_by('sortkey')
                                             )
            ret3 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                                   select_related( 'path' ).
                                                   order_by('sortkey')
                                             )

            # self.directory_list = super().getqueryset( Directory.objects,   'path__regex',       ret1, 2 )
            # rem_objs          = super().getqueryset( Directory.objects,   'path__regex',       ret1, 3 )
            pic_objs            = super().getqueryset( PictureFile.objects, 'path__path__regex', ret2, 1 )
            rem_pic_objs        = super().getqueryset( PictureFile.objects, 'path__path__regex', ret3, 2 )

            self.object_list = list( chain( pic_objs, rem_pic_objs ) )

            return self.object_list

    def search_queryset( self, objects, search, ret ):
        return ret( objects, { 'path__icontains': search } )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        ret1 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'thumbnail' ).
                                               extra( select={'lower_path': 'lower(path)'} ).order_by('lower_path')
                                         )
        context[ 'directory_list' ] = super().getqueryset( Directory.objects,   'path__regex',       ret1, 2 )
        context[     'album_list' ] = Album.objects.all()
        context[       'universe' ] = PictureFile.objects.all()

        return context

    def getlink_params( self ):
        return ''

class AlbumContentView( PhotoListView ):

    model = AlbumContent
    form_class = AlbumContentForm

    def getfilter( self, index ):
        return -1;

    def get_queryset( self ):

        PhotoListView.object_list = AlbumContent.objects.none()

        if 'pk' in self.kwargs:

            album = self.kwargs[ 'pk' ]

            queryset = Album.objects.filter( id = album )

            if not queryset is None and queryset.count() > 0:

                query = "select * from (( homePIX_albumcontent INNER JOIN homePIX_picturefile ON homePIX_picturefile.id=homePIX_albumcontent.entry_id) INNER JOIN homePIX_album ON homePIX_album.id=homePIX_albumcontent.album_id) WHERE album_id=" + str( queryset[ 0 ].id )

                PhotoListView.object_list = AlbumContent.objects.raw( query )

        return PhotoListView.object_list

    def search_queryset( self, objects, search, ret ):
        return ret( objects, { 'path__icontains': search } )

    def getlink_params( self ):
        return 'ID=0&Key=0&'


class WelcomeView( PhotoListView ):

    model = AlbumContent

    template_name = 'homePIX/welcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def getfilter( self, index ):
        return -1;

    def get_queryset( self ):

        PhotoListView.object_list = AlbumContent.objects.none()

        album = '4'

        queryset = Album.objects.filter( id=album )

        if not queryset is None and queryset.count() > 0:

            query = "select * from (( homePIX_albumcontent INNER JOIN homePIX_picturefile ON homePIX_picturefile.id=homePIX_albumcontent.entry_id) INNER JOIN homePIX_album ON homePIX_album.id=homePIX_albumcontent.album_id) WHERE album_id=" + str( album )

            PhotoListView.object_list = AlbumContent.objects.raw( query )

            previous = PhotoListView.object_list[ len( PhotoListView.object_list ) - 1 ]

            index = 0

            for file in PhotoListView.object_list:

                if file.entry_id == id:

                    next_id = ( index + 1 ) % len( PhotoListView.object_list )

                    self.nav[ 'Item'     ] = PictureFile.objects.get( id=file.entry_id )
                    self.nav[ 'next'     ] = PictureFile.objects.get( id=PhotoListView.object_list[ next_id ].entry_id )
                    self.nav[ 'previous' ] = PictureFile.objects.get( id=previous.entry_id )

                    break

                previous = file
                index += 1

        return PhotoListView.object_list

    def render_to_response(self, context):

        fromDate = self.request.GET.get( 'fromDate', None )
        toDate   = self.request.GET.get( 'toDate',   None )

        if fromDate:
            return redirect('collection/?fromDate=' + fromDate + '&toDate=' + toDate )

        return super().render_to_response(context)

# Sourced from https://stackoverflow.com/questions/3229419/how-to-pretty-print-nested-dictionaries
# Author: y.petremann
def pretty(value, htchar='\t', lfchar='\n', indent=0):

    nlch = lfchar + htchar * (indent + 1)

    if type(value) is dict:
        items = [
            nlch + repr(key) + ': ' + pretty(value[key], htchar, lfchar, indent + 1)
            for key in value
        ]
        return '{%s}' % (','.join(items) + lfchar + htchar * indent)
    elif type(value) is list:
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return '[%s]' % (','.join(items) + lfchar + htchar * indent)
    elif type(value) is tuple:
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return '(%s)' % (','.join(items) + lfchar + htchar * indent)
    else:
        return repr(value)

# Sourced from https://stackoverflow.com/questions/3229419/how-to-pretty-print-nested-dictionaries
# Author: y.petremann
class Formatter(object):
    def __init__(self):
        self.types = {}
        self.htchar = '\t'
        self.lfchar = '\n'
        self.indent = 0
        self.set_formater(object, self.__class__.format_object)
        self.set_formater(dict, self.__class__.format_dict)
        self.set_formater(list, self.__class__.format_list)
        self.set_formater(tuple, self.__class__.format_tuple)

    def set_formater(self, obj, callback):
        self.types[obj] = callback

    def __call__(self, value, **args):
        for key in args:
            setattr(self, key, args[key])
        formater = self.types[type(value) if type(value) in self.types else object]
        return formater(self, value, self.indent)

    def format_object(self, value, indent):
        return repr(value)

    def format_dict(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + repr(key) + ': ' +
            (self.types[type(value[key]) if type(value[key]) in self.types else object])(self, value[key], indent + 1)
            for key in value
        ]
        return '{%s}' % (','.join(items) + self.lfchar + self.htchar * indent)

    def format_list(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + (self.types[type(item) if type(item) in self.types else object])(self, item, indent + 1)
            for item in value
        ]
        return '[%s]' % (','.join(items) + self.lfchar + self.htchar * indent)

    def format_tuple(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + (self.types[type(item) if type(item) in self.types else object])(self, item, indent + 1)
            for item in value
        ]
        return '(%s)' % (','.join(items) + self.lfchar + self.htchar * indent)

class CalendarView( PhotoListView ):

    model = PictureFile

    template_name = 'homePIX/calendar.html'
    years = {}

    def build_calendar( self ):

        PhotoListView.sortkey = "Date"

        PhotoListView.object_list = PictureFile.objects.none()

        queryset = PictureFile.objects

        if not queryset is None and queryset.count() > 0:

            # out_file = open('calendar'+'.txt', 'w')

            query = 'select id, file, substr( taken_on, 0, 11), count( substr( taken_on, 0, 11 ) ) as count from homePIX_picturefile where not taken_on like "1966-01-28%" group by substr( taken_on, 0, 11 ) order by substr( taken_on, 0, 11);'

            obj_list = PictureFile.objects.raw( query )
            self.years = {}
            unique_years = []

            for val in obj_list:
                unique_years.append( val.taken_on.year )

            unique_years = sorted( set( unique_years ) )

            if len( unique_years ) > 0:

                first_year = unique_years[ 0 ]
                quarter_len = 4
                quarter_cnt = int( 12 / quarter_len )
                year_group_len = 4
                year_index = 0

                self.years[ unique_years[ 0 ] ] = {}

                for year in unique_years:

                    group_year = year - ( year - first_year ) % year_group_len

                    if year == 2012:
                        pprint( { "year": year,  "group_year": group_year } )

                    if year_index % year_group_len == 0:
                        self.years[ group_year ] = {}

                    year_index += 1

                    self.years[ group_year ][ year ] = [None] * quarter_cnt

                    if year == 2012:
                        pprint( { "Quarters: " : self.years[ group_year ][ year ] } )

                    for quarter in range( 0, quarter_cnt ):

                        self.years[ group_year ][ year ][ quarter ] = {}

                        for month_index in range( 0, quarter_len):

                            index = quarter * quarter_len + month_index + 1

                            first_day, days = monthrange( year, index )

                            self.years[ group_year ][ year ][ quarter ][ month_index ] = [ None ] * 6

                            for day in range( 42 ):

                                week = int( ( day - ( day % 7 ) ) / 7 )

                                if not self.years[ group_year ][ year ][ quarter ][ month_index ][ week ]:
                                    self.years[ group_year ][ year ][ quarter ][ month_index ][ week ] = [ None ] * 7

                                self.years[
                                                group_year ][
                                                year ][
                                                quarter ][
                                                month_index ][
                                                week ][
                                                int( day % 7 ) ] = [
                                    -1,
                                    -1,
                                    "Default",
                                    datetime( year, index, day + 1 ) if day < days else None,
                                    int( quarter * quarter_len + month_index ) + 1,
                                    ""
                                    ]

                for val in obj_list:

                    taken_on_year = val.taken_on.year
                    group_year = taken_on_year - ( taken_on_year - first_year ) % year_group_len

                    month_abs  = val.taken_on.month - 1

                    quarter = int( ( month_abs - (month_abs % quarter_len) ) / quarter_len )
                    month   = month_abs % quarter_len
                    day     = val.taken_on.day - 1

                    week = int( ( day - ( day % 7 ) ) / 7 )

                    entry = [
                        val.id,
                        val.count,
                        val.title,
                        val.taken_on,
                        int( quarter * quarter_len + month ) + 1,
                        val.file.replace( 'X3', 'S' )
                    ]

                    # Note: The final index (day) is 0 here to paper over a problem with
                    # doing logic in Django templates. We need the first picture from
                    # ANY day to embellish the calendar month
                    self.years[ group_year ][ taken_on_year ][ quarter ][ month ][ 0 ][ 0 ] = entry
                    self.years[ group_year ][ taken_on_year ][ quarter ][ month ][ week ][ int( day % 7 ) ] = entry

        PhotoListView.object_list = obj_list

    def get_context_data(self, **kwargs):

        context = {}

        PhotoListView.sortkey = "Date"

        self.build_calendar()

        context[ 'sort'     ] = self.sortkey
        context[ 'calendar' ] = self.years
        context[ 'quarters' ] = range(4)
        context[ 'months'   ] = range(3)
        context[ 'days'     ] = [
            'Mon',
            'Tue',
            'Wed',
            'Thu',
            'Fri',
            'Sat',
            'Sun',
            ]

        return context

    def get_queryset( self ):
        self.build_calendar()
        return PhotoListView.object_list

    def form_valid( self, form ):
        return redirect('/?fromDate=19660128&toDate=' + datetime.datetime.now().strftime ("%Y%m%d") )

class AlbumContentDetailView( PhotoListViewBase ):

    model = AlbumContent
    form_class = AlbumContentForm
    nav = {}

    template_name = 'homePIX/picturefile_detail.html'

    def get_context_data(self, **kwargs):

        if self.nav:
            return { **super().get_context_data(**kwargs), **self.nav  }
        else:
            return super().get_context_data(**kwargs)

    def getfilter( self, index ):
        return -1;

    def get_queryset( self ):

        PhotoListView.object_list = AlbumContent.objects.none()

        if 'album_id' in self.kwargs:

            album = self.kwargs[ 'album_id' ]

            if 'pk' in self.kwargs:

                id = int( self.kwargs[ 'pk' ] )

                queryset = Album.objects.filter( id=album )

                if not queryset is None and queryset.count() > 0:

                    query = "select * from (( homePIX_albumcontent INNER JOIN homePIX_picturefile ON homePIX_picturefile.id=homePIX_albumcontent.entry_id) INNER JOIN homePIX_album ON homePIX_album.id=homePIX_albumcontent.album_id) WHERE album_id=" + str( album )

                    PhotoListView.object_list = AlbumContent.objects.raw( query )

                    previous = PhotoListView.object_list[ len( PhotoListView.object_list ) - 1 ]

                    visitor_ip = super().get_client_ip()

                    index = 0

                    for file in PhotoListView.object_list:

                        if file.entry_id == id:

                            if visitor_ip != '85.2.137.247':

                                current_pic = PictureFile.objects.get( id=file.entry_id )

                                current_pic.hits += 1
                                current_pic.save()

                            next_id = ( index + 1 ) % len( PhotoListView.object_list )

                            self.nav[ 'Item'     ] = PictureFile.objects.get( id=file.entry_id )
                            self.nav[ 'next'     ] = PictureFile.objects.get( id=PhotoListView.object_list[ next_id ].entry_id )
                            self.nav[ 'previous' ] = PictureFile.objects.get( id=previous.entry_id )

                            break

                        previous = file
                        index += 1

        return PhotoListView.object_list

    def search_queryset( self, objects, search, ret ):
        return ret( objects, { 'path__icontains': search } )

    def getlink_params( self ):
        return 'ID=0&Key=0&'

class FoldersView( PhotoListViewBase ):

    model = ThumbnailBase
    template_name = 'homePIX/directory_list.html'
    subdir = ''
    album_id  = 0
    album_key = 'bkX94q'
    dir_objs     = None
    pic_objs     = None
    rem_pic_objs = None

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

    def processQuery1( self, cmd, param1, param2, method, pic ):

        response = self.getQuery( cmd, param1, param2 )

        if response.status_code == 200:
            method( response.json(), pic )
        elif response.status_code == 404:
            print('Not Found.')
        else:
            print('Something else returned')

    def get_queryset( self ):

        query_cmd = home_settings.REMOTE_CMDs[ 0 ]

        if 'pk' in self.kwargs:
            self.album_id = int( self.kwargs[ 'pk' ] )
        elif self.request.GET.get( 'ID', None ):
            self.album_id = self.request.GET[ 'ID' ]

        if self.album_id > 0:

            dir_query = Directory.objects.filter( id=self.album_id )

            if dir_query:

               self.album_id  = dir_query[ 0 ].remote_id
               self.album_key = dir_query[ 0 ].remote_key

        query_cmd = 'smugmug.images.get'

        ret1 = lambda queryset, filter_dict: ( queryset.filter( **filter_dict ).
                                               select_related( 'thumbnail' ).
                                               extra( select={'lower_path': 'lower(path)'} ).order_by('lower_path')
                                         )

        dir = None

        def saveWithThumbnail( js, pic ):

            try:

                nonlocal dir
                dir.thumbnail = pic
                dir.save()
            except:
                print('Failed to save.')

        def getImages( js ):

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

            if js[ 'Album' ][ 'ImageCount' ] > 0:
                self.processQuery1( 'smugmug.images.getInfo', '&ImageID=' + str( image_id ), '&ImageKey=' + image_key, saveWithThumbnail, pic )

        def processAllData( js ):

            nonlocal dir
            nonlocal query_cmd

            if query_cmd == home_settings.REMOTE_CMDs[ 0 ]:

                albums = js[ 'Albums' ]

                for album in albums:

                    pathname = home_settings.REMOTE_URLs[ 0 ] + album[ 'Title' ]
                    dir_query = Directory.objects.filter( path=pathname )

                    if not dir_query:

                        self.album_id  = album[ 'id'  ]
                        self.album_key = album[ 'Key' ]

                        dir = Directory()
                        dir.path = pathname
                        dir.remote_id  = self.album_id
                        dir.remote_key = self.album_key
                        dir.save()

                        try:
                            self.processQuery( 'smugmug.images.get', '&AlbumID=' + str( self.album_id ), '&AlbumKey=' + self.album_key, getImages )
                        except:
                            pass

            else:

                try:
                    pictures = js[ 'Album' ][ 'Images' ]
                except:
                    return PictureFile.objects.none()

                objs = Directory.objects.filter( remote_id=self.album_id )

                if not objs is None and objs.count() > 0:
                    self.subdir = path.relpath( objs[ 0 ].path, home_settings.REMOTE_URLs[ 0 ] )

                dir = Directory.objects.filter( remote_id=self.album_id )

                if False and not dir is None and dir.count() > 0:

                    for picture in pictures:

                        picture_id  = picture[ 'id'  ]
                        picture_key = picture[ 'Key' ]

                        response = self.getQuery( 'smugmug.images.getInfo', '&ImageID=' + str( picture_id ), '&ImageKey=' + picture_key )

                        if response.status_code == 200:

                            js = response.json()

                            file = js[ 'Image' ][ 'X3LargeURL' ]

                            pics = None

                            try:

                                pics = PictureFile.objects.filter( file=file
                                                         ).filter( path_id=dir[ 0 ].id
                                                         )
                            except:
                                continue

                            if not pics:
                                self.createPictureFile( file, dir[ 0 ] )

#        if self.request.user.is_anonymous():
        self.processQuery( query_cmd, '&AlbumID=' + str( self.album_id ), '&AlbumKey=' + self.album_key, processAllData )

        try:
            self.direction = self.request.GET.get( 'direction', None )
        except:
            self.direction = None

        key = 'path'

        try:

            key = self.sorts[ PhotoListView.sortkey ]

            if key == 'taken_on':
                key = 'path'

        except:
            pass

        if self.direction == "desc":
            key = '-' + key

        cache = PhotoListView.q_expr
        PhotoListView.q_expr = lambda search: Q( path__icontains=search )

        cache_filter = PhotoListView.q_filter
        PhotoListView.q_filter = lambda objects, search, q_expr: objects.order_by( 'path' ).filter( q_expr( search ) )

        self.dir_objs = PhotoListView.getqueryset( self, Directory.objects.order_by( key ), 'path__regex',  ret1, 2 )

        PhotoListView.q_expr = cache
        PhotoListView.q_filter = cache_filter

        if self.album_id:

            objs = Directory.objects.filter( remote_id=self.album_id )

            if not objs is None and objs.count() > 0:
                self.object_list = super().get_queryset().filter( path_id=objs[ 0 ].id )
        else:
            self.object_list = super().get_queryset()

        if self.dir_objs:
            self.object_list = list( chain( self.dir_objs, self.object_list ) )

        return self.object_list

    def search_directories( self, objects, search, ret ):

        return objects.order_by( 'path' ).select_related( 'keywords' ).filter(
                        Q( file__icontains=search )
                      | Q( title__icontains=search )
                      | Q( path__path__icontains=search )
                      | Q( keywords__keywords__icontains=search )
                    )

    def getlink_params( self ):

        ret = "";
        keys = [ 'search', 'ID', 'Key', 'fromDate', 'toDate' ]

        for key in keys:
            if self.request.GET.get( key, None ):
                ret += key + ' =' + self.request.GET.get( key, None ) +'&'

        return ret

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
        return render(self.request, self.template_name, {'pk': pk, 'quequery_fuistions': Question.objects.filter(paperquestion__paper_id=pk).order_by('paperquestion__order'), 'paper': Paper.objects.get(id=pk)})

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

class LoginView( TemplateView ):

    template_name = 'homePIX/login.html'

    def post(self, request, **kwargs):

        logout(request)

        username = password = ''

        if request.POST:

            form = CaptchaTestForm(request.POST)

            # Validate the form: the captcha field will automatically
            # check the input
            # if form.is_valid():

            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:

                    login(request, user)
                    return HttpResponseRedirect('/')

        return HttpResponseRedirect('homePIX/login.html')

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

   return render( request, 'homePIX/albumcontent_list.html', { 'form': form } )

@login_required
def add_id_to_album( request, album_id, pic_id ):

    album = get_object_or_404(   Album,       id = int( album_id ) )
    picture = get_object_or_404( PictureFile, id = int( pic_id ) )

    entries = AlbumContent.objects.filter(
                        Q( album_id=album_id )
                      & Q( entry_id=pic_id )
                      )

    if entries is None or entries.count() <= 0:

        entry = AlbumContent()
        entry.album = album
        entry.entry = picture
        entry.save()

        return redirect( '/albums/?ID=' + str( album_id ) )

    return redirect( '/albums/' )

@login_required
def add_ids_to_album( request, album_id, pic_id ):

    album = get_object_or_404(   Album,       id = int( album_id ) )

    ids = pic_id.split( ',' )

    for id in ids:

        if len( id ) > 0:

            picture = get_object_or_404( PictureFile, id = int( id ) )

            entries = AlbumContent.objects.filter(
                                Q( album_id=album.id )
                              & Q( entry_id=id )
                              )

            if entries is None or entries.count() <= 0:

                entry = AlbumContent()
                entry.album = album
                entry.entry = picture
                entry.save()

    return HttpResponse(json.dumps(
        {
            'name': album.name,
            'id':   album.id,
            'count':album.modcount
        }
        ),
        content_type="application/json"
        )

@login_required
def del_ids_from_album( request, album_id, pic_id ):

    album = get_object_or_404( Album, id = int( album_id ) )

    ids = pic_id.split( ',' )

    for id in ids:

        if len( id ) > 0:

            AlbumContent.objects.filter(
                    Q( album_id=album_id )
                  & Q( entry_id=id )
              ).delete()

    return HttpResponse(json.dumps(
        {
            'name'   :album.name,
            'id'     :album.id,
            'count'  :album.modcount,
            'deleted':pic_id,
        }
        ),
        content_type="application/json"
        )

@login_required
def delete_id_from_album( request, album_id, pic_id ):

    try:
        entries = AlbumContent.objects.filter(
                            Q( album_id=album_id )
                          & Q( entry_id=pic_id )
                          ).delete()
        return redirect( '/albums/?ID=' + str( album_id ) )
    except:
        pass

    return redirect( '/albums/' )

@login_required
def organisation_bubble_ids( request, pic_ids ):

    ids = pic_ids.split( ',' )

    query = 'SELECT id, sortkey FROM homePIX_picturefile ORDER BY sortkey LIMIT 1;'
    top_pics = PictureFile.objects.raw( query )
    top_pic = top_pics[ 0 ]

    sort_key = int( top_pic.sortkey );

    for id in ids:
        if len( id ) > 0:

            query = 'SELECT id, sortkey FROM homePIX_picturefile WHERE id=' + id + ';'
            print( query )

            pics = PictureFile.objects.raw( query )
            pic  = pics[ 0 ]
            print("Oldkey= "  + str( pic.sortkey ) )

            sort_key -= 1

            pic.sortkey = sort_key
            pic.save()

            print("Newsort= " + str( pic.sortkey ) )

    return HttpResponse(json.dumps(
        {
            'name'   :'universe'
        }
        ),
        content_type="application/json"
        )

@login_required
def set_album_thumb( request, album_id, pic_id ):

    album = get_object_or_404(   Album,       id = int( album_id ) )
    picture = get_object_or_404( PictureFile, id = int( pic_id ) )

    album.thumbnail = picture
    album.save()

    return redirect( '/albums/' )

@login_required
def new_album( request ):

    if request.method == 'GET':

        now = datetime.now()

        name = request.GET.get( 'name', now.strftime("%d/%m/%Y %H:%M:%S") )

        album = Album()
        album.name = name
        album.save()

    return redirect( '/albums/' )

@login_required
def set_folder_thumb( request, album_id, pic_id ):

    folder = get_object_or_404(  Directory,   id = int( album_id ) )
    picture = get_object_or_404( PictureFile, id = int( pic_id ) )

    folder.thumbnail = picture
    folder.save()

    return redirect( '/folders/' )

@login_required
def add_comment_to_post( request, album_id, pic_id ):

   post = get_object_or_404( PictureFile, pk = pic_id )

   if request.method == 'POST':

        form = CommentForm( request.POST )

        if form.is_valid():

            item = form.save( commit = False )
            item.post = post
            item.save()

            return redirect( '../', pk = post.id )
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
