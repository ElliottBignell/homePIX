import os
import subprocess
from pprint import pprint

def get_field( filename, field, default ):

    value = default

    try:

        p = subprocess.Popen(
                'exiftool ' + filename + ' -' + field, 
                shell=True,
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT
            )

        for line in p.stdout:
            k, v = line.decode( 'UTF-8' ).split( ':' )
            value = v.strip()
            break
    except:
        return default

    return value

def reduce_file( filename, file_out, path, compression ):

    try:

        if not os.path.isfile( path + '/' + file_out ):

            p = subprocess.call( [
                    'convert', 
                    path + '/' + filename, 
                    '-resize', 
                    '200x200^', 
                    '-quality', 
                    compression, 
                    path + '/' + file_out 
                ] )
        # p = subprocess.Popen( cmd, shell=True, stdin=stdin, stdout=stdout, stderr=stderr )
    except:
        print( "Error calling ImageMagick with " + path + '/' + file_out )
