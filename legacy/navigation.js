var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)
var index = 0;
var count = 0;
var  file = getQueryVariable( "file"  );
var   dir = getQueryVariable( "dir"   );
var dragObj;

document.addEventListener( "touchstart", handleTouchStart, false);        
document.addEventListener( "touchmove",  handleTouchMove,  false);
document.addEventListener( "keydown",    doKeyDown,        false )
//document.addEventListener( "keyup",      doKeyUp,          false );
  window.addEventListener( "keypress",   doKeyPress,       false );

$( ".draggable" ).draggable({
    revert: 'invalid'
});

$( ".draggable" ).on( "dragstart", function() {

    var regexp = /div_([0-9]*)/;
    var thismatch = regexp.exec(this.id);

    imgnav.setFunction( function( x, i ) 
        {
            var entry = {
                html: this.innerHTML,
                selected: ( i - 1 == thismatch[ 1 ] ) ? true : false,
                oldindex: i - 1,
                newindex: i - 1
            };

            return entry;
        }
    );

    dragObj = this.id;
});

$( ".droppable" ).droppable({

  drop: function( event, ui ) {

    //$( "#" + dragObj ).insertBefore( "#" + this.id );
    $( "#" + dragObj ).css( {
        top: "0px", 
        left: "0px" 
    });

    var regexp = /div_([0-9]*)/;
    var match = regexp.exec(dragObj);
    var thismatch = regexp.exec(this.id);

    dispatchOp( ( match[ 1 ] - 1 ) + "," + ( match[ 1 ] - 1 ) + "@B@m" + ( thismatch[ 1 ] - 1 ) );

    return false;
  }
});

$( "#find" ).keydown( function( e ) {

    var code = (e.keyCode ? e.keyCode : e.which);

    switch ( code ) {
    case 13: //Return
    case 17: //Ctrl
    case 37: //Left-arrow
    case 39: //Right-arrow
        break;
    default:
        //alert( e.keyCode + " " + e.which );
    }
});

function togglePanel()
{
  $('#slideout').toggleClass('on');
}

$('#find').on('search', function(e) {
    e.preventDefault();
});

