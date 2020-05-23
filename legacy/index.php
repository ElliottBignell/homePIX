<!DOCTYPE html>
<html>
<head>

    <title>Picture Browser Home Directory</title>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="icon" href="puddycat.jpg">

    <link href="css3-loesung-text-shadow.css" rel="stylesheet" />
    <link href="directories.css" rel="stylesheet" />
    <link href="clearall.css" rel="stylesheet" />
    <link href="tooltips.css" rel="stylesheet" />
    <link href="panels.css" rel="stylesheet" />

    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    <script src="mover.js" type="text/javascript"></script>
    <script src="albumMover.js" type="text/javascript"></script>
    <script src="lazysizes-gh-pages/lazysizes.min.js" type="text/javascript"></script>
    <script src="resize.js"></script>
    <script src="navigation.js" type="text/javascript" async=""></script>

</head>
<body>
<?php include 'detectmobilebrowser.php';?>
<?php include 'makeThumbnails.php';?>
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
$filename  = $_GET["file"];
$findstr   = $_GET["find"];
$pathpat   = '/^[A-Za-z0-9_]*$/';
$cwd       = getcwd();
    
$prettydir = preg_replace( '{^/(.*)$}', '$1', $picdir );
$lofile    = preg_replace( "{^(.*)/([^/]*\.jpg)$}", '$1/.low_$2', $filename );
$absDir = preg_replace( '/[\/]pics/', '..', $picdir, 1 );
$dirname = preg_replace( '/[\/]pics/', '..', $picdir, 1 );

$filepat   = '/(?<!tnl_)(?<!low_)[A-Za-z0-9_]*\.' . $allExt . '/';
$fragpat   = '/([0-9]*)(\t )*\.\/(.*\.' . $allExt . ')/';
$findpat   = '/([0-9]*)\t\.\/(.*\.txt)/';

$is = isMobile();

$headerheight = ( 0 == $is ? "70px" : "100px" );
$maintop      = ( 0 == $is ?  "80px" : "110px" );

function echoSearchField( $width )
{
    return "
              <form id='multisearch'>
                  <fieldset>
                      <input id='find' style='align:right;width:" . $width . ";' type='text' value='$findValue'>
                      <input type='submit' style='display:none'/>
                  </fieldset>
              </form>
              <!--<form action='$_SERVER[PHP_SELF]' method='POST'>-->
            ";
}

function panelSwitch( $text, $findValue )
{
    return "<td style='background-color:black;column-span:all;padding:0px;width:3vw;text-align:center;'>
              <div class='tooltip'>
                  <a href=javascript:togglePanel()>
                      <h2>$text</h2>
                  </a>
                  <span class='tooltiptext'>
                      $findValue
                  </span>
              </div>
           </td>";
}

function echoBox( $findValue, $width )
{
  return "<td style='background-color:black;padding:0px;width:" . $width . ";text-align:center;'>
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
    global $headerheight, $is;

    echo <<<HEADERTABLE
      <div id="pageheader" style="height:$headerheight;">
          <table style="background-color:black;width:100vw;padding:0px;">
          <tr>
              <td style="column-span:all;padding:0px;width:1vw;">
              </td>
              <td style=";column-span:all;padding:0px;width:3vw;">
                  <div class="tooltip">
                    <a href=index.php>
                        <table>
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
              <td style="column-span:all;padding:0px;width:55vw;">
              </td>
             <td style='column-span:all;padding:0px;width:34vw;'>
             </td>
HEADERTABLE;
    if ( 0 == $is ) {

        echo "          <td>";
        echo echoSearchField( "32vw" );
        echo "          </td>";
        echo "          <td>";
        echo echoBox( "Tool Tip", "3vw" );
        echo "          </td>";
    }
    else
        echo "<td></td><td></td>";

    echo panelSwitch( "&#x2295;", "Tool Tip" );

    if ( 0 == $is ) {

        //echo panelSwitch( "&#x2611;", "Tool Tip" );
        //echo panelSwitch( "&#x2622;", "Tool Tip" );
        //echo panelSwitch( "&#x262E;", "Tool Tip" );
    }

        echo <<<HEADERTABLE3
                  <td style="column-span:all;padding:0px;width:1vw;">
                  </td>
HEADERTABLE3;

    if ( 1 == $is ) {

        echo <<<HEADERTABLE4
                  <td style="column-span:all;padding:0px;width:1vw;">
                  </td>
          </tr>
          <tr>
HEADERTABLE4;
        echo "<td colspan='6' style='width:100%;'>";
        echo echoSearchField( "90%" );
        echo "</td>";
        echo echoBox( "Tool Tip", "2vw" );
    }

    if ( 1 != $is ) {

        echo <<<HEADERTABLE5
          </tr>
      </table>
    <table style="width:100vw;padding:0px;border:none;font-size:14pt;font-weight:bold;">
        <tr style="width:100%;padding:0px;">
            <td style="padding:0px;width:20%;">
            </td>
            <td style="padding:0px;padding-right:15px;width:15%;text-align:right;">
                PHOTOS
            </td>
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
HEADERTABLE5;
    }

    echo <<<HEADERTABLE6
        </tr>
    </table>
  </div>

    <script type="text/javascript">

        $(document).ready(function() {

            var photos = $('#photocounthidden').html();
            var albums = $('#albumcounthidden').html();

            $('#photocount').text( photos );
            $('#albumcount').text( albums );

            $(window).trigger('resize');
        });
    </script>
HEADERTABLE6;
}

