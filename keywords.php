<?php  

    $req_dump = $_REQUEST;

    $keywords = $req_dump[ "keyword" ];
    $first    = $req_dump[ "firstN"  ];
    $last     = $req_dump[ "lastN"   ];
    $url      = $req_dump[ "path"    ];

    $pwd      = shell_exec( "pwd" );
    $pwd = trim(preg_replace('/\s\s*/', '', $pwd));

    $file = $pwd . preg_replace('/\/pics\//', '/../', $url);

    $cmd = "exiftool " . $file . " | grep Keywords | sed -e 's:.*\: ::'";
    $result = shell_exec( $cmd );
    $result = trim(preg_replace('/\s\s+/', '', $result));

    $cmd = "echo \"" . $keywords . "," . $result . "\" | sed -e 's:,:\\n:g' | grep -v '^[ \\t]*$' | sort | uniq";
    $sorted = shell_exec( $cmd );
    $sorted = trim(preg_replace('/\s\s*/', ',', $sorted));
    $sorted = trim(preg_replace('/,\s*$/', '', $sorted));

    $cmd = "exiftool -Keywords=\"" . $sorted . "\" -overwrite_original " . $file;
    shell_exec( $cmd );

    $txtfile = preg_replace('/^(.*\/)([^\/]*)$/', '${1}.${2}.txt', $file);
    $cmd = "exiftool \"" . $file . "\" > \"" . $txtfile . "\"";
    shell_exec( $cmd );

    $cmd = "exiftool " . $file . " | grep Keywords | sed -e 's:.*\: ::'";
    $result = shell_exec( $cmd );

    echo $result;
?>
