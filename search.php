<?php include 'common.php';?>
<?php  

    $req_dump = $_REQUEST;

    $pwd      = shell_exec( "pwd" );
    $pwd = trim(preg_replace('/\s\s*/', '', $pwd));

    $dir = $pwd . preg_replace('/\/pics\//', '/../', $url);

    unlink( $albumFilename );

    $allExt    = '[jJ][pP][gG]';
    $filepat   = '/(?<!tnl_)(?<!low_)[A-Za-z0-9_]*\.' . $allExt . '/';
    $fragpat   = '/([0-9]*)(\t )*\.\/(.*\.' . $allExt . ')/';
    $findpat   = '/([0-9]*)\t\.\/(.*\.txt)/';

    $value = $req_dump[ "search" ];

    $albumFilename = $dir . "/../." . $value . ".listing.txt";
    $keywordsFilename = $dir . "/.keywords.txt";

    $grepcmd = "grep -r -i --include .*.jpg.txt " . $value . " " . $dir . "/../ > " . $keywordsFilename;
    $results = exec( $grepcmd );

    $value = preg_replace( '{^\"(.*)\"$}', '${1}', $value );
    $results = preg_grep( "/" . $value . "/i", file( $keywordsFilename ) );

    $n = 0;

    $fileListing = "";

    foreach($results as $result) {

        $result = preg_replace( '{^(.*)[\/]\.([^/]*\.)txt.*$}', '${1}/${2}', $result );

        $fileListing .= ++$n . "\t" . $result;
    }

    $cnt = iterateOverFiles( $fileListing, $filepat, $fragpat, function( $file ) 
    {
        global $albumFilename;

        file_put_contents( $albumFilename, $file . "\n", FILE_APPEND );

        return true;
    } );

    echo "../." . $value . ".listing.txt";
?>
