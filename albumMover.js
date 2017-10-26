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
    var settings;
    var mapFun;
    var sortFun;
    var threshold;
};

mover.prototype = {

  navigate: function( idx, evt ) {
    this.move( idx, evt );
  },
  select: function( idx, evt ) {
    this.set( idx, evt );
  },
  setFunction: function( fnc ) {
    this.setByFunctor( fnc );
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
  },
  setByFunctor: function( fnc ) {
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
    setByFunctor: function( fnc ) 
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

    this.mapFun = function( obj, x, i ) 
        { 
            var entry = {
                html: document.getElementById( 'div_'     + ( i + 1 ) ).innerHTML,
                keys: document.getElementById( 'keywords' + ( i + 1 ) ).innerHTML,
                datetime: document.getElementById( 'datetime' + ( i + 1 ) ).innerHTML,
                sortkey: document.getElementById( 'datetime' + ( i + 1 ) ).innerHTML,
                selected: ( obj.settings[ i ] == 1 ? true : false ),
                oldindex: i,
                newindex: i
            };

            return entry;
        }.bind( null, this );

    this.sortFun = function( obj, a, b ) 
        { 
            if ( !a.selected &&  b.selected ) 
                return b.newindex <  obj.threshold ?  1 : -1;
            if (  a.selected && !b.selected ) 
                return b.newindex >= obj.threshold ? -1 :  1;

            return 0;
        }.bind( null, this );

    //$( this ).bind( "yell", function(){
        //alert("In");
    //});
};

albumMover.prototype = 
{
    ctrlmove: function( idx )
    {
        var count = this.settings.length;

        function selection( a, b )
        {
            if ( !a.selected &&  b.selected ) 
                return 1;
            if (  a.selected && !b.selected ) 
                return -1;
            return 0;
        }

        var selcount = 0;

        var obj = this;

        this.content = Array.apply( null, Array( count ) ).map( this.mapFun );

        this.content.sort( selection );

        for ( i = 0; i < count; i++ ) {

            selcount += this.content[ i ].selected ? 1 : 0;
            this.content[ i ].newindex = i;
        }

        this.threshold = idx + selcount - 1;

        this.content.sort( this.sortFun );

        for ( i = 0; i < count; i++ ) {

            this.settings[ i ] = this.content[ i ].selected ? 1 : 0;

            var oldIndex = this.content[ i ].oldindex;

            if ( i != oldIndex ) {

                var str = this.content[ i ].html;
                str = str.replace( /((file-number|dir-number|piclink|picture|art_keywords|header)_)[0-9]+/g, "$1" + ( i + 1 ) );
                document.getElementById( 'div_' + ( i + 1 ) ).innerHTML = str;

                var str = this.content[ i ].keys;
                document.getElementById( 'keywords' + ( i + 1 ) ).innerHTML = str;

                str = this.content[ i ].datetime;
                document.getElementById( 'datetime' + ( i + 1 ) ).innerHTML = str;

                $( "#picture_" + ( i + 1 ) ).attr("style", 
                    "border:2px solid " 
                  + ( ( this.settings[ i ] ) == 0 ? "white;" : "green;" )
                    );

                //if ( this.content[ i ].selected ) {

                    $.ajax({
                        method: 'POST',
                        url: 'newlist.php',
                        data: 
                        {
                            path:     this.picdir,
                            moveFrom: oldIndex,
                            moveTo:   i
                        }
                    });
                //}
            }
        }
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

            if ( idx != index ) {

                index = idx;

                $( '#picture_' + index ).goTo();
                $( '#piclink_' + index ).focus();

                this.navigate( index, evt );
            }

            if ( evt.ctrlKey ) {
                $(window).trigger('resize');
            }

            evt.preventDefault();
        }
    },
    set: function( idx, evt ) 
    {
        if ( idx > 0 && idx <= count ) {

            index = idx;

            if ( 0 == this.settings[ index - 1 ] ) {

                this.settings[ index - 1 ] = 1;
                this.navigate( index, evt );
            }
            else
                this.settings[ index - 1 ] = 0;
        }
    },
    setByFunctor: function( fnc ) 
    {
        try {

            var count = this.settings.length;

            this.content = Array.apply( null, Array( count ) ).map( fnc );

            for ( i = 0; i < count; i++ ) {

                this.settings[ i ] = ( this.content[ i ].selected == true ) ? 1 : 0;

                $( "#picture_" + i ).attr("style", 
                    "border:2px solid " 
                  + ( ( this.settings[ i ] ) == 0 ? "white;" : "green;" )
                    );
            }

            for ( i = 0; i < count; i++ ) {

                if ( this.content[ i ].selected == true ) {

                    this.navigate( i + 1, null );
                    break;
                }
            }
        }
        catch ( err ) {
            console.log( err.message );
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
