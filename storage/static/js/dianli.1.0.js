// coding: utf8
/*
 电力元素的处理js,所有元素都采用绝对地址定位，位置大小全都采用比例系统处理
 * */

$(document).ready(function () {
    var manager = Manager.newCanvasManager('c', {width: 900, height: 500, mode: 'edit'});
    if ( manager ) {
        g_manager = manager;
        for ( var i = 0; i < 1; i ++ ) {
            var segment = manager.newSegment(100 + i * 20, 100, 100 + i * 20, 200);
            manager.append(segment);
        }
        for ( var i = 0; i < 1; i ++ ) {
            var icon = manager.newIcon(100 + 40 * i, 450, '/static/imgs/dl/'+(i+1)+'.png');
            manager.append(icon);
        }
        for ( var i = 0; i < 1; i ++ ) {
            var lable = manager.newLable(150, 210 + 20 * i, '测试'+ i);
            manager.append(lable);
            var data = manager.newData(200, 210 + 20 * i, 'voltage', 0.0);
            manager.append(data);
        }
        if ( manager.mode != 'normal' ) {
            window.onkeydown = manager.on_keydown;
        }
        manager.renderALL();

        $("#save").click(function () {
            var backup = g_manager.on_save();
            g_backup = JSON.stringify(backup);
            console.log(g_backup);
        });

        $("#restore").click(function () {
            g_manager.on_restore(JSON.parse(g_backup));
        });
    }
});



var DianLiObject = {
    newBus: function (begin) {
    }
}

