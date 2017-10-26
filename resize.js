var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)

$( window ).on( "resize", function() {                                         

    var elems = $('[id^=picture_]' ).length;
    $( "#picture_" + elems ).trigger( "load" );
});

window.addEventListener('load',   prepareResize, false);        

var widths  = [];
var heights = [];
var rows    = [];
var rowIds  = [];
var defaultHeight = 200;

$("img").one("load", function() {

    widths[  this.id ] = $(this).width();
    heights[ this.id ] = $(this).height();

    resizeGroups( this );

}).each(function() {
  if(this.complete) $(this).load();
});
 
function prepareResize(evt) 
{                                         
    prepareGroups();
}

function prepareGroups( prefix ) 
{                                         
    $('.lazyload').each(

        function() {

            widths[  this.id ] = $( this ).width();
            heights[ this.id ] = $( this ).height();
        }
   );
}

function resizeGroups( obj ) 
{                                         
    var id = obj.id;

    var prefix = id.replace( /_[0-9]*/, "" );
    var elems  = id.replace( /.*_/, "" );
    var index = ( elems - 1 + 1 );
    var keywords = $( "#keywords" + index ).html();
    var text     = $( "#title"    + index ).html();

    if ( "" != text ) {
        $( "#header_"       + index ).html( "<h1>" + text + "</h1>" );
    }

    if ( "" != keywords ) {
        $( "#art_keywords_" + index ).html( keywords.replace( /,/g, "<br>" ) );
    }

    //var elems = $('[id^=' + prefix + ']' ).length;

    if ( 0 == elems )
        return;

    var begin = 1;
    var end = 0;
    var pic       = $( "#" + prefix + "_" + begin );
    var screenWidth = document.documentElement.clientWidth;
    var padding = 6;

    while ( end <= elems ) {

        try {

            var groupno = 1;
            var groupWidth = padding;

            while ( ++end <= elems && groupWidth <= screenWidth ) {

                var oldbegin = begin;
                var key = prefix + '_' + end;
                var newGroupWidth = groupWidth;

                do {

                    key = prefix + '_' + begin;

                    if ( heights[ key ] != 0 ) {

                        var aspect = widths[ key ] / heights[ key ];
                        var elemWidth = defaultHeight * aspect;
                        newGroupWidth = groupWidth + elemWidth + padding;

                        if ( newGroupWidth <= screenWidth ) {
                            groupWidth = newGroupWidth;
                        }
                    }

                } while ( ++begin <= elems && newGroupWidth <= screenWidth );

                var groupEnd = begin - 1;
                begin = oldbegin;

                var elemWidth  = widths[  key ];
                var elemHeight = heights[ key ];
                var newWidth = groupWidth + elemWidth;

                //if ( newWidth > screenWidth ) {

                    var proportion = ( groupWidth + padding ) / screenWidth;
                    var newheight = Math.round( defaultHeight / ( proportion != 0 ? proportion : 1 ) );

                    if ( newheight > ( defaultHeight * 2 ) ) {
                        newheight = defaultHeight * 2;
                    }

                    rows[ groupno ] = { 
                        'count': 0,
                        'begin': 0,
                        'end': 0
                    };

                    rows[ groupno ].begin = begin;
                    rows[ groupno ].end   = groupEnd;

                    do {

                        key = prefix + '_' + begin;

                        if ( heights[ key ] != 0 ) {

                            var aspect = widths[ key ] / heights[ key ];

                            try {

                                var thisid =  "#" + prefix + "_" + begin ;

                                $( thisid ).removeAttr( "height" );
                                $( thisid ).removeAttr( "width" );

                                $( thisid ).attr( "height",  newheight          );
                                $( thisid ).attr( "width",   newheight * aspect );
                                $( thisid ).attr( "groupno", groupno            );

                                rows[ groupno ].count++;
                                rowIds[ begin ] = groupno;
                            }
                            catch (err) {
                                console.log( err );
                            }
                        }
                        else
                            console.log( "Skipping " + key + "\n" );

                    } while ( ++begin < groupEnd );

                    groupno++;
                //}

                begin = groupEnd; 
                groupWidth = padding;
            }
        }
        catch (err) {
            console.log( err );
        }
    }
}
