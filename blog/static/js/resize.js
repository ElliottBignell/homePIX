var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)

$( window ).on( "resize", function() {                                         

    var count = $('img[id^=picture]').length;
    var index = 1;

    resizeGroups( "#picture_" + count );
});

window.addEventListener('load',   prepareResize, false);        

var widths  = [];
var heights = [];
var rows    = [];
var rowIds  = [];

$("img").on("load", function() {

    widths[  this.id ] = $(this).width();
    heights[ this.id ] = $(this).height();

    resizeGroups( this.id );

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

function resizeGroups( id ) 
{                                         
    var prefix = id.replace( /_[0-9]*/, "" );
    var elems  = id.replace( /.*_/, "" );
    var index = ( elems - 1 + 1 );

    if ( 0 == index )
        return;

    var begin = 1;
    var end = 0;
    var pic       = $( prefix + "_" + begin );
    var screenWidth  = document.documentElement.clientWidth;
    var screenHeight = document.documentElement.clientHeight;
    var padding = 6;
    var defaultHeight = screenHeight / 2;

    $('[id^=keywords]').each( 
        function() { 

            var keywords =  $( this ).html().replace( /,/g, "<br>" );
            var arttag = "#" + this.id.replace( /keywords/, "art_keywords_" );
            $( arttag ).html( keywords );
            
            var titletag  = "#" + this.id.replace( /keywords/, "title"   );
            var headertag = "#" + this.id.replace( /keywords/, "header_" );
            var title =  $( titletag ).html();
            $( headertag ).html( title );
        } );

    while ( end <= elems ) {

        //try {

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

                begin = oldbegin;

                var elemWidth  = widths[  key ];
                var elemHeight = heights[ key ];
                var newWidth = groupWidth + elemWidth;

                //if ( newWidth > screenWidth ) {

                    var proportion = ( groupWidth + padding ) / screenWidth;
                    var newheight = Math.round( defaultHeight / ( proportion != 0 ? proportion : 1 ) );

                    if ( newheight > ( defaultHeight ) ) {
                        newheight = defaultHeight;
                    }

                    rows[ groupno ] = { 
                        'index': groupno,
                        'count': 0,
                        'begin': begin,
                        'end': begin - 1,
                        'newheight': newheight
                    };

                    resizeGroup( prefix, rows[ groupno ] );
                //}

                begin = rows[ groupno++ ].end; 
                groupWidth = padding;
            }
        //}
        //catch (err) {
            //console.log( err );
        //}
    }
}

function resizeGroup( prefix, group )
{
    do {

        var begin = group.begin;

        var key = prefix + '_' + begin;

        if ( heights[ key ] != 0 ) {

            var aspect = widths[ key ] / heights[ key ];

            //try {

                var thisid =  prefix + "_" + begin ;
                var height = group.newheight / 2;

                $( thisid ).removeAttr( "height" );
                $( thisid ).removeAttr( "width" );

                $( thisid ).attr( "height",  height          );
                $( thisid ).attr( "width",   height * aspect );
                $( thisid ).attr( "groupno", group.index     );

                $( "#header_" + begin ).width( height - 6 );

                rows[ group.index ].count++;
                rowIds[ begin ] = group.index;
            //}
            //catch (err) {
                //console.log( err );
            //}
        }
        else
            console.log( "Skipping " + key + "\n" );

    } while ( ++begin < group.end );
}
