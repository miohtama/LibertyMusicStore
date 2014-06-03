(function($) {

    "use strict";

    var paymentProgress = 0;

    var countdownStart = new Date();

    function formatTwoDigits(n) {
        return ("0" + n).slice(-2);
    }

    function formatTimeLeftShort(start, end) {
        var elapsed = end - start;
        var difference = new Date(elapsed);

        // TODO: Finish
        // Calculate total hours > 24
        var hours = 24*(difference.getDate()-1) + difference.getHours();
        return formatTwoDigits(hours) + ":" + formatTwoDigits(difference.getMinutes()) + "." + formatTwoDigits(difference.getSeconds());
    }

    /**
     * Initialize all countdown timers on the page.
     */
    function updateCountdowns() {

        // Get the current time from the server
        // Milliseconds, what a brilliant idea Brendan Eich
        var serverCountdownStart = new Date(parseInt($("meta[name='x-countdown-start']").attr("content"), 10) * 1000);

        $("[data-countdown-until]").each(function() {
            var elem = $(this);
            var until = new Date(parseInt(elem.attr("data-countdown-until"), 10) * 1000);

            // Calculate the current countdown moment
            // JavaScript Date has no + operator WTF
            var now = new Date() - countdownStart - (-serverCountdownStart);
            var format = elem.attr("data-countdown-format");


            if(now > until) {
                elem.html("<span class='countdown-passed'>passed</span>");
            } else {
                var text;

                if(format == "short") {
                    text = formatTimeLeftShort(now, until);
                } else {
                    text = moment(until).countdown(now, countdown.HOURS|countdown.MINUTES|countdown.SECONDS).toString();
                }

                elem.text(text);
            }

        });
    }

    function updatePaymentProgress() {
        paymentProgress += 0.5;
        paymentProgress = Math.min(paymentProgress, 100);
        $("#payment-progress .progress-bar").css("width", paymentProgress+"%");
    }

    /**
     * Load the library.
     */
    function initBitcoinAddresses() {
        // Basic initialization
        bitcoinaddress.init({
            // jQuery selector defining bitcon addresses on the page
            // needing the boost
            selector: ".bitcoin-address",

            // Id of the DOM template element we use to decorate the addresses.
            // This must contain placefolder .bitcoin-address
            template: "bitcoin-address-template",

            generateQREagerly: true,

            // Passed directly to QRCode.js
            // https://github.com/davidshimjs/qrcodejs
            qr : {
                width: 128,
                height: 128,
                colorDark : "#000000",
                colorLight : "#ffffff"
            }
        });
    }

    function initTooltips() {
        $(".rule-tip").tooltip();
    }

    function pollTransaction() {

        if(!window.poll) {
            return;
        }

        function repoll() {
            console.log("Starting long-poll again");
            window.setTimeout(pollTransaction, 10);
        }

        var transactionUUID = window.poll.transactionUUID;
        var url = window.poll.pollURL;
        var nextURL = window.poll.nextURL;

        var buster = Math.random();

        console.log("Transaction long poll to ", url);

        $.ajax({
            url: url,
            data: {"cache-buster": buster},
            success: function(data) {

                // 304 not modified
                if(!data) {
                    repoll();
                    return;
                }

                // We get notification related to this transaction, go forward
                console.log(data);
                data = JSON.parse(data);
                if(data.transaction_uuid == transactionUUID) {
                    window.location = nextURL;
                } else {
                    // Another transaction for this customer
                    repoll();
                }
            },
            error: function(xhr) {
                console.log(xhr);
                alert("Error communicating with the server.");
            }
        });
    }

    /**
     * On transaction wait page, have some confirmations dialogs for buttons.
     */
    function handleConfirmManualActions() {

        $(".manual-actions button").click(function(e) {

            var $this = $(this);
            var text = $this.text().trim();
            if(window.confirm('Are you sure you want to do "' + text + '"?')) {
                return true;
            } else {
                e.preventDefault();
                return false;
            }
        });
    }

    function initPrices() {
        bitcoinprices.init({

            // Where we get bitcoinaverage data
            // or null if we run headless (not in browser)
            url: "https://api.bitcoinaverage.com/ticker/all",

            // Which of bitcoinaverages value we use to present prices
            marketRateVariable: "24h_avg",

            // Which currencies are in shown to the user
            currencies: ["BTC", "USD", "EUR", "CNY"],

            // Special currency symbol artwork
            symbols: {
                "BTC": "<i class='fa fa-btc'></i>",
                "USD": "$",
                "EUR": "€"
            },

            // Which currency we show user by the default if
            // no currency is selected
            defaultCurrency: "BTC",

            // We don't have clickable price features
            // in the store
            clickablePriceSelector: ".foobar",

            // How the user is able to interact with the prices
            ux : {
                // Make everything with data-btc-price HTML attribute clickable
                clickPrices : true,

                // Build Bootstrap dropdown menu for currency switching
                menu : true
            },

            // Allows passing the explicit jQuery version to bitcoinprices.
            // This is useful if you are using modular javascript (AMD/UMD/require()),
            // but for most normal usage you don't need this
            jQuery: jQuery
        });
    }


    $(document).ready(function() {
        initPrices();
        initBitcoinAddresses();
        initTooltips();
        window.setInterval(updatePaymentProgress, 500);
        pollTransaction();
        handleConfirmManualActions();
    });

})(jQuery);
