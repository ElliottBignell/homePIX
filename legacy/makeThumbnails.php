<?php  
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
?>

