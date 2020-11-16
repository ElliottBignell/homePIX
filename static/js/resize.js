var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)

$( window ).on( "resize", function() {

    var count = $('img[id^=picture]').length;
    var index = 1;

    resizeGroups( "#picture_" + count );
});

$( window ).on( "load", function() {

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

function resizeGroups()
{
    var begin = 1;
    var end = 0;

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

    var group_width = 0;
    var objs = [];

    var gallery_width = $( '#div_collection' ).width();
    //console.log( "Gallery width: " + gallery_width );

    $('.justified').each(

        function( i, obj ) {

            var aspectRatioAttr = $( obj ).attr( 'aspectRatio' );
            var aspectRatio   = 1.6;

            if ( aspectRatioAttr ) {
                aspectRatio = aspectRatioAttr;
            }

            var gap = 16;

            extraWidth = aspectRatio * 200;

            //console.log( obj.id + " " + pic_id );
            //console.log( "  Vals: " + Math.round( group_width ) + " " + Math.round( aspectRatio ) );
            //console.log( "  Group width: " + Math.round( group_width * 100.0 ) / 100.0 );

            if ( group_width + extraWidth > gallery_width ) {

                var row_count  = objs.length + 1;
                var total_gaps = gap * ( row_count - 1 );
                var ratio      = ( gallery_width - total_gaps )
                               / ( group_width - total_gaps );

                //console.log( "Proportionate growth: " + objs.length + " " + Math.round( ratio * 100.0 ) / 100.0 );

                var total_width = 0;

                for ( i = 0; i < row_count - 1; i++ ) {

                    var next_obj = objs[ i ];
                    var pic_id   = next_obj.id.replace( /^div/, "picture" )
                                              .replace(/(picture_[0-9]*)_.*/, '$1');
                    var pic_obj  = $( '#' + pic_id );

                    var aspectRatioAttr = $( obj.id ).attr( 'aspectRatio' );
                    var picAspectRatio = 1.6;

                    if ( aspectRatioAttr ) {
                        picAspectRatio = aspectRatioAttr;
                    }
                    else {
                        picAspectRatio = Math.round( pic_obj.width() * 100.0 / pic_obj.height() ) / 100.0;
                    }

                    var obj_width   =  Math.round( ratio * 200 * picAspectRatio );
                    var obj_height  =  Math.round( ratio * 200 );

                    total_width += obj_width;

                    //console.log( "   > " + pic_id + " " + total_width + " " + next_obj.style.width + " " + obj_width + " " + obj_height + ' ' + picAspectRatio );

                    //if ( obj_height == obj_width ) {
                    //    console.log( "EQUALITY: " + pic_id + " " + obj_width + " " + obj_height );
                    //}

                    pic_obj.height( obj_height );
                    pic_obj.width(  obj_width  );
                }

                group_width = 0;
                objs = [];
            }

            objs.push( obj );
            group_width += extraWidth + gap;
        }
    );
}

