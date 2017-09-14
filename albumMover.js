////////////////////////////////////////////////////////////////
// Scroll plugin

(function($)
{
    $.fn.goTo = function() {

        if ( $(this).offset().top > 100) {

            $('html, body').animate({
                scrollTop: $(this).offset().top + 'px'
            }, 'fast');
        }

        return this; // for chaining...
    }
})(jQuery);


function extend(base, sub) {
  // Avoid instantiating the base class just to setup inheritance
  // Also, do a recursive merge of two prototypes, so we don't overwrite 
  // the existing prototype, but still maintain the inheritance chain
  // Thanks to @ccnokes
  var origProto = sub.prototype;
  sub.prototype = Object.create(base.prototype);
  for (var key in origProto)  {
     sub.prototype[key] = origProto[key];
  }
  // The constructor property was set wrong, let's fix it
  Object.defineProperty(sub.prototype, 'constructor', { 
    enumerable: false, 
    value: sub 
  });
}

////////////////////////////////////////////////////////////////
// Polymorphic navigator

function mover() 
{
};

mover.prototype = {
  navigate: function( idx, evt ) {
    this.move( idx, evt );
  },
  select: function( idx, evt ) {
    this.set( idx, evt );
  },
  setDirName: function( directoryName ) {
    this.setDirectory( directoryName );
  },
  ctrlmove: function( idx ) {
    // Abstract
  },
  move: function( idx, evt ) {
    // Abstract
  },
  set: function( idx, set ) {
    // Abstract
  },
  setDirectory: function( directoryName ) {
    // Abstract
  }
};

////////////////////////////////////////////////////////////////
// Navigator for image page

function fileMover()
{
    index = getQueryVariable( "index" );
    count = getQueryVariable( "count" );

    mover.call( this );
}

fileMover.prototype = {

    ctrlmove: function( idx )
    {
        alert( "Not implemented" );
    },
    move: function( idx, evt )
    {
        var imgText = document.getElementById( 'img' + idx ).innerHTML;
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
    },
    set: function( idx, evt ) 
    {
    },
    setDirectory: function( directoryName ) 
    {
    }
};

////////////////////////////////////////////////////////////////
// Navigator for album page

function albumMover( dir ) 
{
    count = $('*').filter(function () {
        return this.id.match(/picture_\d+/); //regex for the pattern "picture_ followed by a number"
    }).length;

    index = 1;
    this.settings = Array.apply( null, Array( count ) ).map( function(x, i) { return 0; } );
    this.picdir   = dir;

    // Call the parent's constructor
    mover.call(this);

    $( this ).bind( "yell", function(){
        alert("In");
    });
};

albumMover.prototype = 
{
    ctrlmove: function( idx )
    {
        var count = this.settings.length;

        newHTML = Array.apply( null, Array( count ) ).map( 
            function( x, i ) { return document.getElementById( 'div_' + ( i + 1 ) ).innerHTML; } 
        );

        oldHTML = Array.apply( null, Array( count ) ).map( 
            function( x, i ) { return document.getElementById( 'div_' + ( i + 1 ) ).innerHTML; } 
        );

        var source = 0;
        var target = 0;

        while ( target < idx - 1 && source < count ) {

            if ( this.settings[ source ] == 0 ) {

                newHTML[ target ] = oldHTML[ source ];
                this.settings[ target++ ] = 0;
                console.log( "first: " + idx + " " + (target-1) + " " + this.settings[ target - 1 ] );
            }

            source++;
        }

        var oldsource = target;
        source = 0;

        while ( source < count ) {

            if ( this.settings[ source ] == 1 ) {

                newHTML[ target ] = oldHTML[ source ];
                this.settings[ target++ ] = 1;
                console.log( "second: " + idx + " " + (target-1) + " " + this.settings[ target - 1 ] );
            }

            source++;
        }

        source = oldsource;

        while ( source < count ) {

            if ( this.settings[ source ] == 0 ) {

                newHTML[ target ] = oldHTML[ source ];
                this.settings[ target++ ] = 0;
                console.log( "third: " + idx + " " + target + " " + this.settings[ target ] );
            }
                
            source++;
        }

//
//            if ( 0 != this.settings[ source ] ) {
//
//                var strA = document.getElementById( 'div_' + source ).innerHTML;
//                var strB = document.getElementById( 'div_' + target ).innerHTML;
//
//                strA = strA.replace( /((dir-number|piclink|picture)_)[0-9]+/g, "$1" + target );
//                strB = strB.replace( /((dir-number|piclink|picture)_)[0-9]+/g, "$1" + source );
//
//                document.getElementById( 'div_' + source ).innerHTML = strB;
//                document.getElementById( 'div_' + target ).innerHTML = strA;
//
//                target++;
//                cnt++;
//            }

        for ( i = 0; i < count; i++ ) {

            var str = newHTML[ i ];
            str = str.replace( /((dir-number|piclink|picture)_)[0-9]+/g, "$1" + ( i + 1 ) );
            document.getElementById( 'div_' + ( i + 1 ) ).innerHTML = str;
        }
            //$( "div_" + index ).load( self );
            //$( "div_" + idx   ).load( self );
    },
    move: function( idx, evt )
    {
        if ( idx > 0 && idx <= count ) {

            if ( evt.ctrlKey ) {
                this.ctrlmove( idx );    
            }

            var oldIndex = index;
            var newIndex = idx;

            $( "#picture_" + oldIndex ).attr("style", 
                "border:2px solid " 
              + ( ( this.settings[ oldIndex - 1 ] ) == 0 ? "white;" : "green;" )
                );
            $( "#picture_" + newIndex ).attr("style", 
                "border:2px solid " 
              + ( ( this.settings[ newIndex - 1 ] ) == 0 ? "red;" : "blue;" )
                );

            index = idx;

            if ( idx != index ) {

                $( '#picture_' + index ).goTo();
                $( '#piclink_' + index ).focus();

                if ( evt.ctrlKey ) {
                    
                    $.ajax({
                      method: 'POST',
                      url: 'newlist.php',
                      data: {path:this.picdir,moveFrom:oldIndex + 1,moveTo:newIndex + 1}
                    });
                }

                this.navigate( index, evt );
            }
        }
    },
    set: function( idx, evt ) 
    {
        if ( idx > 0 && idx <= count ) {

            index = idx;

            this.settings[ index - 1 ] = 1;
            this.navigate( index, evt );
        }
    },
    setDirectory: function( directoryName ) 
    {
    }
};

// Setup the prototype chain the right way
extend( mover, fileMover  );
extend( mover, albumMover );

// Here is where the albumMover (and mover) constructors are called
var imgnav;
