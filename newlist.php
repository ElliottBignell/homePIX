<!DOCTYPE html>
<html>
<head>
<title>File Writer PHP page</title>
<meta charset="UTF-8" />

</head>
<body>
<?php  

    $req_dump = $_REQUEST;
    $fp = fopen('request.log', 'a');

    $from = $req_dump[ "moveFrom" ];
    $to   = $req_dump[ "moveTo"   ];
    $url  = $req_dump[ "path"     ];

    $cmd = "printf '%s\\" . "n' " . $from . "m" . $to . " w q | ed -s " . $url . ".listing.txt";
    // $cmd = "printf '%s\\" . "n' " . $from . "m" . $to . " " . $to . "-m" . $from . "- w q | ed -s " . $url . ".listing.txt";
file_put_contents( "/media/Seagate/www/request.txt", $cmd . "\n", FILE_APPEND );
    fwrite( $fp, $cmd . "\n" );

    shell_exec( $cmd );

    fclose($fp);
?>
</body>
</html>
