<!DOCTYPE html>
<html>
    <head>

        <title>Image Page</title>
        <meta charset="UTF-8" />


        <link href="clearall.css" rel="stylesheet" />
        <link href="css3-loesung-text-shadow.css" rel="stylesheet" />

        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js"></script>
        <script src="albumMover.js" async=""></script>
        <script src="navigation.js" async=""></script>
        <script src="lazysizes-gh-pages/lazysizes.min.js" async=""></script>

    </head>
    <body onload="imgnav = new fileMover();imgnav.navigate( index, null );detectswipe('main', myfunction);">
        <?php
        
            include dirname(__FILE__)."/common.php";

            function doDimensions( $filename, $absDir, $which )
            {
                $exiffile = preg_replace( '{^(.*/)*([^/]*\.jpg)$}', '../$1.$2.txt', $filename );

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
                $filename = preg_replace( '{^(.*/)*([^/]*\.jpg)$}', '.$2.txt', $filename );
                $exiffile = $absDir . "/" . $filename;

                if ( !file_exists( $exiffile ) ) {
                    exec( "./makeThumbnail.sh -e $absDir/$filename" );
                }

                if ( file_exists( $exiffile ) ) {

                    $exiffile = $absDir . "/" . $filename;

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

            function doGPS( $listing )
            {
                $gps_elem  = array();
                $gps_val   = "60,60";

                if ( preg_match('/([0-9]*) deg ([0-9]*)\' ([0-9]*)(\.([0-9]*))*\" [NS], ([0-9]*) deg ([0-9]*)\' ([0-9]*)(\.([0-9]*))*\" [EW]/', $listing, $gps_elem) ) {

                    $seconds = $gps_elem[ 3 ] . $gps_elem[ 4 ];
                    $latitude = $gps_elem[ 1 ] + $gps_elem[ 2 ] / 60 + $seconds / 3600;

                    $seconds = $gps_elem[ 8 ] . $gps_elem[ 9 ];
                    $longitude = $gps_elem[ 6 ] + $gps_elem[ 7 ] / 60 + $seconds / 3600;

                    $gps_val = $latitude . "," . $longitude;
                }

                 return "https://maps.googleapis.com/maps/api/staticmap?key=AIzaSyA218PwQJKRsvO8n1ZJk5Dfmgtz8JaVUN8&center=" . $gps_val . "&markers=color:red%7Clabel:Picture%7C" . $gps_val . "&zoom=11&size=200x300&sensor=false";
            }

            function doExif( $filename, $absDir )
            {
                $exiffile = preg_replace( '{^(.*/)*([^/]*\.jpg)$}', '$1.$2.txt', $filename );
                $exiffile = $absDir . "/" . $exiffile;

                if ( !file_exists( $exiffile ) ) {
                    exec( "./makeThumbnail.sh -e $absDir/$filename" );
                }

                if ( file_exists( $exiffile ) ) {

                    $listing = file_get_contents( $exiffile);
                    $listing = nl2br($listing, true);

                    return doGPS( $listing );
                }
                
                return "";
            }

            $picdir = $_GET["dir"];
            $filename = $_GET["file"];
        
            $prettydir = preg_replace( '{^/(.*)$}', '$1', $picdir );
            $lofile    = preg_replace( "{^(.*)/([^/]*\.jpg)$}", '$1/.low_$2', $filename );
            $absDir = preg_replace( '/[\/]pics/', '..', $picdir, 1 );

            $stylestr = "display:block;margin-left:auto;margin-right:auto;border:0px;ipadding:0px;max-width:100%;max-height:100%;object-fit:contain;";

    $img_url = doExif( $filename, $absDir );

    echo <<<HEADERTABLE
            <table id="maintab" style="width:100%;height:100%;padding:0px;border:0px;">
                <tr style="background-color:black;width:100%;padding:0px;">
                    <td colspan=3 style="background-color:black;column-span:all;padding:0px;">
                        <a href=index.php><h1>&#x2302;</h1></a>
                    </td>
                    <td style="background-color:black;column-span:all;padding:0px;">
                        <input type="text" onkeydown="doSubmit()" id="find" style="align:right;width:32vw;">
                    </td>
                </tr>
                <tr colspan=4 style="width:100%;height:100%;object-fit:contain;">
                    <td style="width:25px">
                        <a href=javascript:retreat()><h1>&#9664;</h1></a>
                    </td>
                    <td id="picframe" style="max-width:99%;max-height:99%;object-fit:contain;">
                        <a id="mainlink" href=$filename>
                            <img id="main" class="lazyload" data-src="$picdir/$filename" src="$picdir/$lofile" alt="$picdir/$filename" style="$stylestr"/>
                        </a>
                    </td>
                    <td style="width:25px;">
                        <a href=javascript:advance()><h1>&#9654;</h1></a>
                    </td>
                    <td id="sidebar" style="width:220px;vertical-align:top;">
                        <div style="font:inherit;overflow:auto;vertical-align:top;">
                            <span id="title" class="titletext" style="font-size:100%;">
                                Title<br>
                            </span>
                            <span class="titletext">
                                Taken on 
                            </span>
                            <span id="datetime" class="titlecontent">
                                2000-00-00<br>
                            </span>
                            <span class="titletext">
                                Filename<br>
                            </span>
                            <span id="filename" class="titlecontent">
                                $filename<br>
                            </span>
                            <span class="titletext">
                                Description<br>
                            </span>
                            <span id="description" class="titlecontent">
                                $comment<br>
                            </span>
                            <span class="titletext">
                                Dimensions 
                            </span>
                            <span id="dimensions" class="titlecontent"> ? <br> </span>
                            <span id="megapixels" class="titlecontent"> ? <br></span>
                            <span class="titletext">
                                AspectRatio
                            </span>
                            <span id="aspect" class="titlecontent"> ? <br> </span>
                            <span class="titletext">
                                Camera
                            </span>
                            <span id="camera" class="titlecontent"> ? <br></span>
                            <span class="titletext">
                                Exposure
                            </span>
                            <span id="fnumber" class="titlecontent"> ? </span>
                            <span id="exposure" class="titlecontent"> ? </span>
                            <span id="exposureprogram" class="titlecontent"> ? </span>
                            <span id="iso" class="titlecontent"> ? </span>
                            <span id="flash" class="titlecontent"> ? <br></span>
                            <span class="titletext">
                                Lens 
                            </span>
                            <span id="lensid" class="titlecontent"> ? <br></span>
                            <span id="lens" class="titlecontent"> ? <br></span>
                            <span id="focusmode" class="titlecontent"> ? <br></span>
                            <span id="focusdistance" class="titlecontent"> ? <br></span>
                            <span id="focallength" class="titlecontent"> ? </span>
                            <span id="focallen35mm" class="titlecontent"> ? <br></span>
                            
                            <div id="panel1" style="display:inline">
                                <a href=javascript:panel1() class="unembellish">
                                    <span class="titletext">
                                        Keywords<br>
                                    </span>
                                </a>
                                <span id="keywords" class="titlecontent" style="font-size:100%;">
                                   ?<br>
                                </span>
                            </div>
                            <div id="panel2" style="display:none">
                                <a href=javascript:panel2() class="unembellish">
                                    <span class="titletext">
                                        Location<br>
                                    </span>
                                </a>
                                <span id="map">
                                    <img src="$img_url"/>
                                /<span>
                            </div>
                            <span class="titletext">
                                Copyright
                            </span>
                            <span id="copyright" class="titlecontent"> ? <br></span>
                        </div>
                    </td>
                </tr>
                <tr style="background-color:black;width:100%;padding:0px;">
                    <td id="footbar" colspan=4 style="background-color:black;column-span:all;padding:0px;">
                        <h1>$filename in $prettydir</h1>
                    </td>
                </tr>
            </table>
HEADERTABLE;

            $listing = file_get_contents( ".." . $dirname . "/.listing.txt" );
            $listing = nl2br($listing, true);
            $fileListing = listDir( $absDir );
            $index = 1;

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
                    "Focal Length",                    //  16.0 mm35 mm equivalent: 24.0 mm)
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
                    "Lens ID",                         // : Tamron AF 16-300mm f/3.5-6.3 Di II VC PZDB016),
                    "Lens",                            //  16-300mm f/3.5-6.3 G VR
                    "Megapixels"                       //  29.3
                );

            iterateOverFiles( $fileListing, $filepat, $fragpat, function( $file ) {

                    global $thumbnail, $index, $absDir, $keys;

                    $file =  preg_replace( "{^\./(.*)$}", "$1", $file );

                    echo "<div style=\"display:none;\" id=img" . $index . ">";
                    echo "/pics/$file";
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
  </body>
</html>


