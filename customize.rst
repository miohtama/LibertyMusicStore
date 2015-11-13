Sample CSS to be dropped in through web admin.

Dark theme example
+++++++++++++++++++++

Extra HTML for the store to make it white on black::

    <link href='http://fonts.googleapis.com/css?family=Volkhov' rel='stylesheet' type='text/css'>
    <style>
        body {
           background: black;
           color: #aaa;
           margin: 20px;
        }

        h1, h3 {
           font-family: "Volkhov",serif;
        }

        .btn-default {
            background: #666;
            color: white;
        }

        /* QR code must be on the white background or BlockChain mobile wallet does not pick it up */
        .bitcoin-address-qr-container {
            padding: 40px 0;
            background: white;
        }
    </style>

Some fonts
++++++++++++

Examples::

    <link href='https://fonts.googleapis.com/css?family=Libre+Baskerville&amp;subset=latin,latin-ext' rel='stylesheet' type='text/css'>
