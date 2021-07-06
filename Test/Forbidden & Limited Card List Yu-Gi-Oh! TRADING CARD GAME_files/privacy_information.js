(function () {
    "use strict";

    function assign(target, source) {
        var keysArray = Object.keys(source);
        var len       = keysArray.length;
        var i, k;
        target        = target || {};

        for (i = 0; i < len; i++) {
            k        = keysArray[i];
            var desc = Object.getOwnPropertyDescriptor(source, k);
            if (desc !== undefined && desc.enumerable) {
                if (Object.prototype.toString.call(source[k]) === '[object Object]') {
                    target[k] = assign(target[k], source[k]);
                } else {
                    target[k] = source[k];
                }
            }
        }
        return target;
    }

    /**
     *
     * @param elm
     */
    function closeContainer(elm) {
        elm.classList.add('kdepi-close');
        setTimeout(function () {
            elm.style.cssText = 'display:none;';
        }, option.CONTAINER_DURATION);
    }


    /**
     * ダイアログなど初期設定
     */
    function initialize() {
        var fragment, style, month;
        fragment = document.createDocumentFragment();

        // CSS
        style = document.createElement('link');
        style.setAttribute('rel', 'stylesheet');
        // www.konami.com系列は、デバッグ用のサーバーも参照できるようにしておく
        if (document.location.hostname.match(/www\.konami\.com|wwwdev\d\.konami/)) {
            style.setAttribute('href', '/games/s/common/css/style_privacy_information.css');
        } else {
            style.setAttribute('href', 'https://www.konami.com/games/s/common/css/style_privacy_information.css');
        }
        document.head.appendChild(style);

        // CookieNotice
        cookieNoticeContainer.init(fragment, option.CONTAINER_ID_COOKIE_NOTICE);

        // 年齢固定
        ageGateContainer.setAgeCookie(1900,1);

        if ((getCookieVal('AG') !== "1") && (getCookieVal('AG') !== "2")) {
            // AGが無い場合は年齢認証
            ageGateContainer.init(fragment, option.CONTAINER_ID_AGE_GATE);
        } else {
            // AGが既にある場合は、cookie notice
            cookieNoticeContainer.start();
        }

        document.body.appendChild(fragment);

        // month = document.getElementById('privacy-information-age-gate-month');
        // if (month !== null) {
        //     month.focus();
        // }
    }

    function getCookieVal(key) {
        var vTbl = (document.cookie + ';').match(key + '=([^\S;]*)');
        if (vTbl === null) {
            return null;
        }
        return vTbl[1];
    }

    function getPrimaryLanguage() {
        var languages = window.navigator.languages || [
            window.navigator.language ||
            window.navigator.userLanguage ||
            window.navigator.browserLanguage
        ];

        if (Array.isArray(languages)) {
            return languages[0] || '';
        }
        return languages || '';
    }

    function main() {
        var debugEdgescape, debugAnalytics, debugAnalyticsExpire;
        
        window.dataLayer = window.dataLayer || [];

        option = assign(option, window.kdePrivacyInformation || {});

        if (location.search.match(/debug=1/)) {
            debugEdgescape = location.search.match(/Edgescape=(\d)/);
            if (debugEdgescape !== null) {
                document.cookie = 'Edgescape=' + debugEdgescape[1] + ';Secure';

            }
            debugAnalytics = location.search.match(/Analytics=(\d)/);
            if (debugAnalytics !== null) {
                debugAnalyticsExpire = new Date();
                debugAnalyticsExpire.setDate(debugAnalyticsExpire.getDate() + 28);
                document.cookie = 'Analytics=' + debugAnalytics[1] + ';path=/;expires=' + debugAnalyticsExpire + ';Secure';
            }
        }

        // アナリティクス判定
        if (getCookieVal('Analytics') === "1") {
            return; //計測NGなので抜ける
        }
        if (getCookieVal('Analytics') === "2") {
            return; // 計測OKなので抜ける
        }

        // Edgescape判定
        if (getCookieVal('Edgescape') === "2") {
            return; // JPは計測ONなので抜ける
        }

        // Edgescapeが無くて、言語設定がjaの場合(デバッグ想定)
        if ((getCookieVal('Edgescape') !== '1')
            && (getCookieVal('Edgescape') !== '2')
            && (getCookieVal('Edgescape') !== '3')
            && (getPrimaryLanguage().match(/^ja/))) {
            return;
        }

        // 初期設定
        if (document.attachEvent ? document.readyState === "complete" : document.readyState !== "loading") {
            initialize();
        } else {
            document.addEventListener('DOMContentLoaded', initialize);
        }
    }

    var option = {
        COOKIE_NOTICE_BODY_TEXT:     {
            'en': 'We use cookies to ensure you have the best experience and full functionality of our website. If you continue without changing your settings, we’ll assume that you are happy to receive all cookies from the KONAMI DIGITAL ENTERTAINMENT. website. You can change your cookie settings in your browser settings.'
        },
        COOKIE_NOTICE_LINK_TEXT:     {
            'en': 'Cookie Notice'
        },
        COOKIE_NOTICE_LINK_URL:      {
            'en': 'https://legal.konami.com/games/privacy/'
        },
        COOKIE_NOTICE_CONTINUE_TEXT: {
            'en': 'Continue'
        },
        CONTAINER_ID_AGE_GATE:       'privacy-information-age-gate',
        CONTAINER_ID_COOKIE_NOTICE:  'privacy-information-cookie-notice',
        CONTAINER_DURATION:          800
    };

    /**
     * 年齢認証
     * @type {{el: Element, init: init}}
     */
    var ageGateContainer = {
        el:                 null,
        containerClosed:    false,
        sendBirthComplete:  false,
        /**
         *
         * @param fragment
         * @param id
         */
        init:               function (fragment, id) {
            var months, years, i, now, nowYear;

            // ダイアログ
            this.el    = document.createElement('div');
            this.el.id = id;
            this.el.classList.add('kdepi-overwrite');
            months = '';
            for (i = 1; i <= 12; i++) {
                months += '<option value="' + i + '">' + i + '</option>';
            }
            months += '<option value="" selected disabled>Month</option>';
            years    = '';
            now      = new Date();
            nowYear  = now.getFullYear();
            for (i = 1900; i <= nowYear; i++) {
                years += '<option value="' + i + '">' + i + '</option>';
                if (i === 2000) {
                    years += '<option value="" disabled selected>Year</option>';
                }
            }

            this.el.innerHTML = '<div class="kdepi-fade"><div class="kdepi-panel"><div class="kdepi-content"><p>Please enter your birth date.</p><select id="privacy-information-age-gate-month" tabindex="1">' + months + '</select><select id="privacy-information-age-gate-year" tabindex="2">' + years + '</select><a id="privacy-information-age-gate-submit" href="#" tabindex="3">Send</a></div></div></div>';

            this.el.querySelector("#privacy-information-age-gate-submit").addEventListener('click', this.onAgeGateSubmit.bind(this));

            fragment.appendChild(this.el);

        },
        /**
         *
         * @param e
         */
        onAgeGateSubmit:    function (e) {
            var m, y, mV, yV, valid;
            m     = this.el.querySelector('#privacy-information-age-gate-month');
            y     = this.el.querySelector('#privacy-information-age-gate-year');
            valid = true;

            mV = parseInt(m.value.trim(), 10);
            if (isNaN(mV) || (mV < 1) || (12 < mV)) {
                m.classList.add('kdepi-error');
                valid = false;
            } else {
                m.classList.remove('kdepi-error');
            }

            yV = parseInt(y.value.trim(), 10);
            if (isNaN(yV) || (yV < 1900)) {
                y.classList.add('kdepi-error');
                valid = false;
            } else {
                y.classList.remove('kdepi-error');
            }

            // 入力された値が不正なら抜ける
            if (!valid) {
                e.preventDefault();
                return;
            }

            this.setAgeCookie(yV, mV);

            if ((getCookieVal('AG') === '2') && (getCookieVal('Edgescape') === '3')) {
                window.dataLayer.push({
                    event: 'AnalyticsON_EG3-AG2'
                });
            }

            // 16才以下ならAnalytics不可
            if (getCookieVal('AG') === '1') {
                this.setAnalyticsCookie('1');
            }

            // 消す
            this.containerClosed = false;
            closeContainer(this.el);
            setTimeout(function () {
                this.containerClosed = true;
                this.startCookieNotice();
            }.bind(this), option.CONTAINER_DURATION);

            e.preventDefault();
        },
        setAgeCookie:       function (year, month) {
            var now, birth, cookieVal, expire, COOKIE_VAL_UNDER = 1, COOKIE_VAL_UPPER = 2;

            now       = new Date();
            birth     = new Date(year, month - 1);
            cookieVal = COOKIE_VAL_UNDER;
            if ((now.getTime() - birth.getTime()) > (16 * 365 * 24 * 60 * 60 * 1000)) {
                cookieVal = COOKIE_VAL_UPPER;
            }
            expire = new Date();
            expire.setDate(expire.getDate() + 60);

            document.cookie = 'AG=' + cookieVal + ';path=/;expires=' + expire.toUTCString() + ';Secure';
        },
        setAnalyticsCookie: function (v) {
            var expire;

            expire = new Date();
            expire.setDate(expire.getDate() + 28);

            document.cookie = 'Analytics=' + v + ';path=/;expires=' + expire.toUTCString() + ';Secure';
        },
        startCookieNotice:  function () {
            if (this.containerClosed) {
                cookieNoticeContainer.start();
            }
        }
    };

    //--------------------------------------------------------------------------------------------------------------
    /**
     * CookieNotice + opt-in
     * @type {{el: Element, init: init}}
     */
    var cookieNoticeContainer = {
        el:             null,
        /**
         *
         * @param fragment
         * @param id
         */
        init:           function (fragment, id) {
            // ダイアログ
            this.el    = document.createElement('div');
            this.el.id = id;
            this.el.classList.add('kdepi-close');
            this.el.style.cssText = 'display: none;';
            this.el.innerHTML     = '<div class="kdepi-content"><section class="kdepi-cookie-notice"><p>' + option.COOKIE_NOTICE_BODY_TEXT['en'] + '<a href="' + option.COOKIE_NOTICE_LINK_URL['en'] + '" target="_blank">[' + option.COOKIE_NOTICE_LINK_TEXT['en'] + ']</a></p></section><a id="privacy-information-cookie-notice-opt-in" href="#">' + option.COOKIE_NOTICE_CONTINUE_TEXT['en'] + '</a></div>';

            this.el.querySelector("#privacy-information-cookie-notice-opt-in").addEventListener('click', this.onOptInSubmit.bind(this));

            fragment.appendChild(this.el);
        },
        onOptInSubmit:  function (event) {
            this.setOptInCookie();

            if ((getCookieVal('AG') === '2') && (getCookieVal('Edgescape') === '1')) {
                window.dataLayer.push({
                    event: 'AnalyticsON_EG1-AG2-AO2'
                });
            }

            closeContainer(this.el);

            event.preventDefault();
        },
        setOptInCookie: function () {
            var cookieVal, expire, COOKIE_VAL_OPT_IN_NG = 1, COOKIE_VAL_OPT_IN_OK = 2;

            cookieVal = COOKIE_VAL_OPT_IN_OK;
            expire    = new Date();
            expire.setDate(expire.getDate() + 28);

            document.cookie = 'AO=' + cookieVal + ';path=/;expires=' + expire + ';Secure';
        },
        /**
         *
         */
        start:          function () {
            if (getCookieVal('Edgescape') !== '1') {
                return;
            }
            if (getCookieVal('AG') !== '2') {
                return;
            }
            if (getCookieVal('AO') === '2') {
                return;
            }

            this.el.style.cssText = 'display: block;';
            this.el.classList.remove('kdepi-close');
        }
    };

    main();
}());