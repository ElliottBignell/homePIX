function fileMover()
{
    alert( "fileMover" );
    index = getQueryVariable( "index" );
    count = getQueryVariable( "count" );

    mover.call( this );
}

fileMover.prototype = new mover();

fileMover.prototype.select = function( idx )
{
};

fileMover.prototype.navigate = function( idx )
{
    alert( "navigate" );
    var imgText = document.getElementById( 'img'   + idx ).innerHTML;
    var lowText = document.getElementById( 'low' + idx ).innerHTML;

    var keyWords = document.getElementById( 'keywords' + idx).innerHTML.replace( /,/g, ", " );

    $( "#title"   ).attr("innerHTML", document.getElementById( 'title' + idx ).innerHTML );
    //$( "#title"   ).attr("innerHTML", imgText.replace( /(.*)[\/]([^\/]*)(\.jpg)/, '$2<br>' ) );
    $( "#filename").attr("innerHTML", imgText + '<br>' );

    $( "#main"    ).attr("data-src",imgText );
    $( "#main"    ).attr("alt",     imgText );
    $( "#main"    ).attr("src",     imgText );
    $( "#mainlink").attr("href",    imgText );
    $( "#description" ).attr( "innerHTML", "TODO<br>" );
    $( "#dimensions"  ).attr( "innerText", ( 
                                  document.getElementById( 'picWidth'  + idx ).innerHTML +
                                  " x " +
                                  document.getElementById( 'picHeight' + idx ).innerHTML
                              ).replace( /<br>/gm, "" ) + " ("
                            );
    $( "#megapixels"      ).attr( "innerHTML",        document.getElementById( 'megapixels'      + idx ).innerHTML + " MP)<br>" );
    $( "#keywords"        ).attr( "innerHTML",        keyWords                                                     + "<br>" );
    $( "#aspect"          ).attr( "innerHTML",        document.getElementById( 'aspectRatio'     + idx ).innerText + "<br>" );
    $( "#comment"         ).attr( "innerHTML",        document.getElementById( 'comment'         + idx ).innerHTML + "<br>" );
    $( "#datetime"        ).attr( "innerHTML",        document.getElementById( 'datetime'        + idx ).innerHTML + "<br>" );
    $( "#copyright"       ).attr( "innerHTML",        document.getElementById( 'copyright'       + idx ).innerHTML + "<br>" );
    $( "#camera"          ).attr( "innerHTML",        document.getElementById( 'camera'          + idx ).innerText + "<br>" );
    $( "#fnumber"         ).attr( "innerText", "f/" + document.getElementById( 'fnumber'         + idx ).innerText + " at " );
    $( "#exposure"        ).attr( "innerText",        document.getElementById( 'exposure'        + idx ).innerText + " sec on " );
    $( "#exposureprogram" ).attr( "innerText",        document.getElementById( 'exposureprogram' + idx ).innerText + " (ISO" );
    $( "#iso"             ).attr( "innerText",        document.getElementById( 'iso'             + idx ).innerText + ")" );
    $( "#flash"           ).attr( "innerHTML",        document.getElementById( 'flash'           + idx ).innerHTML + "" );
    $( "#lensid"          ).attr( "innerText",        document.getElementById( 'lensid'          + idx ).innerText + " on " );
    $( "#focusmode"       ).attr( "innerText",        document.getElementById( 'focusmode'       + idx ).innerText + " at " );
    $( "#focusdistance"   ).attr( "innerText",        document.getElementById( 'focusdistance'   + idx ).innerText + " distance" );
    $( "#focallength"     ).attr( "innerText",        document.getElementById( 'focallength'     + idx ).innerText + " (equiv. " );
    $( "#focallen35mm"    ).attr( "innerHTML",        document.getElementById( 'focallen35mm'    + idx ).innerText + ")<br>" );
    $( "#lens"            ).attr( "innerHTML",        "" );

    var rawDate = document.getElementById( 'datetime' + idx ).innerText.replace( /:/, "-" );
    rawDate = rawDate.replace( /:/, "-" );

    var now = new Date( rawDate );

    var curr_date = now.getDate();
    var curr_month = now.getMonth() + 1; //Months are zero based
    var curr_year = now.getFullYear();
    var fmtDate = "" + curr_date + "-" + curr_month + "-" + curr_year;

    $( "#datetime" ).attr( "innerHTML", fmtDate + "<br>" );

    index = idx;

    resizeImg( $( "#main" ) );
};

extend( mover, fileMover );
