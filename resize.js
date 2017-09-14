var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)

window.addEventListener('resize', handleResize,  false);        
window.addEventListener('load',   prepareResize, false);        

var widths  = [];
var heights = [];

$("img").one("load", function() {

    widths[  this.id ] = $(this).width();
    heights[ this.id ] = $(this).height();

    resizeGroups( this );

}).each(function() {
  if(this.complete) $(this).load();
});
 
function handleResize(evt) 
{                                         
    var elems = $('[id^=picture_]' ).length;

    resizeGroups( $( "#picture_" + elems ) );
}

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
    var prefix = obj.id.replace( /_[0-9]*/, "" );
    var elems  = obj.id.replace( /.*_/, "" );

    //var elems = $('[id^=' + prefix + ']' ).length;

    if ( 0 == elems )
        return;

    var begin = 1;
    var end = 0;
    var pic       = $( "#" + prefix + "_" + begin );
    var groupWidth = 0;
    var screenWidth = document.documentElement.clientWidth;
    var padding = 6;

    while ( end <= elems ) {

        try {

            while ( ++end <= elems && groupWidth <= screenWidth ) {

                var key = prefix + '_' + end;

                if ( 200 != heights[ key ] ) {

                    widths[  key ] = $( "#" + key ).width();
                    heights[ key ] = $( "#" + key ).height();
                }

                var elemWidth  = widths[  key ];
                var elemHeight = heights[ key ];
                var newWidth = groupWidth + elemWidth;

                if ( newWidth > screenWidth ) {

                    var proportion = ( groupWidth + padding ) / screenWidth;
                    var newheight = Math.round( 200.0 / ( proportion != 0 ? proportion : 1 ) );

                    do {

                        key = prefix + '_' + begin;

                        if ( 200 != heights[ key ] ) {

                            widths[  key ] = $( "#" + key ).width();
                            heights[ key ] = $( "#" + key ).height();
                        }

                        if ( heights[ key ] != 0 ) {

                            var aspect = widths[ key ] / heights[ key ];

                            try {

                                var id =  "#" + prefix + "_" + begin ;

                                $( id ).removeAttr( "height" );
                                $( id ).removeAttr( "width" );
                                $( id ).attr( "height",  newheight          );
                                $( id ).attr( "width",   newheight * aspect );
                            }
                            catch (err) {
                                console.log( err );
                            }
                        }
                    } while ( ++begin < end );

                    groupWidth = elemWidth + padding;
                    elemWidth = 0;
                }
                else {
                    groupWidth += elemWidth + padding;
                }
            }
        }
        catch (err) {
            console.log( err );
        }
    }
}
