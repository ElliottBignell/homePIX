<?php

    function doDimensions( $filename, $absDir, $which )
    {
        $exiffile = preg_replace( '{^(.*/)*[\.]*([^/]*\.jpg)(\.txt)*$}', '../$1.$2.txt', $filename );

        if ( !file_exists( $exiffile ) ) {
            exec( "./makeThumbnail.sh -e $absDir/$filename" );
        }

        $targetW = 90;
        $targetH = 60;

        if ( file_exists( $exiffile ) ) {

            $listing = file_get_contents( $exiffile);
            $listing = nl2br($listing, true);

            $width  = array();
            $height = array();

            if ( preg_match( '/(Image Width) *: *(.*)/',  $listing, $width ) ) {
                $targetW = $width [ 2 ];
            }

            if ( preg_match( '/(Image Height) *: *(.*)/', $listing, $height ) ) {
                $targetH = $height[ 2 ];
            }
        }

        $retval = 0;

        switch ( $which ) {
        case 0:
            $retval = $targetW / $targetH;
            break;
        case 1:
            $retval = $targetW;
            break;
        case 2:
            $retval = $targetH;
            break;
        }

        return $retval;
    }

    function doTags( $filename, $absDir, $keys, &$tags )
    {
        $file = preg_replace( '{^(.*/)*[\.]*([^/]*\.jpg)(\.txt)*$}', '.$2.txt', $filename );
        $exiffile = $absDir . "/" . $file;

        if ( !file_exists( $exiffile ) ) {
            exec( "./makeThumbnail.sh -e $absDir/$file" );
        }

        if ( file_exists( $exiffile ) ) {

            $exiffile = $absDir . "/" . $file;

            $listing = file_get_contents( $exiffile);
            $listing = nl2br($listing, true);

            $elem  = array();

            foreach( $keys as $key ) {

                $regex = '{ *' . $key . ' *: *(.*)}';

                if ( preg_match( $regex, $listing, $elem ) ) {
                    $tags[ $key ] = $elem[ 1 ];
                }
            }
        }
    }

    $listing = file_get_contents( ".." . $dirname . "/.listing.txt" );
    $listing = nl2br($listing, true);

    $index = 1;

    $absDir = str_replace(array('\'', '"'), '', $absDir);

    $fileListing = listDir( $absDir );

    $allExt    = '[jJ][pP][gG]';
    $filepat   = '/(?<!tnl_)(?<!low_)[A-Za-z0-9_]*\.' . $allExt . '/';
    $fragpat   = '/([0-9]*)(\t )*\.\/(.*\.' . $allExt . ')/';

    $keys = array(
        "Image Description",               //  Wallis
        "File Size",                       //  9.6 MB
        "Artist",                          //  Elliott Bignell
        "Copyright",                       //  Elliott Bignell
        "File Type",                       //  JPEG
        "File Type Extension",             //  jpg
        "Camera Model Name",               //  NIKON D300
        "Exposure Time",                   //  1/125
        "F Number",                        //  13.0
        "Exposure Program",                //  Manual
        "ISO",                             // : 200
        "Date/Time Original",              //  2017:07:26 13:04:31
        "Focal Length",                    //  16.0 mm
        "Quality",                         //  RAW
        "White Balance",                   //  5000K
        "Focus Mode",                      //  Manual
        "ISO Setting",                     //  200
        "Vibration Reduction",             //  On
        "Shutter Speed",                   //  1/125
        "Metering Mode",                   //  Center-weighted average
        "Focal Length",                    //  16.0 mm35 mm equivalent: 24.0 mm
        "Light Source",                    //  Unknown
        "Exposure Difference",             //  +0.5
        "Flash Mode",                      //  Did Not Fire
        "Shooting Mode",                   //  Continuous, Exposure Bracketing
        "Focus Distance",                  //  21.13 m
        "Shutter Count",                   //  226896
        "Multi Exposure Mode",             //  Off
        "Multi Exposure Shots",            //  0
        "Directory Number",                //  136
        "File Number",                     //  9792
        "User Comment",                    //  Elliott Bignell, 2016
        "Exposure Mode",                   //  Manual
        "Focal Length In 35mm Format",     //  24 mm
        "Keywords",                        //  Schweiz,Wallis,Valais,Boulder,Matterhorn,Cervino
        "Lens",                            //  16-300mm f/3.5-6.3
        "Comment",                         //  Wallis
        "Aperture",                        //  13.0
        "Auto Focus",                      //  Off
        "Flash",                           //  No Flash
        "Lens ID",                         // : Tamron AF 16-300mm f/3.5-6.3 Di II VC PZDB016,
        "Lens",                            //  16-300mm f/3.5-6.3 G VR
        "Megapixels"                       //  29.3
        );

        iterateOverFiles( $fileListing, $filepat, $fragpat, function( $file ) {

            global $thumbnail, $index, $absDir, $keys;

            $file =  preg_replace( "{^\./(.*)$}", "/pics/$1", $file );

            echo "<div style=\"display:none;\" id=img" . $index . ">";
            echo "$file";
            echo "</div>";

            $thumbnail   = "";

            if ( preg_match( '/^[^\/]*\.jpg$/', $file ) ) {
                $thumbnail   = ".low_" . $file;
            }
            else {
                $thumbnail =  preg_replace( "{^(.*)\/([^/]*\.jpg)$}", "$1/.low_$2", $file );
            }

            $tags = array();

            doTags( $file, $absDir, $keys, $tags );

            $keytags = array();

            $keytags[ "low"             . $index ] = "/pics/$thumbnail" ;
            $keytags[ "aspectRatio"     . $index ] = doDimensions( $file, $absDir, 0 );
            $keytags[ "picWidth"        . $index ] = doDimensions( $file, $absDir, 1 );
            $keytags[ "picHeight"       . $index ] = doDimensions( $file, $absDir, 2 );
            $keytags[ "title"           . $index ] = $tags[ "Image Description" ];
            $keytags[ "comment"         . $index ] = $tags[ "Comment" ];
            $keytags[ "keywords"        . $index ] = $tags[ "Keywords" ];
            $keytags[ "datetime"        . $index ] = $tags[ "Date/Time Original" ];
            $keytags[ "copyright"       . $index ] = $tags[ "Copyright" ];
            $keytags[ "camera"          . $index ] = $tags[ "Camera Model Name" ];
            $keytags[ "exposure"        . $index ] = $tags[ "Exposure Time" ];
            $keytags[ "fnumber"         . $index ] = $tags[ "F Number" ];
            $keytags[ "exposureprogram" . $index ] = $tags[ "Exposure Program" ];
            $keytags[ "iso"             . $index ] = $tags[ "ISO" ];
            $keytags[ "focallength"     . $index ] = $tags[ "Focal Length" ];
            $keytags[ "focusmode"       . $index ] = $tags[ "Focus Mode" ];
            $keytags[ "focusdistance"   . $index ] = $tags[ "Focus Distance" ];
            $keytags[ "focallen35mm"    . $index ] = $tags[ "Focal Length In 35mm Format" ];
            $keytags[ "lens"            . $index ] = $tags[ "Lens" ];
            $keytags[ "flash"           . $index ] = $tags[ "Flash" ];
            $keytags[ "lensid"          . $index ] = $tags[ "Lens ID" ];
            $keytags[ "megapixels"      . $index ] = $tags[ "Megapixels" ];

            foreach( $keytags as $key => $value ) {

                echo "<span style=\"display:none;\" id=\"" . $key . "\">" .
                    preg_replace( '{<[a-zA-z]*>}', '', $value ) .
                    "</span>";
            }

            $index += 1;

            return true;
        } 
    );
?>