function echoDirectory( $folder, $picdir, $cnt, $thumbnail, $file, $index, $dragdropclass )
{
    $formatdir  = preg_replace( '/\s/', "%20", $folder );
    $formatfile = preg_replace( '/\s/', "%20", $file   );

    echo <<<DIRECTORY
        <div class="tooltip $dragdropclass" id="dir_$index">
            <a id="dirlink_$index" href=index.php?dir="/pics$picdir/$formatdir"&file=$formatfile>
                <span class="tooltipsubject" id="dir-number_$index">
                    <img class="lazyload" id="img-number_$index" src="/pics/$thumbnail" data-src="/pics/$thumbnail" alt="$file" style="border:2px solid white;height:200px;">
                </span>
                <div id="header_dir_o_$index" class="tooltipleft tooltipdir">
                    <div id="header_dir_$index" class="tooltiplefttext">
                        $folder
                    </div>
                </div>
                <span class="tooltiptext tooltipbottom">
                    <article>Contains $cnt files</article>
                </span>
            </a>
        </div>
DIRECTORY;
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

echo "<div id=\"mainlist\" style=\"top:" . $maintop . ";overflow-y:scroll;overflow-x:hidden;\">";

$isFind = ( preg_match( '/^[\/]".*"$/', $picdir ) );

if ( $isFind ) {
    $findValue = preg_replace( '{^/"(.*)"}', '${1}',  $picdir);
}

if ( ! $isFind ) {

    $isFind = ( 0 != strlen( $findstr ) );

    if ( $isFind ) {
        $findValue = $findstr;
    }
}

if ( $isFind || $findValue ) {

    $n = 0;

    $folder = "\"" . $findValue . "\"";

    if ( ! $isFind ) {
        echoDirectory( $folder, "$picdir", $cnt, $thumbnail, $file, $n, "" );
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

if ( ! $isFind ) {

    // Albums
    $albums = glob( "../.*.listing.txt" );
    $albumcnt = 0;

    if ( !empty( $albums ) && "" == $picdir) {

        if ( 0 == $is ) {

            echo "<span class=\"unembellish\">" . 
                 "Albums<br>" .
                 "</span>";
        }

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

                echoDirectory( $title, "", $cnt, $thumbnail, $file, $index++, "droppable" );
                return ( $cnt > 0 );
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

            echoDirectory( $folder, "$picdir", $cnt, $thumbnail, $file, $index++, "" );

            $photocnt += $cnt;
        }

        echo "<br>";
    }
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
        <div class="tooltip droppable draggable" id="div_$index" style="min-height:200px;">
            <a id="piclink_$index" href="image.php?file=$file&dir=/pics$dir&index=$index&count=$cnt">
                <section class="wrapper" id="file-number_$index">
                    <span class="tooltipsubject">
                        <img id="picture_$index" 
                             class="lazyload" 
                             src="$loThumbnail" 
                             data-src="$thumbnail" 
                             alt="$file" 
                             style="border:$colour;position:relative;top:100%;left:0%;z-index:0;height:200px;">
                        </img>
                    </span>
                </section>
                <div id="header_o_$index" class="tooltipleft tooltiptext">
                    <div id="header_$index" class="tooltiplefttextnooff">
                        $tipText
                    </div>
                </div>
                <span class="tooltiptext tooltiptop">
                    <article id="art_pageno_$index">$index</article>
                </span>
                <span class="tooltiptext tooltipbottom">
                    <article id="art_keywords_$index">No keywords</article>
                </span>
            </a>
            <span class="tooltipedit">
                <form id="editprops">
                    <fieldset>
                        <input id="title" type="text" value="test">
                    </fieldset>
                </form>
            </span>
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

echo <<<PANEL
<div id="slideout">
    <div class="tooltip droppable" id="div_0" style="min-height:200px;position:absolute;top:10;left:10;border:black;">
        <section class="wrapper" id="file-number_0">
            <span class="tooltipsubject" style="position:relative;top:10;left:10;">
                <img id="picture_0" 
                     class="lazyload" 
                     src="todo.jpg" 
                     data-src="todo.jpg" 
                     alt="todo.jpg" 
                     style="border:black;position:relative;top:10px;left:10px;z-index:0;height:200px;">
                </img>
            </span>
            <form id="editprops" style="position:absolute;top:0;left:0;">
                <fieldset>
                    <input id="title" type="text" value="New Album" style="position:absolute;top:10;left:20px;width:250px">
                </fieldset>
            </form>
        </section>
        <div id="header_o_0" class="tooltipleft tooltiptext">
            <div id="header_0" class="tooltiplefttextnooff">
                Drop Here!
            </div>
        </div>
        <span class="tooltiptext tooltipbottom">
            <article id="art_keywords_0">Drop pictures to create<br>a new album</article>
        </span>
    </div>
</div>
PANEL;

?>
<?php include 'hiddenTags.php';?>
</div>
</body>
</html>

