/*
 url 操作库
 version: 1.0
* */
((typeof $) === 'function' ? function () {
    function UrlQuery(s) {
        var query = {};
        if ( s.length === 0 ) return {};
        s = s.split('&');
        for ( var i = 0; i < s.length; i ++ ) {
            var pair = s[i].split('=');
            if ( pair.length === 2 ) {
                var n = Number(pair[1]);
                query[ decodeURI(pair[0]) ] = Number.isNaN(n) ? decodeURI(pair[1]) : n;
            } else if ( pair.length === 1 ) {
                query[ decodeURI(pair[0]) ] = '';
            } else {
                query[ decodeURI(pair[0]) ] = decodeURI(pair.slice(1, pair.length).join("="));
            }
        }
        return query;
    }
    function PluginUrl(location) {
        this.host = location.host;
        this.hostname = location.hostname;
        this.href = location.href;
        this.origin = location.origin;
        this.pathname = location.pathname;
        this.port = location.port;
        this.protocol = location.protocol;
        var idx = this.href.indexOf('?');
        this.queryString = idx > 0 ? this.href.slice(idx + 1, this.href.length) : "";
        this.query = this.queryString.length > 0 ? UrlQuery(this.queryString) : {};
    }
    function MakeQueryString(query) {
        var s = [];
        for ( var idx in query ) {
            var pair = [encodeURI(idx), encodeURI(query[idx])].join('=');
            s.push(pair);
        }
        return s.join("&");
    }
    /*
       跳转至指定url
    * */
    PluginUrl.prototype.jump = function(url, override){
        if ( ! override ) {
            window.location.href = url;
        } else {
            url = url.split('?');
            var querystring = url[1] ? url[1] : "";
            var uri = url[0];
            var query = UrlQuery(querystring);
            for ( var idx in this.query ) {
                query[ idx ] = this.query[ idx ];
            }
            var newQueryString = MakeQueryString(query);
            if ( newQueryString.length ) {
                window.location.href = uri + '?' + newQueryString;
            } else {
                window.location.href = uri;
            }
        }
        // code should not be here.
    };
    /*
     刷新当前页面
    * */
    PluginUrl.prototype.reload = function(){
        window.location.reload();
    };
    /*
    获取url ? 后面的参数
    * */
    PluginUrl.prototype.get = function(key, default_value){
        if ( ! this.query[decodeURI(key)] ) {
            return decodeURI(default_value);
        } else {
            return this.query[decodeURI(key)];
        }
    };
    PluginUrl.prototype.getQueryString = function() {
        this.queryString = MakeQueryString(this.query);
        return this.queryString;
    };

    $.url = new PluginUrl(window.location)
}(): (console.log("no jquery been found!")));
