<!DOCTYPE html>
<html>
  <head>
      <title>Picture Browser Sub-Directory</title>
      <meta charset="UTF-8" />
      <link href="../css3-loesung-text-shadow.css"
          rel="stylesheet" />
  </head>
  <body>
<?php

    $picdir = getcwd();
    $filepat = '/^(?<!\.tnl_)[A-Z][A-Za-z0-9_]*\.jpg/';

    echo "<h1>Pictures in $picdir</h1>" . "<br>";

    // Open a directory, and read its contents
    $dir = scandir($picdir);

    foreach($dir as $token)
    {
	if(($token != ".") && ($token != ".."))
	{
            $hasJPEGS = FALSE;

            $iterator = new RecursiveDirectoryIterator('.');
            $filter = new RegexIterator($iterator->getChildren(), '/t.(jpg)$/');
            $filelist = array();

            foreach($filter as $entry) {

                $hasJPEGS = TRUE;
                break;
            }

            if ( $hasJPEGS ) {
    
	        if(is_dir($path.'/'.$token))
	        {
		    $folders[] = $token;
	        }
	        else
	        {
		    $files[] = $token;
	        }
            }
	}
    }

    foreach($folders as $folder)
    {
	$newpath = $path.'/'.$folder;
	echo "<a href = tema2.php?cale=$newpath> [ $folder ]/index.php </a>" . "<br>";
    }

    foreach($files as $file)
    {
	if (preg_match( $filepat, $file )) {
	    echo "<a href=$file><img src=.tnl_$file alt=$file style=\"border:2px solid white\"></img></a>";
	} else {
            echo "A match was not found.";
	}
    }
?>
  </body>
</html>