function dispatchOp( value )
{
    var substr = value.match( /(g|v|[0-9\^]*,[0-9$]*|[0-9]+|\%)([\W])((.*)\2)*(s|m([0-9]+)|\>|\<|[kta](\+|\-)*\=\".*\")/i );

    if ( null != substr ) {
        
        var index = 1;

        var filter    = substr[ index++ ];

        index++;

        var text      = substr[ index++ ];
        index++
        var operation = substr[ index++ ];

        var regexp = new RegExp( ".*" + text + ".*", "i" );
        var patterns = [];
        var selval = ( filter.match( /(g|v)/ ) && 'g' == filter );

        function bindLate(funcName, fixThis) { // instead of bind

            return function() {
                return fixThis[ funcName ].apply( fixThis, arguments );
            }
        }

        var selectGorV = function( i )
        {
            var keys = $( "#keywords"+ ( i + 1 ) ).html() + "," + 
                       $( "#title"   + ( i + 1 ) ).html() + "," + 
                       $( "#comment" + ( i + 1 ) ).html() + "," + 
                       $( "#header_" + ( i + 1 ) ).html();

            return ( ( "" != keys && keys.match( regexp ) ) ? selval : !selval );
        }

        var selectRange = function( range, i )
        {
            return ( ( i <= range.last && i >= range.first ) ? true : false );
        }

        var keyDate  = function(        i ) { return document.getElementById( 'datetime' + ( i + 1 ) ).innerHTML; }

        var nullRange = function( range, i ) { return 0; }
        var   nullKey = function(        i ) { return 0; }

        var rangeFun = nullRange;
        var   keyFun = nullKey;

        var vimRange = function()
        {
            imgnav.setFunction( function( x, i ) 
                {
                    var entry = {
                        html: document.getElementById( 'div_' + ( i + 1 ) ).innerHTML,
                        selected: rangeFun( i ),
                        oldindex: i + 1,
                        newindex: i + 1
                    };

                    return entry;
                }
            );
        }

        //var callback1 = function() { alert( "Invalid range in search" ); }

        var vimMove = function()
        {
            vimRange();

            var idx = 0;

            var place = substr[ index ];

            switch ( place ) {
            case '^':
                idx = 1;
                break;
            case '$':
                idx = count;
                break;
            default:
                idx = parseInt( place ) + 1;
                break;
            }

            var event = new MouseEvent('click', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'ctrlKey': true
                    });

            imgnav.navigate( idx, event );
        }

        var vimSort = function( forwards )
        {
            rangeFun = nullRange;
              keyFun = keyDate;

            vimRange();

            var one = forwards ? 1 : -1;

            imgnav.sortFun = function( obj, forth, a, b ) { 
                return (a.sortkey < b.sortkey) ? forth : ((a.sortkey > b.sortkey) ? forth : 0);
            }.bind( null, imgnav, forwards );

            var event = new MouseEvent('click', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'ctrlKey': true
                    });

            imgnav.navigate( 1, event );
        }

        var exifSet = function( word, first, last )
        {
            var keywords  = word.match( /[kta](\+|\-)*\=\"(.*)\"/ );
            var filelist  = "";
            var albumName = "";

            for ( var i = first; i <= last; i++ ) {

                var url = $( "#piclink_" + i ).attr( "href" );
                var files = url.match( /.*file=(.*)\&dir=(.*)\&index=.*/ );

                if ( null != files ) {

                    var filepath = files[ 2 ] + files[ 1 ];

                    var setTitle = function() {

                        return {
                            opcode:    0, // Flag for Title, interpreted server-side
                            path:      filepath,
                            title:     keywords[ 3 ],
                            index:     i
                        };
                    };

                    var setKeywords = function( op ) {

                        return {
                            opcode:    op, // Flag for Keywords, interpreted server-side
                            path:      filepath,
                            keyword:   keywords[ 3 ],
                            index:     i
                        };
                    };

                    var setAlbum = function() {

                        return {
                            files:   filelist,
                            album:   albumName
                        };
                    };

                    var retTitle = function( result ) {

                        var items = result.match( /(.*)\t(.*)/ );

                        if ( null != items ) {
                            $( "#header_" + items[ 1 ] ).html( "<h1>" + items[ 2 ] + "</h1>" ); 
                        }
                    };

                    var retKeywords = function( result ) {

                        var items = result.match( /(.*)\t(.*)/ );

                        if ( null != items ) {

                            $( "#keywords"      + items[ 1 ] ).html( items[ 2 ] ); 
                            $( "#art_keywords_" + items[ 1 ] ).text( items[ 2 ] ); 
                        }
                    };

                    var retAlbum = function( result ) {
                    };

                    var dataFn = setTitle;
                    var  retFn = retTitle;
                    var serverPHP = "keywords.php";

                    switch ( true ) {
                    case  /k\=\"(.*)\"/.test( keywords ):
                        dataFn = setKeywords.bind( null, 1 );
                        retFn  = retKeywords;
                        break;
                    case  /k\+\=\"(.*)\"/.test( keywords ):
                        dataFn = setKeywords.bind( null, 2 );
                        retFn  = retKeywords;
                        break;
                    case  /k\-\=\"(.*)\"/.test( keywords ):
                        dataFn = setKeywords.bind( null, 3 );
                        retFn  = retKeywords;
                        break;
                    case  /a\+\=\"(.*)\"/.test( keywords ):
                        filelist += ( ( "" != filelist ) ? ";" : "" ) + filepath;
                        albumName = keywords[2];
                        continue;
                        break;
                    default:
                        break;
                    }

                    $.ajax({
                        url: serverPHP,
                        data: dataFn(),
                        success: retFn
                    });
                }
            }

            switch ( true ) {
            case  /a\+\=\"(.*)\"/.test( keywords ):

                serverPHP = 'newalbum.php';
                dataFn = setAlbum.bind( null );
                retFn  = retAlbum;

                $.ajax({
                    url: serverPHP,
                    data: dataFn(),
                    success: retFn
                });
                break;

            default:
                break;
            }
        }

        var firstN = -1;
        var  lastN = -1;

        switch ( true ) {
        case /(g|v)/.test( filter ):
            rangeFun = selectGorV;
            break;
        case /[0-9\^]*,[0-9$]*/.test( filter ):
            var indices = filter.match( /([0-9\^]*)(,([0-9$]*)*)/i );
            firstN = ( null == indices[ 1 ] || '^' == indices[ 1 ] ) ?     1 : Number( indices[ 1 ] );
            lastN  = ( null == indices[ 3 ] || '^' == indices[ 3 ] ) ? count : Number( indices[ 3 ] );
            rangeFun = selectRange.bind( null, { current: -1, first: firstN, last: lastN } );
            break;
        case /^[0-9]+$/.test( filter ):
            firstN = filter + 1;
            lastN  = filter + 1;
            rangeFun = selectRange.bind( null, { current: -1, first: firstN, last: lastN } );
            break;
        case /\%/.test( filter ):
            firstN = 1;
            lastN  = count + 1;
            rangeFun = selectRange.bind( null, { current: -1, first: firstN, last: lastN } );
            break;
        default:
            console.log( "Invalid pattern in search submit" );
            break;
        }

        patterns.push( { 'pattern':new RegExp(/s/),               'callback': vimRange } );
        patterns.push( { 'pattern':new RegExp(/m([0-9]+|\$|\^)/), 'callback': vimMove  } );
        patterns.push( { 'pattern':new RegExp(/\<|\>/),           'callback': vimSort.bind( null, operation == '>' ? true : false ) } );
        patterns.push( { 'pattern':new RegExp(/\=\".*\"/),        'callback': exifSet.bind( null, operation, firstN, lastN ) } );

        for ( var i=0; i<patterns.length; i++ ) {

            if ( patterns[ i ].pattern.test( operation ) ){
                patterns[ i ].callback();
            }
        }
    }
    else {

        var retSearch = 

        $.ajax({
            url: 'search.php',
            data: { search:value },
            success: function( result ) {
                    window.location.href = "index.php?dir=/pics&file=" + result;
                }
            });
    }
}

$('#multisearch').submit(function( e ) {

    dispatchOp( $('#find').val() );
    e.preventDefault();
});

var xDown = null;                                                        
////////////////////////////////////////////////////////////////
function handleTouchStart(evt) 
{                                         
    xDown = evt.touches[0].clientX;                                      
    yDown = evt.touches[0].clientY;                                      
};                                                

function handleTouchMove(evt) 
{
    if ( ! xDown || ! yDown ) {
        return;
    }

    var xUp = evt.touches[0].clientX;                                    
    var yUp = evt.touches[0].clientY;

    var xDiff = xDown - xUp;
    var yDiff = yDown - yUp;

    if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/

        if ( xDiff > 0 ) {
            //advance();
        } 
        else {
            //retreat();
        }                       
    } 
    else {
    
        if ( yDiff > 0 ) {
            //advance();
        } 
        else { 
            //retreat();
        }                                                                 
    }

    /* reset values */
    xDown = null;
    yDown = null;                                             
};

function resizeImg( img ) 
{
    stylestr = "display:block;margin-left:auto;margin-right:auto;border:0px;ipadding:0px;object-fit:contain";

    $( "#main" ).attr("style",   stylestr );
    $( "#main" ).load( self );

    var width  = $( window ).width() - 200;
    var height = $( window ).height() - 50;

    var aspectRatio =     width / height;
    var imgRatio    = $( "#aspectRatio" + index ).attr( "innerHTML" );

    if ( aspectRatio < imgRatio ) {
        
        $( "#main" ).attr("width", width );
        $( "#main" ).attr("height", width / imgRatio < height ? height : width / imgRatio );
    }
    else {

        $( "#main" ).attr("width", height * imgRatio );
        $( "#main" ).attr("height", height );
    }

    $( "#main" ).attr("style",   stylestr );
    $( "#main" ).load( self );
    $( "#sidebar" ).attr( "width", 200 );

    $( "#maintab" ).load( self );
    $( "#title" ).load( self );
}

function doKeyUp(e)
{
}

function doKeyDown(e)
{
}

function doSubmit()
{
    //alert( $( "find" ).attr( "innerText" ) );
}


function doKeyPress(e)
{
    var code = (e.keyCode ? e.keyCode : e.which);
    var evtobj = window.event? event : e;

    if ( e.target == document.body ||
       ( e.target. nodeType == 1 && e.target.tagName == 'A' )
       ) 
    {
        switch ( code ) {
        case 13: //Return
            event.preventDefault();
            //document.getElementById( 'piclink_' + index ).click();
            break;
        case 35: //End
            imgnav.navigate( count, e );
            break;
        case 36: //Home
            imgnav.navigate( 1, e );
            break;

        case 32: //Spacebar

            //if ( e.target == document.body ) {

                $( '#picture_' + index ).goTo();
                imgnav.select( index, e );
                e.preventDefault();
            //}

            break;

        case 38:
        case 'k':
            retreatY( e );
            break;
        case 40:
        case 'j':
            advanceY( e );
            break;
        case 39:
        case 'w':
            advance( e );
            break;
        case 37:
        case 'b':
            retreat( e );
            break;
        case 'G':
            break;

        case 'F': // F
        case 'f': // f

            if ( e ) {

                e.preventDefault();
                $( "#find" ).focus();
            }
            break;

        case 114: // F3
            e.preventDefault();
            $( "#find" ).focus();
            break;

        default:
            //alert( e.which );
        } 
    }
}

function advanceY( evtobj ) 
{ 
    imgnav.navigate( 
        parseInt( index ) 
      + parseInt( rows[ rowIds[ index ] ].count ) 
      % parseInt( count ), evtobj 
    ); 
}

function retreatY( evtobj ) 
{ 
    imgnav.navigate( 
        parseInt( index ) 
      - parseInt( rows[ rowIds[ rows[ rowIds[ index ] ].begin - 1 ] ].count ) 
      % parseInt( count ), evtobj 
    ); 
}

function advance( evtobj ) { imgnav.navigate( parseInt( index ) + parseInt( 1 ) % parseInt( count ), evtobj ); }
function retreat( evtobj ) { imgnav.navigate( parseInt( index ) - parseInt( 1 ) % parseInt( count ), evtobj ); }

function panel1() { panelSwitch( 1 ); }
function panel2() { panelSwitch( 2 ); }

function panelSwitch( idx )
{
    $( "#panel1" ).attr( "style", "display:" + (( idx == 2) ? "inline" : "none" ) + ";" );
    $( "#panel2" ).attr( "style", "display:" + (( idx == 1) ? "inline" : "none" ) + ";" );
}

function getQueryVariable(variable)
{
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if(pair[0] == variable){return pair[1];}
    }
    return(false);
}

function detectswipe(el,func) 
{
    swipe_det = new Object();

    swipe_det.sX = 0; 
    swipe_det.sY = 0; 
    swipe_det.eX = 0; 
    swipe_det.eY = 0;

    var min_x = 30;  //min x swipe for horizontal swipe
    var max_x = 30;  //max x difference for vertical swipe
    var min_y = 50;  //min y swipe for vertical swipe
    var max_y = 60;  //max y difference for horizontal swipe
    var direc = "";

    ele = document.getElementById(el);

    ele.addEventListener('touchstart',function(e){
            var t = e.touches[0];
            swipe_det.sX = t.screenX; 
            swipe_det.sY = t.screenY;
        },false);

    ele.addEventListener('touchmove',function(e){
            e.preventDefault();
            var t = e.touches[0];
            swipe_det.eX = t.screenX; 
            swipe_det.eY = t.screenY;    
        },false);

    ele.addEventListener('touchend',function(e) {

            if ((((swipe_det.eX - min_x > swipe_det.sX) || 
                  (swipe_det.eX + min_x < swipe_det.sX) ) && 
                 ((swipe_det.eY < swipe_det.sY + max_y) && 
                  (swipe_det.sY > swipe_det.eY - max_y) && 
                  (swipe_det.eX > 0))
            )) {

                //horizontal detection
                if(swipe_det.eX > swipe_det.sX) 
                    retreat();
                else 
                    advance();
            }
            else if ((((swipe_det.eY - min_y > swipe_det.sY) || 
                       (swipe_det.eY + min_y < swipe_det.sY)) && 
                      ((swipe_det.eX < swipe_det.sX + max_x) && 
                       (swipe_det.sX > swipe_det.eX - max_x) && 
                       (swipe_det.eY > 0))
            )) {

                //vertical detection
                if(swipe_det.eY > swipe_det.sY) 
                    advance();
                else 
                    retreat();
            }

            if (direc != "") {
                if(typeof func == 'function') 
                    func(el,direc);
            }
            direc = "";
            swipe_det.sX = 0; swipe_det.sY = 0; swipe_det.eX = 0; swipe_det.eY = 0;
        },false);  
}

function myfunction(el,d) 
{
    switch ( d ) {
    case "r":
        advance();
        break;
    case "l":
        retreat();
        break;
    }
}
