<!DOCTYPE html>
<html>
    <head>

        <title>Image Page</title>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link href="directories.css" rel="stylesheet" />
        <link href="clearall.css" rel="stylesheet" />
        <link href="css3-loesung-text-shadow.css" rel="stylesheet" />

        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js"></script>
        <script src="mover.js" type="text/javascript"></script>
        <script src="fileMover.js" type="text/javascript"></script>
        <script src="navigation.js" type="text/javascript"></script>
        <script src="lazysizes-gh-pages/lazysizes.min.js" type="text/javascript"></script>
        <script src="resize.js"></script>

    </head>
    <body>
        <?php
        
            error_reporting( E_ALL | E_STRICT );

            include dirname(__FILE__)."/common.php";

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
                $exiffile = preg_replace( '{^(.*/)*[\.]*([^/]*\.jpg)(\.txt)$}', '$1.$2.txt', $filename );
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
            $lofile    = preg_replace( "{^(.*)/([^/]*\.jpg)$}", '$1/.tnllo_$2', $filename );
            $absDir = preg_replace( '/[\/]pics/', '..', $picdir, 1 );

            if ( !file_exists( $lofile ) ) {
                exec( "./makeThumbnail.sh -o $absDir/$lofile" );
            }

            $stylestr = "display:block;margin-left:auto;margin-right:auto;border:0px;ipadding:0px;max-width:100%;max-height:100%;object-fit:contain;";

    $img_url = doExif( $filename, $absDir );

    echo <<<HEADERTABLE
        <div id="pageheader">
              <table style="background-color:black;width:100vw;padding:0px;">
                <tr style="background-color:black;width:100%;padding:0px;">
                    <td colspan=3 style="background-color:black;column-span:all;padding:0px;">
                        <a href=index.php><h1>&#x2302;</h1></a>
                    </td>
                    <td style="background-color:black;column-span:all;padding:0px;">
                        <input type="text" onkeydown="doSubmit()" id="find" style="align:right;width:32vw;">
                    </td>
                </tr>
            </table>
        </div>
        <div id="mainpic">
            <table id="maintab" style="width:100%;height:calc( 100% - 40px );padding:0px;border:0px;">
                <tr colspan=4>
                    <td style="width:25px;vertical-align:middle;">
                        <a href=javascript:retreat()><h1>&#9664;</h1></a>
                    </td>
                    <td id="picframe" style="width:calc( 100% - 270px );object-fit:contain;vertical-align:middle;">
                        <a id="mainlink" href="$picdir$filename">
                            <img id="main" class="lazyload" data-src="$picdir$filename" src="$picdir/$lofile" alt="$picdir$filename" style="$stylestr"/>
                        </a>
                    </td>
                    <td style="width:25px;vertical-align:middle;">
                        <a href=javascript:advance()><h1>&#9654;</h1></a>
                    </td>
                    <td style="width:220px;">
                        <div style="font:inherit;overflow:auto;vertical-align:top;position:absolute;top:65px;width:200px;height:calc( 100% - 310 );">
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
            </table>
        </div>
        <div id="pagefooter">
            <table style="background-color:black;width:100vw;padding:0px;height:45px;">
                <tr style="background-color:black;width:100%;padding:0px;">
                    <td id="footbar" colspan=4 style="background-color:black;column-span:all;padding:0px;">
                        <h1>$filename in $prettydir</h1>
                    </td>
                </tr>
            </table>
        </div>
HEADERTABLE;

echo <<<HEADERTABLE2
    <script type="text/javascript">
        imgnav = new fileMover( '../$prettydir/' );
        imgnav.navigate( 1, null );
        detectswipe('main', myfunction);
    </script>
HEADERTABLE2;

    $filename = "";

    ?>

    <?php include 'hiddenTags.php';?>
  </body>
</html>


