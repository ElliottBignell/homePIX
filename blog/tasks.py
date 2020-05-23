import os
import sys
import glob
import fnmatch
import re
from background_task import background
from blog.models import PictureFile, Directory, Keywords
from blog.exifdata import get_field
from django.db.models import Q

@background( schedule=1 )
def bulk_saver( path ):

    pattern = '/*.[Jj][Pp][Gg]'

    print( 'Scanning directory: ' + path )

    dirs  = {}

    directory_set = Directory.objects.select_related( 'thumbnail' )

    for r, d, f in os.walk( path ):

        for dirname in d:

            newpath  = os.path.relpath( r + '/' + dirname, path )
            pathname = newpath.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')
            newdir = None

            newpathname = path + '/' + pathname

            try:
                newdir = directory_set.get( path = newpathname )
            except Directory.DoesNotExist:
                newdir = Directory()
                newdir.path = newpathname
                newdir.save()

            print( newdir )
            dirs[ newpath ] = newdir

    picture_set = None

    try:
        picture_set = ( PictureFile.objects
                            .select_related( 'keywords' )
                            .select_related( 'path' )
                        )
    except:
        print( 'Abort on exception' )
        return

    print( 'Scanned subdirectories' )

    for root, directory in dirs.items():

        newdir = None
        pathname = directory.path
        print( 'Scanning ... ' + pathname )

        try:
            newdir = directory_set.get( path = pathname )
        except Directory.DoesNotExist:
            continue

        for filename in  glob.glob( pathname + pattern ):

            newfile = None
            newpath  = os.path.relpath( filename, pathname )
            newfilename = newpath.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')

            try:
                newfile = picture_set.get( Q( path_id = newdir.id ) & Q( file = newfilename ) )
            except PictureFile.DoesNotExist:
                continue

            if newfile:

                if not newdir.thumbnail or newdir.thumbnail.id != newfile.id:
                    newdir.thumbnail = newfile
                    newdir.save
                break

    for root, directory in dirs.items():

        pathname = directory.path

        try:
            newdir = directory_set.get( path = pathname )
        except Directory.DoesNotExist:
            continue

        pic_count = 0

        for filename in  glob.glob( pathname + pattern ):

            newfile = None
            newpath  = os.path.relpath( filename, pathname )
            newfilename = newpath.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')

            try:
                newfile = picture_set.get( Q( path_id = newdir.id ) & Q( file = newfilename ) )
            except PictureFile.DoesNotExist:

                try:
                
                    newfile = PictureFile()
                    newfile.path = newdir
                    newfile.file = newfilename
                    newfile.sortkey = newfile.id
                    newfile.save()
                except Exception as e:
                    print( "Exception ",  e )
                    print( "Secondary exception with filename: " + newfilename )
                    continue

            description = get_field( newfilename, 'ImageDescription', newfilename ) 

            if newfile.title != description:

                newfile.title = description
                newfile.save()

            new_key = None

            keys = ""

            try:

                keys = get_field( newfilename, 'Keywords', "" ) 

                if keys:

                    try:
                        new_key = Keywords.objects.get( keywords = keys )
                    except Keywords.DoesNotExist:

                        m = re.match( r'(.*)(\.[jJ][pP][gG])$', keys )

                        if not m:

                            print( 'Found: ' + keys )
                            new_key = Keywords()
                            new_key.keywords = keys
                            new_key.save()
            except:
                keys = ""

            if new_key:

                newfile.keywords = new_key
                newfile.save()

            pic_count += 1

            if pic_count > 10:
                break

    for root, directory in dirs.items():

        newdir = None
        pathname = directory.path

        try:
            newdir = directory_set.get( path = pathname )
        except Directory.DoesNotExist:
            continue

        for filename in  glob.glob( pathname + '/*.[Jj][Pp][Gg]' ):

            newfile = None
            newpath  = os.path.relpath( filename, pathname )
            newfilename = newpath.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')

            try:
                newfile = picture_set.get( Q( path_id = newdir.id ) & Q( file = newfilename ) )
            except PictureFile.DoesNotExist:
                continue

            if newfile:
                newdir.thumbnail = newfile
                newdir.save
                break

    print( 'Finished: ' + path )
