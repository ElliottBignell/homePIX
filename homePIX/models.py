import os
import re
import sys
import fnmatch
from django.db import models, transaction
from django import forms
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
from pprint import pprint
from django.conf import settings
from random import randint

# Create your models here.

class FileType( forms.Field ):

    filename = models.CharField( max_length = 200, default='.default.jpg' )

    def __str__( self ):
        return self.filename

class ListModel( models.Model ):

    class Meta:
        abstract = True

    @transaction.atomic
    def bulk_saver( self, words_list ):

        for key, value in words_list.items():
            value.save()

class Keywords( ListModel ):

    keywords = models.TextField( unique = True )
    count = models.PositiveIntegerField( default = 0 )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.

    @property
    def modlist( self ):
        return self.keywords.split( ',' )

    @property
    def modid( self ):
        return self.id

    def __str__( self ):
        return self.keywords

class ThumbnailBase( ListModel ):

    pic_size = [ 200, 200 ]

    class Meta:
        abstract = True

    @property
    def modpath( self ):
        pass

    @property
    def modthumb( self ):
        pass

    @property
    def modid( self ):
        pass

    @property
    def thumb_size( self ):
        return self.pic_size[ 1 ]

    @thumb_size.setter
    def thumb_size( self, value ):
        self.pic_size[ 1 ] = value

    @property
    def modtype( self ):
        pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__( self ):
        return self.keywords

class Directory( ThumbnailBase ):

    path  = models.TextField( unique = True )
    count = models.PositiveIntegerField( default = 0 )
    thumbnail = models.ForeignKey( 'PictureFile', on_delete = models.CASCADE, null = True, blank = True )

    def __str__( self ):
        return os.path.relpath( self.path, settings.MEDIA_ROOT )

    def get_absolute_url( self ):

        if '???' == self.path:
            return reverse( 'tasks/' + self.path )
        else:
            return reverse( 'folders/' )

    @property
    def modpath( self ):
        return os.path.relpath( self.path, settings.MEDIA_ROOT )

    @property
    def modthumb( self ):

        if self.thumbnail and self.thumbnail.path == self:
            return self.thumbnail
        else:

            objs = PictureFile.objects.select_related( 'path' ).filter( path = self.id )

            if ( objs ):
                return ( objs[ 0 ] )
            else:

                regex = self.path + '/.+' 
                queryset = Directory.objects.select_related( 'thumbnail' ).filter( path__regex=regex )

                if queryset:

                    thumb = None

                    for dir in queryset:

                        objs = PictureFile.objects.select_related( 'path' ).filter( path = dir )

                        if ( objs ):
                            thumb = ( objs[ 0 ] )
                            break

                    return thumb

        return ( PictureFile.objects
                    .select_related( 'path' )
                    [ 0 ]
                )

    @property
    def modid( self ):
        return self.id

    @property
    def modcount( self ):

        cnt = PictureFile.objects.select_related( 'path' ).filter( path = self.id ).count()

        regex = self.path + '/.+' 
        queryset = Directory.objects.select_related( 'thumbnail' ).filter( path__regex=regex )

        if queryset:

            for dir in queryset:
                cnt += PictureFile.objects.select_related( 'path' ).filter( path = dir ).count()

        return cnt

    @property
    def modtype( self ):
        return 2

class PictureFile( ThumbnailBase ):

    file = models.CharField( max_length = 200, default='.default.jpg' )
    path = models.ForeignKey( Directory, on_delete = models.CASCADE, null = True )
    title = models.TextField()
    objects = models.Manager()
    keywords = models.ForeignKey( Keywords, on_delete = models.CASCADE, null = True )
    sortkey = models.PositiveIntegerField( unique = True,  null = True  )
    added_on = models.DateTimeField( auto_now_add = True,  null = True )
    taken_on = models.DateTimeField( auto_now_add = True,  null = True )
    last_modified = models.DateTimeField( auto_now = True, null = True )

    mod_file    = ''
    mod_preview = ''
    mod_random_key = 0

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.mod_file = '.'    + re.sub( r'(.*)(\.[jJ][pP][gG])', r'\1_200\2',     self.file )
        self.mod_preview = '.' + re.sub( r'(.*)(\.[jJ][pP][gG])', r'\1_200_5pc\2', self.file )
        self.mod_random_key = randint( 1, 0x7FFFFFFF)

    def save(self, *args, **kwargs):

        if '???' == self.file:
            return HttpResponseRedirect( "/background" + '/media/pi/Archive' )
        else:
            super().save(*args, **kwargs)  # Call the "real" save() method.

    def publish( self ):
        self.save()

    def approve_comments( self ):
        return self.comments.filter( approved_comment = True )

    def get_absolute_url( self ):

        if '???' == self.file:
            return reverse( 'tasks' )
        else:
            return reverse( 'folders' )

    @property
    def modpath( self ):
        return 'pics/' + os.path.relpath( self.path.path, settings.MEDIA_ROOT )

    @property
    def modfile( self ):
        return self.mod_file

    @property
    def modpreview( self ):
        return self.mod_preview

    @property
    def modthumb( self ):
        return self

    @property
    def modid( self ):
        return self.id

    @property
    def modtype( self ):
        return 1

    @property
    def modid( self ):
        return self.id

    @property
    def modrandomkey( self ):
        return self.mod_random_key

    def __str__( self ):
        return self.path.path + '/' + self.title

class Album( ThumbnailBase ):

    name = models.TextField( default='New Album' )
    count = models.PositiveIntegerField( default = 0 )
    thumbnail = models.ForeignKey( 'PictureFile', on_delete = models.CASCADE, null = True, blank = True )

    def get_absolute_url( self ):
        return reverse( 'album' )

    def __str__( self ):
        return self.name

    @property
    def modpath( self ):
        return 'albums/' + name

    @property
    def modthumb( self ):

        queryset =  PictureFile.objects.filter( id = self.thumbnail_id )

        if queryset.count()  > 0:
            return self.thumbnail
        else:

            queryset = AlbumContent.objects.select_related( 'entry' ).filter( album = self.id )
            
            if queryset.count()  > 0:
                return ( queryset[ 0 ].entry )

        return None

    @property
    def modid( self ):
        return self.id

    @property
    def modcount( self ):

        queryset = AlbumContent.objects.filter( album = self.id )

        if queryset:
            return queryset.count()

        return 0

    @property
    def modtype( self ):
        return 3

class AlbumContent( ListModel ):

    album = models.ForeignKey(       Album, on_delete = models.CASCADE )
    entry = models.ForeignKey( PictureFile, on_delete = models.CASCADE )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def get_absolute_url( self ):
        return reverse( 'albumcontent' )

    def __str__( self ):
        return str( self.album ) + ":" + str( self.entry )

    @property
    def modthumb( self ):

        objs = PictureFile.objects.select_related( 'path' ).filter( id = self.entry_id )

        if ( objs ):
            return ( objs[ 0 ] )

        return None

class Comment( models.Model ):

    post = models.ForeignKey( 'blog.PictureFile', related_name = 'comments', on_delete = models.CASCADE )
    author = models.CharField( max_length = 200 )
    text = models.TextField()
    create_date = models.DateTimeField( default = timezone.now )
    approved_comment = models.BooleanField( default = False )

    def approve( self ):
        self.approved_comment = True
        self.save()

    def get_absolute_url( self ):
        return reverse( 'picture_list' )

    def __str__( self ):
        return self.text
