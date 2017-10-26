<?php  

    $req_dump = $_REQUEST;

    $keywords = "";
    $opcode   = $req_dump[ "opcode" ];
    $url      = $req_dump[ "path"    ];
    $index    = $req_dump[ "index"   ];

    $pwd      = shell_exec( "pwd" );
    $pwd = trim(preg_replace('/\s\s*/', '', $pwd));

    $file = $pwd . preg_replace('/\/pics\//', '/../', $url);

    function setTitle( $title )
    {
        global $file;

        $cmd = "exiftool -ImageDescription=\"" . $title . "\" -overwrite_original " . $file;
        shell_exec( $cmd );

        $cmd = "exiftool " . $file . " | grep \"Image Description\" | sed -e 's:.*\: ::'";

        return shell_exec( $cmd );
    }

    function setKeywords( $keywords, $opCodeIdx )
    {
        global $file;

        $sorted = $keywords;

        switch ( $opCodeIdx ) {
        case 1:
            break;
        case 2:
            $cmd = "exiftool " . $file . " | grep Keywords | sed -e 's:.*\: ::'";
            $retval = shell_exec( $cmd );
            $retval = trim(preg_replace('/\s\s+/', '', $retval));

            $cmd = "echo \"" . $keywords . "," . $retval . "\" | sed -e 's:,:\\n:g' | grep -v '^[ \\t]*$' | sort | uniq";
            $sorted = shell_exec( $cmd );
            break;
        case 3:
            $cmd = "exiftool " . $file . " | grep Keywords | sed -e 's:.*\: ::'";
            $retval = shell_exec( $cmd );
            $retval = trim(preg_replace('/\s\s+/', '', $retval));

            $sorted = implode( ",", array_diff( explode( ",", $retval ), explode( ",", $keywords ) ) );
            break;
        }

        $sorted = trim(preg_replace('/\s\s*/', ',', $sorted));
        $sorted = trim(preg_replace('/,\s*$/', '', $sorted));

        $cmd = "exiftool -Keywords=\"" . $sorted . "\" -overwrite_original " . $file;
        shell_exec( $cmd );

        $txtfile = preg_replace('/^(.*\/)([^\/]*)$/', '${1}.${2}.txt', $file);
        $cmd = "exiftool \"" . $file . "\" > \"" . $txtfile . "\"";
        shell_exec( $cmd );

        $cmd = "exiftool " . $file . " | grep Keywords | sed -e 's:.*\: ::'";

        return shell_exec( $cmd );
    }

    $result = "Not initialised";

    switch ( $opcode ) {
    case '0':
        $keywords = $req_dump[ "title" ];
        $result = setTitle( $keywords );
        break;
    case '1':
        $keywords = $req_dump[ "keyword" ];
        $result = setKeywords( $keywords, 1 );
        break;
    case '2':
        $keywords = $req_dump[ "keyword" ];
        $result = setKeywords( $keywords, 2 );
        break;
    case '3':
        $keywords = $req_dump[ "keyword" ];
        $result = setKeywords( $keywords, 3 );
        break;
    default:
        $result = "Fail";
        break;
    }

    echo $index . "\t" . $result;
?>
