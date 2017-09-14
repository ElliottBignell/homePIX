<?php 

    function merge( $listing, $fulldir, $dirname, $token, $depth )
    {
        $mergedirs = '/(jpegs|done|DCIM|work|parts)/';
        $newlisting = "";

        if ( preg_match( $mergedirs, $token ) ) {
        //    $newlisting = listDir( $fulldir, $depth + 1 );
        }
        elseif ( ( $token != "." ) && ( $token != ".." ) ) {
            $newlisting = iterateOverDir( $dirname, $token, $depth );
        }

        if ( strlen( $listing ) > 0 && strlen( $newlisting ) > 0 ) {
            $listing = "$listing<br>\n$newlisting";
        }
        else {
            $listing = "$listing$newlisting";
        }

        return $listing;
    }

    function listAlbum( $file )
    {
        $listing = file_get_contents( $file );
        $listing = nl2br($listing, true);

        return $listing;
    }

    function listDir( $dirname, $depth = 1 )
    {
        try {

            if ( !file_exists( "$dirname/.listing.txt" ) ) {
                exec( "./makeThumbnail.sh -l \"$dirname\"" );
            }

            exec( "./makeThumbnail.sh -u \"$dirname\"" );

            $listing = file_get_contents( "$dirname/.listing.txt" );
            $listing = nl2br($listing, true);

            // Open a directory, and read its contents
            $dir = scandir( $dirname );

            foreach( $dir as $token )
            {
                $fulldir = $dirname . "/" . $token;

                if ( is_dir( $fulldir ) && is_readable( $fulldir ) ) {
                    $listing = merge( $listing, $fulldir, $dirname, $token, $depth );
                }
            }

            return $listing;
        }
        catch ( Exception $e ) {
            echo 'Caught exception in listDir: ',  $e->getMessage(), "<br>";
        }
    }

    function iterateOverDir( $dirname, $token, $depth )
    {
        global $folders;
        global $allExt;

        $formatdir =  "$dirname/$token" ;
        $listing   =  "";

        if ( is_dir( "$formatdir" ) )
        {
            try {

                $hasJPEGS = FALSE;

                $directory = new RecursiveDirectoryIterator( "$formatdir" );
                $iterator  = new RecursiveIteratorIterator( $directory, RecursiveIteratorIterator::LEAVES_ONLY, RecursiveIteratorIterator::CATCH_GET_CHILD );
                $filter    = new RegexIterator( $iterator, '/\.(' . $allExt . ')$/i' );

                foreach ( $filter as $entry ) {

                    if ($entry) {

                        $hasJPEGS = TRUE;
                        $listing = "1\t$entry";
                        break;
                    }
                }

                if ( $hasJPEGS && 1 == $depth) {
                    $folders[] = $token;
                } 
            }
            catch ( Exception $e ) {
                echo 'Caught exception in iterateOverDir: ',  $e->getMessage(), "<br>";
            }
        }
    
        return $listing;
    }

    function iterateOverFiles( $fileListing, $filepat, $fragpat, $processMatch )
    {
        $files = explode( "\n", $fileListing );

        if ( count( $files ) > 0 ) {

            foreach($files as $line)
            {
                $elements  = array();

                preg_match( $fragpat, $line, $elements );

                $file = $elements[ 0 ];

                if ( preg_match( $filepat, $file ) ) {

                    if ( ! $processMatch( $file ) ) {
                        break;
                    }
                }
            }
        }

        return count( $files );
    }
?>
