<!DOCTYPE html>
<html>
<head>
<title>Picture Browser Home Directory</title>
<meta charset="UTF-8" />

<link href="css3-loesung-text-shadow.css" rel="stylesheet" />
<link href="directories.css" rel="stylesheet" />
<link href="clearall.css" rel="stylesheet" />
<link href="tooltips.css" rel="stylesheet" />

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script src="albumMover.js" type="text/javascript"></script>
<script src="navigation.js" async=""></script>
<script src="lazysizes-gh-pages/lazysizes.min.js" async=""></script>
<script src="resize.js" async=""></script>

</head>
<body>
<?php  

    error_reporting( E_ALL | E_STRICT );

    include dirname(__FILE__)."/common.php";

    $findValue = false;

    $mergefolders = array();
    $folders      = array();

    $thumbnail   = "";
    $loThumbnail = "";

    $defaultExt= 'jpg';
    $allExt    = '[jJ][pP][gG]';
    $picdir    = $_GET["dir"];
    $filename   = $_GET["file"];
    $pathpat   = '/^[A-Za-z0-9_]*$/';
        
    $prettydir = preg_replace( '{^/(.*)$}', '$1', $picdir );
    $lofile    = preg_replace( "{^(.*)/([^/]*\.jpg)$}", '$1/.low_$2', $filename );
    $absDir = preg_replace( '/[\/]pics/', '..', $picdir, 1 );

    $filepat   = '/(?<!tnl_)(?<!low_)[A-Za-z0-9_]*\.' . $allExt . '/';
    $fragpat   = '/([0-9]*)(\t )*\.\/(.*\.' . $allExt . ')/';
    $findpat   = '/([0-9]*)\t\.\/(.*\.txt)/';

    function echoButton( $text, $findValue )
    {
        return "<td style='background-color:black;column-span:all;padding:0px;width:3vw;'>
                  <div class='tooltip'>
                      <a href=index.php><h2>$text</h2></a>
                      <span class='tooltiptext'>
                          $findValue
                      </span>
                  </div>
               </td>";
    }

    function echoBox( $findValue )
    {
      return "<td style='background-color:black;column-span:all;padding:0px;width:3vw;'>
              <div class='tooltip'>
                  <a href=index.php>
                      <div id='search_box'><div id='search'></div><span id='cabe'></span></div>
                  </a>>
                  <span class='tooltiptext'>
                      $findValue
                  </span>
              </div>
          </td>";
    }

    function echoHeader( $findValue )
    {
        echo <<<HEADERTABLE
          <table style="background-color:black;width:100vw;padding:0px;">
          <tr style="background-color:black;width:100vw;padding:0px;">
              <td style="background-color:black;column-span:all;padding:0px;width:1vw;">
              </td>
              <td style="background-color:black;column-span:all;padding:0px;width:3vw;">
                  <div class="tooltip">
                    <a href=index.php>
                        <table
                            <tr>
                                <td style="padding-right:5px;">
                                    <h3>HOMEpix</h3>
                                </td>
                                <td style="padding-left:5px;">
                                    <h2>&#x2302;</h2>
                                </td>
                            </tr>
                        </table>
                    </a>
                    <span class="tooltiptext">
                        Tool Tip
                    </span>
                  </div>
              </td>
              <td style="background-color:black;column-span:all;padding:0px;width:55vw;">
              </td>
              <td style="background-color:black;column-span:all;padding:0px;width:34vw;">
                  <form id="multisearch">
                      <fieldset>
                          <input id="find" style="align:right;width:32vw;" type="text" value="$findValue">
                          <input type="submit" style="display:none"/>
                      </fieldset>
                  </form>
                  <!--<form action="$_SERVER[PHP_SELF]" method="POST">-->
              </td>
HEADERTABLE;
        echo echoBox( "Tool Tip" );
        echo echoButton( "&#x2295;", "Tool Tip" );
        echo echoButton( "&#x2611;", "Tool Tip" );
        echo echoButton( "&#x2622;", "Tool Tip" );
        echo echoButton( "&#x262E;", "Tool Tip" );
        echo <<<HEADERTABLE3
              <td style="background-color:black;column-span:all;padding:0px;width:1vw;">
              </td>
          </tr>
          </table>
            <table style="width:100vw;padding:0px;border:none;font-size:14pt;font-weight:bold;">
                <tr style="width:100%;padding:0px;">
                    <td style="padding:0px;width:20%;">
                    </td>
                    <td style="padding:0px;padding-right:15px;width:15%;text-align:right;">
                        PHOTOS
                    <td style="padding:0px;width:15%;text-align:left;font-weight:normal;">
                        <span id="photocount"></span>
                    </td>
                    <td style="padding:0px;padding-right:15px;width:15%;text-align:right;">
                        ALBUMS
                    <td style="padding:0px;width:15%;text-align:left;font-weight:normal;">
                        <span id="albumcount"></span>
                    </td>
                    <td style="padding:0px;width:20%;">
                    </td>
                </tr>
            </table>
            <script type="text/javascript">

                $(document).ready(function() {

                    var photos = $('#photocounthidden').html();
                    var albums = $('#albumcounthidden').html();

                    $('#photocount').text( photos );
                    $('#albumcount').text( albums );
                });
            </script>
HEADERTABLE3;
    }

    function echoDirectory( $folder, $picdir, $cnt, $thumbnail, $file, $index )
    {
        $formatdir  = preg_replace( '/\s/', "%20", $folder );
        $formatfile = preg_replace( '/\s/', "%20", $file   );

        echo <<<DIRECTORY
            <div class="tooltip">
                <a href=index.php?dir="/pics$picdir/$formatdir"&file=$formatfile>
                    <section class="wrapper" id="dir-number_$index">
                        <header><h1>$folder</h1></header>
                        <article>
                            <img class="lazyload" id="img-number_$index" src="/pics/$thumbnail" data-src="/pics/$thumbnail" alt="$file" style="border:2px solid white">
                        </article>
                    </section>
                    <span class="tooltiptext">
                        <article>$folder</article>
                        <article>Contains $cnt files</article>
                    </span>
                </a>
            </div>
DIRECTORY;
    }

    function makeThumbnails( $file, &$thumb, &$loThumb )
    {
        global $defaultExt;
        global $allExt;

        if ( !preg_match( '/[\.]tnl_/', $file ) ) {

            setThumbnails( "{^(.*)\/([^/]*\.$allExt)$}", $file, $thumb, $loThumb );

            if ( 0 == strlen( $thumb ) ) {
                $thumb = ".default.$defaultExt";
            }

            $exists = preg_replace( '/[\.]/', getcwd() . '/..', $thumb, 1 );

            if ( !file_exists( $exists ) ) {
                exec( "./makeThumbnail.sh -f \"$exists\"" );
            }

            $exists = preg_replace( '/[\.]/', getcwd() . '/..', $loThumb, 1 );

            if ( !file_exists( $exists ) ) {
                exec( "./makeThumbnail.sh -g \"$exists\"" );
            }
        }
    }

    function setThumbnails( $regex, $file, &$thumb, &$loThumb )
    {
        global $allExt;

        if ( preg_match( '/^[^\/]*\.' . $allExt . '$/', $file ) ) {

            $thumb   = ".tnl_" . $file;
            $loThumb = ".tnl_" . $file;
        }
        else {

            $thumb   =  preg_replace( $regex, "$1/.tnl_$2", $file );
            $loThumb =  preg_replace( $regex, "$1/.tnllo_$2", $file );
        }
    }

    // Strip surrouding quotes from directory name
    $picdir =  preg_replace( "{^\"(.*)\"$}", "$1", $picdir );

    $fileListing = "";

    if ( $_POST[ 'find' ] ) {
        $findValue = $_POST[ 'find' ];
    }

    echoHeader( $findValue );

    $isFind = ( preg_match( '/^[\/]".*"$/', $picdir ) );

    if ( $isFind ) {
        $findValue = preg_replace( '{^/"(.*)"}', '${1}',  $picdir);
    }

    if ( $isFind || $findValue ) {

        $results = preg_grep( "/$findValue/i", file( './.keywords.txt' ) );

        $n = 0;

        foreach($results as $result) {

            $result = preg_replace( '{^(.*)[\/]\.([^/]*\.)txt.*$}', '${1}/${2}' . $defaultExt, $result );

            $fileListing .= ++$n . "\t" . $result;
        }

        $folder = "\"" . $findValue . "\"";

        $cnt = iterateOverFiles( $fileListing, $filepat, $fragpat, function( $file ) 
        {
            global $thumbnail, $loThumbnail;

            makeThumbnails( $file, $thumbnail, $loThumbnail );

            return false;
        } );

        if ( ! $isFind ) {
            echoDirectory( $folder, "$picdir", $cnt, $thumbnail, $file, $n );
        }
    }

    $prettydir = preg_replace( '{^[\"]*(.*)"[\"]*$}', '$1', $picdir );
    $prettydir = preg_replace( '{^/pics/}', '', $prettydir );

    if ( ! $isFind ) {

        if ( !empty( $filename ) ) {
            $fileListing = listAlbum( $filename );
        }
        else {
            $fileListing = listDir( "../" . $prettydir );
        }
    }

    $index = 1;

    // Albums
    $albums = glob( "../.*.listing.txt" );
    $albumcnt = 0;

    if ( !empty( $albums ) && "" == $picdir) {
    
        echo "<span class=\"unembellish\">" . 
             "Albums<br>" .
             "</span>";

        foreach( $albums as $token ) {

            $albumcnt++;

            $cnt = iterateOverFiles( $token, '/.*/', '/.*/', function( $file ) 
            {
                global $thumbnail, $loThumbnail, $firstfile;

                $title = preg_replace( '{\.\./\.(.*)\.listing\.txt}', "$1", $file );
                $album = file_get_contents( $file );

                $files = explode( "\n", $album );
                $cnt = count( $files );

                if ( $cnt > 0 ) {
                    makeThumbnails( $files[ 0 ], $thumbnail, $loThumbnail );
                }

                echoDirectory( $title, "", $cnt, $thumbnail, $file, $index++ );

                return true;
            } );
        }
    }

    // Subdirectories
    $photocnt = 0;

    if ( count( $folders ) > 0 ) {

        echo "<span class=\"unembellish\">" . 
             "<br>Directories<br>" .
             "</span>";

        foreach($folders as $folder)
        {
            $thumbnail   = "";
            $loThumbnail = "";

            $firstfile = listDir( "../$picdir/$folder", true );

            if ( 0 == strlen( $firstfile ) ){
                $thumbnail = ".default.$defaultExt";
            }

            $cnt = iterateOverFiles( $firstfile, $filepat, $fragpat, function( $file ) 
            {
                global $thumbnail, $loThumbnail, $firstfile;

                makeThumbnails( $file, $thumbnail, $loThumbnail );

                return false;
            } );

            echoDirectory( $folder, "$picdir", $cnt, $thumbnail, $file, $index++ );

            $photocnt += $cnt;
        }

        echo "<br>";
    }

    $index    = 1;
    $selindex = 1;

    $files = explode( "\n", $fileListing );

    $cnt = count( $files );

    iterateOverFiles( $fileListing, $filepat, $fragpat, function( $file ) 
    {
        global $photocnt; $photocnt++;
        return true;
    } );

    echo "<div id=\"photocounthidden\" style=\"visibility:hidden;\">$photocnt</div>";
    echo "<div id=\"albumcounthidden\" style=\"visibility:hidden;\">$albumcnt</div>";

    iterateOverFiles( $fileListing, $filepat, $fragpat, function( $file ) 
    {
        global $index, $cnt, $selindex;

        makeThumbnails( $file, $thumbnail, $loThumbnail );

                $dir = preg_replace( '{^\.*(/[^/]*/)(.*)$}', '$1', $file,            1 );
               $file = preg_replace( '{^\.*/([^/]*)/(.*)$}', '$2', $file,            1 );
          $thumbnail = preg_replace( '/[\.]/',               '/pics',  $thumbnail,   1 );
        $loThumbnail = preg_replace( '/[\.]/',               '/pics',  $loThumbnail, 1 );

        $tipText = preg_replace( '/.*[\/]/', '', $file );

        $colour = $index != $selindex ? "2px solid white" : "2px solid red";

        echo <<<IMAGE
            <div class="tooltip" id="div_$index">
                <section class="wrapper" id="dir-number_$index">
                    <a id="piclink_$index" href="image.php?file=$file&dir=/pics$dir&index=$index&count=$cnt">
                        <img id="picture_$index" class="lazyload" src="$loThumbnail" data-src="$thumbnail" alt="$file" style="border:$colour;"></img>
                        <span class="tooltipheader">
                            <header id="header_$file"><h1>$tipText</h1></header>
                        </span>
                    </a>
                </section>
            </div>
IMAGE;

        $index += 1;

        return true;
    } );

echo <<<HEADERTABLE2
    <script type="text/javascript">
        imgnav = new albumMover( '../$prettydir/' );
    </script>
HEADERTABLE2;
?>
<?php include 'hiddenTags.php';?>
</body>
</html>

