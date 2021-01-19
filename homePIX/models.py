import os
import re
from django.db import models, transaction
from django import forms
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
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

    id   = models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)
    hits = models.PositiveIntegerField( default = 0 )

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

    def __str__( self ):
        return self.keywords

class Directory( ThumbnailBase ):

    path       = models.TextField( unique = True )
    count      = models.PositiveIntegerField( default = 0 )
    thumbnail  = models.ForeignKey( 'PictureFile', on_delete = models.CASCADE, null = True, blank = True )
    remote_key = models.CharField( max_length = 20, default='fjWM4F' )
    remote_id  = models.PositiveIntegerField( default = 157544933 )

    def __str__( self ):
        return os.path.relpath( self.path, settings.MEDIA_ROOT )

    def get_absolute_url( self ):

        if '???' == self.path:
            return reverse( 'tasks/' + self.path )
        else:
            return reverse( 'folders/' + self.path )

    @property
    def modpath( self ):
        return os.path.relpath( self.path, settings.MEDIA_ROOT )

    @property
    def modname( self ):
        return os.path.relpath( self.path, settings.MEDIA_ROOT ).split( '/' )[ -1 ]

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
    def modurl( self ):
        return 'ID=' + str( self.remote_id ) + '&Key=' + self.remote_key

    @property
    def modtype( self ):
        return 2

class PictureFile( ThumbnailBase ):

    file              = models.CharField( max_length = 200, default='.default.jpg' )
    path              = models.ForeignKey( Directory, on_delete = models.CASCADE, null = True )
    title             = models.TextField(null = True)
    objects           = models.Manager()
    keywords          = models.ForeignKey( Keywords, on_delete = models.CASCADE, null = True )
    sortkey           = models.PositiveIntegerField( unique = True,  null = True )
    added_on          = models.DateTimeField( auto_now_add  = True,  null = True )
    taken_on          = models.DateTimeField( auto_now_add  = True,  null = True )
    last_modified     = models.DateTimeField( auto_now      = True,  null = True )
    location          = models.CharField( max_length        =  200,  null = True )
    primaryCategory   = models.CharField( max_length        =   20,  null = True )
    secondaryCategory = models.CharField( max_length        =   20,  null = True )

    mod_file    = ''
    mod_preview = ''
    mod_random_key = 0

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.mod_file =     re.sub( r'(.*)(\.[jJ][pP][gG])', r'\1_200\2',     self.file )
        self.mod_preview =  re.sub( r'(.*)(\.[jJ][pP][gG])', r'\1_200_5pc\2', self.file )
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
    def modfilestemmed( self ):
        filename = self.file # re.sub( 'https://elliottbignell.smugmug.com/', '/picture/', self.file )
        return re.sub( r'(.*)/X3/(.*)-X3(\.[jJ][pP][gG])', r'\2-L\3', filename )

    @property
    def modfilename( self ):
        filename = self.file # re.sub( 'https://elliottbignell.smugmug.com/', '/picture/', self.file )
        return re.sub( r'(.*)/X3/(.*)-X3(\.[jJ][pP][gG])', r'\1/S/\2-L\3', filename )

    @property
    def modfile( self ):
        filename = self.file # re.sub( 'https://elliottbignell.smugmug.com/', '/picture/', self.file )
        return re.sub( r'(.*)/X3/(.*)-X3(\.[jJ][pP][gG])', r'\1/M/\2-M\3', filename )

    @property
    def modfile_orig( self ):
        filename = self.file
        filename = re.sub( r'(.*)/X3/(.*)-X3(\.[jJ][pP][gG])', r'\1/M/\2-M\3', filename )
        filename = filename.replace( ':', '%3A' )
        filename = filename.replace( '/', '%2F' )
        return filename

    @property
    def modsmallfile( self ):
        filename = self.file # re.sub( 'https://elliottbignell.smugmug.com/', '/picture/', self.file )
        return re.sub( r'(.*)/X3/(.*)-X3(\.[jJ][pP][gG])', r'\1/S/\2-S\3', filename )

    @property
    def modtinyfile( self ):
        filename = self.file # re.sub( 'https://elliottbignell.smugmug.com/', '/picture/', self.file )
        return re.sub( r'(.*)/X3/(.*)-X3(\.[jJ][pP][gG])', r'\1/Ti/\2-Ti\3', filename )

    @property
    def modlargefile( self ):
        filename = self.file # re.sub( 'https://elliottbignell.smugmug.com/', '/picture/', self.file )
        return re.sub( r'(.*)/X3/(.*)-X3(\.[jJ][pP][gG])', r'\1/X3/\2-X3\3', filename )

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
    def modtitle( self ):
        if self.title:
            return self.title;

        return "Unnamed picture"

    @property
    def modrandomkey( self ):
        return self.mod_random_key

    @property
    def moddimensions( self ):
        return { "width":100, "height":200 }

    def __str__( self ):

        ret = self.path.path

        if not self.title is None:
            ret += '/' + self.title

        ret += '/' + str( self.id )

        return ret

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
        return 'albums/' + self.name

    @property
    def modthumb( self ):

        objs = PictureFile.objects.filter( id = self.thumbnail_id )

        if ( objs ):
            self.thumbnail = ( objs[ 0 ] )

        if self.thumbnail:
            return self.thumbnail

        return None

    @property
    def modid( self ):
        return self.id

    @property
    def modname( self ):
        return self.name

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
        return str( self.album.id ) + ":" + str( self.entry.id )

    @property
    def modthumb( self ):

        objs = PictureFile.objects.select_related( 'path' ).filter( id = self.entry_id )

        if ( objs ):
            return ( objs[ 0 ] )

        return None

    @property
    def modtype( self ):
        return 4

class Comment( models.Model ):

    post = models.ForeignKey( 'homePIX.PictureFile', related_name = 'comments', on_delete = models.CASCADE )
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

class CSVEntry( models.Model ):

    filename          = models.CharField( max_length =  200 )
    imageRef          = models.CharField( max_length =   20 )
    caption           = models.CharField( max_length = 2000 )
    tags              = models.CharField( max_length = 2000 )
    licenseType       = models.CharField( max_length =    5 )
    userName          = models.CharField( max_length =  200 )
    superTags         = models.CharField( max_length = 2000 )
    location          = models.CharField( max_length =  200 )
    dateTaken         = models.DateField( null=True, blank=True )
    numberOfPeople    = models.PositiveIntegerField( default = 0 )
    modelRelease      = models.CharField( max_length =   20 )
    isThereProperty   = models.CharField( max_length =    1 )
    propertyRelease   = models.CharField( max_length =   20 )
    primaryCategory   = models.CharField( max_length =   20 )
    secondaryCategory = models.CharField( max_length =   20 )
    imageType         = models.CharField( max_length =   20 )
    exclusiveToAlamy  = models.CharField( max_length =    1 )
    additionalInfo    = models.CharField( max_length =  200 )
    status            = models.CharField( max_length =   10 )

    def __str__( self ):
        return self.filename + self.imageRef + self.dateTaken

class CSVContent( ListModel ):

    picturefile = models.ForeignKey( PictureFile, on_delete = models.CASCADE )
    entry       = models.ForeignKey(    CSVEntry, on_delete = models.CASCADE )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def get_absolute_url( self ):
        return reverse( 'csvcontent' )

    def __str__( self ):
        return str( self.picturefile ) + ":" + str( self.entry )

    @property
    def modthumb( self ):

        objs = PictureFile.objects.select_related( 'path' ).filter( id = self.entry_id )

        if ( objs ):
            return ( objs[ 0 ] )

        return None

    @property
    def modtype( self ):
        return 5
