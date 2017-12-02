<!DOCTYPE html>
<html>
<head>
<title>File Writer PHP page</title>
<meta charset="UTF-8" />

</head>
<body>
<?php  

    $req_dump = $_REQUEST;

    $files = $req_dump[ "files" ];
    $album = $req_dump[ "album" ];
    $album = "." . $album . ".listing.txt";

    $cmd = "( echo \"" . $files . "\"; cat " . $album . ") | sed -e 's:;:\\n:g' > tmp.txt";
    shell_exec( $cmd );

    $cmd = "cat tmp.txt ../". $album . " | sed s:^/pics/:./: | awk '!x[$0]++' > tmp2.txt";
    $result = shell_exec( $cmd );

    $result = shell_exec( "mv tmp2.txt ../" . $album );
    echo $result;
?>
</body>
</html>
