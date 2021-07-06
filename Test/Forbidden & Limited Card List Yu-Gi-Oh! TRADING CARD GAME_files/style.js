(function () {
    "use strict";

    // フッターを埋め込む
    var embedFooter = function () {
        var html = '<div id="footer-policy"><a href="/uk/privacy.html">Privacy Policy</a><a href="/uk/cookies_privacy.html">Cookies Privacy</a><a href="/uk/terms_and_conditions.html">TERMS AND CONDITIONS OF USE</a></div>';
        document.getElementById("footer").insertAdjacentHTML('beforeend', html);
    }();

    /*\
     |*|
     |*|  :: cookies.js ::
     |*|
     |*|  A complete cookies reader/writer framework with full unicode support.
     |*|
     |*|  https://developer.mozilla.org/en-US/docs/DOM/document.cookie
     |*|
     |*|  Syntaxes:
     |*|
     |*|  * docCookies.setItem(name, value[, end[, path[, domain[, secure]]]])
     |*|  * docCookies.getItem(name)
     |*|  * docCookies.removeItem(name[, path])
     |*|  * docCookies.hasItem(name)
     |*|  * docCookies.keys()
     |*|
     \*/

    var docCookies = {
        getItem: function (sKey) {
            if (!sKey || !this.hasItem(sKey)) {
                return null;
            }
            return unescape(document.cookie.replace(new RegExp("(?:^|.*;\\s*)" + escape(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=\\s*((?:[^;](?!;))*[^;]?).*"), "$1"));
        },
        setItem: function (sKey, sValue, vEnd, sPath, sDomain, bSecure) {
            if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) {
                return;
            }
            var sExpires = "";
            if (vEnd) {
                switch (vEnd.constructor) {
                    case Number:
                        sExpires = vEnd === Infinity ? "; expires=Tue, 19 Jan 2038 03:14:07 GMT" : "; max-age=" + vEnd;
                        break;
                    case String:
                        sExpires = "; expires=" + vEnd;
                        break;
                    case Date:
                        sExpires = "; expires=" + vEnd.toGMTString();
                        break;
                }
            }
            document.cookie = escape(sKey) + "=" + escape(sValue) + sExpires + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "") + (bSecure ? "; secure" : "");
        },
        removeItem: function (sKey, sPath) {
            if (!sKey || !this.hasItem(sKey)) {
                return;
            }
            document.cookie = escape(sKey) + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" + (sPath ? "; path=" + sPath : "");
        },
        hasItem: function (sKey) {
            return (new RegExp("(?:^|;\\s*)" + escape(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=")).test(document.cookie);
        },
        keys: /* optional method: you can safely remove it! */ function () {
            var aKeys = document.cookie.replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g, "").split(/\s*(?:\=[^;]*)?;\s*/);
            for (var nIdx = 0; nIdx < aKeys.length; nIdx++) {
                aKeys[nIdx] = unescape(aKeys[nIdx]);
            }
            return aKeys;
        }
    };

    // Cookieがセットされていたら終了
    var COOKIE_NAME = 'accept_cookie_policy';
    if (docCookies.getItem(COOKIE_NAME)) return false;

    var _body = document.body,
        _confirm_cookie = null,
        addClass = function (el, class_name) {
            el.classList.add(class_name);
        },
        removeClass = function (el, class_name) {
            el.classList.remove(class_name);
        };

    // cookieの利用確認を埋め込む
    var embedConfirmCookie = function () {
        var html = '<div id="confirm-cookie"><div id="confirm-cookie-in"><div class="lead"><p>We use cookies to ensure you have the best experience and full functionality of our website. If you continue without changing your settings, we\'ll assume that you are happy to receive all cookies from the KONAMI DIGITAL ENTERTAINMENT B.V. website. You can change your cookie settings in your browser settings.<a href="/uk/cookies_privacy.html" class="btn">Cookies Privacy</a></p></div><div class="btn-area"><p><a class="btn" href="#" onclick="acceptCookies();return false;">Continue</a></p></div></div></div><!--/#confirm-cookie-->';
        var el = document.getElementById("wripper");
        if (!el) return false;
        el.insertAdjacentHTML('beforebegin', html);
        _confirm_cookie = document.getElementById('confirm-cookie');
        addClass(_confirm_cookie, 'open');
        addClass(_body, 'confirm-cookie-open');
    }();

    function animationEndFn () {
//        console.log('animationEndFn');
        removeClass(_confirm_cookie, 'open');
        removeClass(_confirm_cookie, 'close');
        removeClass(_body, 'confirm-cookie-open');
        removeClass(_body, 'confirm-cookie-close');
    }
    // Cookie許可のボタンをクリックしたら
    window.acceptCookies = function () {
        // Cookieを書き込む
        docCookies.setItem(COOKIE_NAME, 1, Infinity, '/uk');
        // cookieの利用確認を閉じる
        addClass(_body, 'confirm-cookie-close');
        addClass(_confirm_cookie, 'close');
//        console.log(_confirm_cookie);
        _confirm_cookie.addEventListener("oAnimationEnd",animationEndFn, false);
        _confirm_cookie.addEventListener("mozAnimationEnd",animationEndFn, false);
        _confirm_cookie.addEventListener("webkitAnimationEnd",animationEndFn, false);
        _confirm_cookie.addEventListener("animationend",animationEndFn, false);
    };
}).call(this);
