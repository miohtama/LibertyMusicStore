/* */

(function() {
    "use strict";

    // Helper for determining max element height of selected elements
    $.fn.max = function(selector) {
        return Math.max.apply(null, this.map(function(index, el) {
            return selector.apply(el);
        }).get());
    };

    /**
     * Fix box height issues caused by too long titles
     */
    function fixAlbumSplashHeights() {
        var albums = $(".splash-album");
        var currentRow = [];

        // ßconsole.log("Found albums:", albums);

        for(var i=0; i<albums.length; i++) {

            if(!$(albums[i]).is(":visible")) {
                continue;
            }

            currentRow.push(albums[i]);
            if(currentRow.length == 3) {

                var maxHeight = $(currentRow).max(function() {
                    return $(this).height();
                });

                // console.log("Fixing ", i, "maxHeight:", maxHeight);

                $(currentRow).height(maxHeight);

                currentRow = [];
            }
        }
    }

    window.fixAlbumSplashHeights = fixAlbumSplashHeights;

    $(window).load(function() {
        fixAlbumSplashHeights();
    });
})();
