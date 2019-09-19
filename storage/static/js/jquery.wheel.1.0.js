// coding: utf8

function RestfulAPIPath(path) {
    this.path = path;
    this.name = path.substring(path.lastIndexOf('/') + 1, path.length);
}
RestfulAPIPath.prototype.read = function (host, user_param, query_string, success, fail) {
    var get = {};

    get.host = host;
    get.method = 'GET';
    get.user_success = success ? success : null;
    get.user_fail = fail ? fail : null;
    get.user_param = user_param ? user_param : null;

    get.query_string = query_string ? "?" + query_string : "";

    get.success = function(data, status, xhr) {
        this.user_success ? this.user_success(data, this.user_param) : true;
    };
    get.fail = function() {
        this.user_fail ? this.user_fail(this.user_param) : true;
    };

    get.url = 'http://' + get.host + this.path + (this.query_string ? this.query_string : "");
    get.ajax = $.ajax(get.url, get);
    return get;
};
RestfulAPIPath.prototype.write = function (host, user_param, query_string, data, success, fail) {
    var post = {};

    post.host = host;
    post.method = 'POST';
    post.user_success = success ? success : null;
    post.user_fail = fail ? fail : null;
    post.user_param = user_param ? user_param : null;
    post.data = data ? data : null;
    post.headers = {"Content-Type": "application/json"};

    post.query_string = query_string ? "?" + query_string : "";

    post.success = function(data, status, xhr) {
        this.user_success ? this.user_success(data, this.user_param) : true;
    };
    post.fail = function() {
        this.user_fail ? this.user_fail(this.user_param) : true;
    };

    post.url = 'http:///' + post.host + this.path + (post.query_string ? '?' + post.query_string : "");
    post.ajax = $.ajax(post.url, post);
    return post;
};

function RestfulAPiManager(host, root, visitor) {
    this.host = host;
    this.root = root;
    this.visitor = visitor;
    this.polls = [];
    this.poll_idx = 0;
    this.query = null;
    this.loop = false;
    this.last = 0;
}
// 将一个路径注册到轮训序列中
RestfulAPiManager.prototype.register = function(path, user_param, success, fail) {
    var api = new RestfulAPIPath(this.root + path);
    var poll = {
        api: api,
        path: path,
        success: success,
        fail: fail,
        user_param: user_param,
        query: null,
    };
    this.polls.push(poll);

    poll.query = api.read(this.host, poll.user_param, "vistor="+this.visitor, poll.success, poll.fail);
};
// 将一个路径从轮训路径中取消
RestfulAPiManager.prototype.unregister = function (path) {
    for ( var i = 0; i < this.polls.length; i ++ ) {
        var poll = this.polls[i];
        if ( poll.path === path ) {
            this.polls.splice(i, 1);
            return;
        }
    }
};

RestfulAPiManager.prototype.poll_done = function () {
    if ( this.poll_idx + 1 === this.polls.length ) {
        this.poll_idx = 0;
        this.loop = true;
    } else {
        this.poll_idx += 1;
    }
    this.query = null;
};

function success_wrapper(data, user_param) {
    var manager = user_param.manager;
    var __poll = user_param.poll;
    __poll.success ? __poll.success(data, __poll.user_param) : true;
    manager.poll_done();
}
function fail_wrapper(user_param) {
    var manager = user_param.manager;
    var __poll = user_param.poll;
    __poll.fail ? __poll.fail(__poll.user_param) : true;
    manager.poll_done();
}
// 开始事件轮训
RestfulAPiManager.prototype.poll = function () {
    var poll = this.polls[this.poll_idx];
    var api = poll.api;
    var user_param = {manager: this, poll: poll};
    this.query = api.read(this.host, user_param, "vistor="+this.visitor, success_wrapper, fail_wrapper);
};
// 开始事件轮训
RestfulAPiManager.prototype.check_poll = function () {
    if ( this.query === null ) {
        if ( ! this.loop ) {
            return this.poll();
        }
        this.last += 1;
        if ( this.last === 100 ) {
            this.last = 0;
            this.loop = false;
        }
    }
};
