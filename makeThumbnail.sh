#!/bin/bash

while [[ $# -gt 0 ]]; do

    key="$1"
    corrpath=`realpath "$2"`
    basepath=`realpath "$2/.."`

    case $key in
        -e|--exif)

            picfile=`echo "$corrpath" | sed -e "s:\.txt$::" -e "s:\(.*/\)*\.*\([^/]*\):\1\2:"`

            if [ -n "$picfile" ]; then 

                echo "$picfile" | sed "s:\(.*/\)*\([^/]*\):exiftool \"\1\2\" > \"\1.\2.txt\":" >> /tmp/log.txt
                echo "$picfile" | sed "s:\(.*/\)*\([^/]*\):exiftool \"\1\2\" > \"\1.\2.txt\":" | sh

            fi

            shift # past argument
        ;;

        -g|--gile)

            tnl=`echo $corrpath | sed s:\.tnllo_::`

            if [ ! -f $corrpath ] || [ $corrpath -nt $tnl ]; then 
                convert $tnl -resize x200 -quality 10% $corrpath
                echo "`date` making `pwd`\\t$corrpath" >> /tmp/log.txt
            fi

            shift # past argument
        ;;

        -f|--file)

            tnl=`echo $corrpath | sed s:\.tnl_::`

            if [ ! -f $corrpath ] || [ $corrpath -nt $tnl ]; then 
                convert $tnl -resize x200 -quality 90% $corrpath
                echo "`date` making `pwd`\\t$corrpath" >> /tmp/log.txt
            fi

            shift # past argument
        ;;

        -l|--list)
            echo "`date` $basepath $corrpath/.listing.txt" >> /tmp/log.txt
            ls -t "$corrpath"/*.{jpg,JPG} "$corrpath"/{jpegs,done,DCIM,work,parts}/*.{jpg,JPG} > "$corrpath/.listing.txt"
            perl -pi.bak -e "s@^$basepath@\.@" "$corrpath/.listing.txt"
            chmod a+rw "$corrpath/.listing.txt"
            shift # past argument
        ;;

        -u|--update-listing)

            if [[ "$corrpath" -ot "$corrpath"/.listing.txt ]]; then

                echo "`date` $basepath $corrpath/.listing.txt" >> /tmp/log.txt

                cat $corrpath/.listing.txt | sort > $corrpath/.listing.sort1.txt
                ls -t "$corrpath"/*.{jpg,JPG} "$corrpath"/{jpegs,done,DCIM,work,parts}/*.{jpg,JPG} | sort > "$corrpath/.listing.sort2.txt"

                perl -pi.bak -e "s@^$basepath@\.@" "$corrpath/.listing.sort1.txt"
                perl -pi.bak -e "s@^$basepath@\.@" "$corrpath/.listing.sort2.txt"

                grep -Fxv -f $corrpath/.listing.sort1.txt $corrpath/.listing.sort2.txt > $corrpath/.listing.diff1.txt
                grep -Fxv -f $corrpath/.listing.sort2.txt $corrpath/.listing.sort1.txt > $corrpath/.listing.diff2.txt

                cat $corrpath/.listing.diff1.txt $corrpath/.listing.txt > $corrpath/.listing2.txt
                mv $corrpath/.listing2.txt $corrpath/.listing.txt
                grep -v -f $corrpath/.listing.diff2.txt $corrpath/.listing.txt > .listing2.txt
                mv $corrpath/.listing2.txt $corrpath/.listing.txt
                #rm $corrpath/.listing.sort* $corrpath/.listing.diff*
                chmod a+rw "$corrpath/.listing.*"

            fi

            shift # past argument
        ;;

        -h|--help)
            echo "No help yet, sorry";
        ;;
        --default|-h|--help)
        ;;
        *)
        ;;
    esac

    shift # past argument or value

done
