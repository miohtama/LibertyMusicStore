/**
 * Boostrap IFRAME loading
 */

{% load static %}

(function() {

    "use strict";

    function loadScript(src, onload) {
        var script = document.createElement('script');
        script.src = src;
        script.onload = function () {
            var pymParent = new pym.Parent('store-embed-iframe-wrapper', '{{ public_url }}{{ store_url }}', {});
        };
        document.head.appendChild(script);
    }

    /**
     * Initialize the embed loader.
     */
    function init() {
        var placeholder = document.getElementById("store-embed");

        var iframeContainer = document.createElement("div");
        iframeContainer.id = "store-embed-iframe-wrapper";
        placeholder.parentNode.insertBefore(iframeContainer, placeholder.nextSibling);
        placeholder.parentNode.removeChild(placeholder);

        // Handle dynamic iframe sizing with pym
        loadScript("{{ public_url }}{% static 'pym.js' %}");
    }

    if (document.readyState == "complete" || document.readyState == "loaded" || document.readyState == "interactive") {
        init();
    } else {
        document.addEventListener("DOMContentLoaded", function(event) {
            init();
        });
    }

})();