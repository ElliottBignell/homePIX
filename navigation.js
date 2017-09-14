var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)
var index;
var count;
var  file = getQueryVariable( "file"  );
var   dir = getQueryVariable( "dir"   );

document.addEventListener( "touchstart", handleTouchStart, false);        
document.addEventListener( "touchmove",  handleTouchMove,  false);
document.addEventListener( "keydown",    doKeyDown,        false )
//document.addEventListener( "keyup",      doKeyUp,          false );
  window.addEventListener( "keypress",   doKeyPress,       false );

$( "#find" ).keydown( function( e ) {

    var code = (e.keyCode ? e.keyCode : e.which);

    switch ( code ) {
    case 13: //Return
        imgnav.navigate( 5, null );
        break;
    case 17: //Ctrl
    case 37: //Left-arrow
    case 39: //Right-arrow
        break;
    default:
        //alert( e.keyCode + " " + e.which );
    }
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
            advance();
        } 
        else {
            retreate();
        }                       
    } 
    else {
    
        if ( yDiff > 0 ) {
            /* up swipe */ 
        } 
        else { 
            /* down swipe */
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
            imgnav.navigate( count, evtobj );
            break;
        case 36: //Home
            imgnav.navigate( 1, evtobj );
            break;

        case 32: //Spacebar

            //if ( e.target == document.body ) {

                $( '#picture_' + index ).goTo();
                imgnav.select( index, evtobj );
                e.preventDefault();
            //}

            break;

        case 39:
        case 'w':
            advance( evtobj );
            break;
        case 37:
        case 'b':
            retreat( evtobj );
            break;
        case 'G':
            break;
        default:
            //alert( e.which );
        } 
    }
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
    swipe_det.sX = 0; swipe_det.sY = 0; swipe_det.eX = 0; swipe_det.eY = 0;
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
    ele.addEventListener('touchend',function(e){
            //horizontal detection
            if ((((swipe_det.eX - min_x > swipe_det.sX) || (swipe_det.eX + min_x < swipe_det.sX)) && ((swipe_det.eY < swipe_det.sY + max_y) && (swipe_det.sY > swipe_det.eY - max_y) && (swipe_det.eX > 0)))) {
            if(swipe_det.eX > swipe_det.sX) direc = "r";
            else direc = "l";
            }
            //vertical detection
            else if ((((swipe_det.eY - min_y > swipe_det.sY) || (swipe_det.eY + min_y < swipe_det.sY)) && ((swipe_det.eX < swipe_det.sX + max_x) && (swipe_det.sX > swipe_det.eX - max_x) && (swipe_det.eY > 0)))) {
            if(swipe_det.eY > swipe_det.sY) direc = "d";
            else direc = "u";
            }

            if (direc != "") {
            if(typeof func == 'function') func(el,direc);
            }
            direc = "";
            swipe_det.sX = 0; swipe_det.sY = 0; swipe_det.eX = 0; swipe_det.eY = 0;
            },false);  
}

function myfunction(el,d) 
{
    advance();
}
