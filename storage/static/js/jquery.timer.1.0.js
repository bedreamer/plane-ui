((typeof $) === 'function' ? function () {
    function IntervalTimer(period_in_10ms, callback, parameter) {
        if ( period_in_10ms < $.min_interval_period ) {
            period_in_10ms = $.min_interval_period;
        }
        this.period = period_in_10ms;
        this.callback = callback;
        this.parameter = parameter;
        this.counter = period_in_10ms / $.min_interval_period;
    }
    IntervalTimer.prototype.reset = function() {
        this.counter = this.period / $.min_interval_period;
    };

    // 定时器列表
    $.intervals = new Array();
    // 最小时间粒度
    $.min_interval_period = 10;

    function Interval_main() {
        $.intervals.each(function (it, i, it) {
            it.counter -= 1;
        });

        $.intervals.each(function (it, i, it) {
            if ( it.counter <= 0 ) {
                it.callback(it.parameter, it);
                it.reset();
            }
        });
    }
    // 启动一个定时器
    $.startInterval = function(period_in_10ms, callback, parameter) {
        var it = new IntervalTimer(period_in_10ms, callback, parameter);
        $.intervals.push(it);
        return it;
    };
    // 停止定时器
    $.stopInterval = function (it) {
        var idx = $.intervals.indexOf(it);
        if ( idx >= 0 ) {
            $.intervals.splice(idx, 1);
        }
    }
}(): (console.log("no jquery been found!")));
