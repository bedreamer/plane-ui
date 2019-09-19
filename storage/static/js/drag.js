/**
    拖拽系统的响应函数， 想要使一个元素变得可拖拽，只需要在class中添加dragable类即可
 * */

function get_window_size() {
    return {
        width: window.innerWidth,
        height: window.innerHeight
    };
}

/*在元素上显示编辑框*/
function show_editor_box(ele) {
    var x, y, w, h;
    var client = get_window_size();

    x = parseFloat($(ele).css('left').split('px')[0]) / 100.0 * client.width - 3 + 'px';
    y = parseFloat($(ele).css('top').split('px')[0]) / 100.0 * client.height - 3 + 'px';
    w = parseFloat($(ele).css('width').split('px')[0]) / 100.0 * client.width + 6 + 'px';
    h = parseFloat($(ele).css('height').split('px')[0]) / 100.0 * client.height + 6 + 'px';

    console.log(x, y, w, h);
    var ele = $('.drag-editor');
    $(ele).css('left', x), $(ele).css('top', y), $(ele).css('width', w), $(ele).css('height', h);
    $(ele).show();
}

/*隐藏编辑框*/
function hide_editor_box() {
    $(".drag-editor").hide();
}

/*取消选择元素， 设置drag-select=false*/
function dis_select_element(ele) {
    $(ele).attr('drag-select', false);
}

/*选择元素， 被选择的元素将会被打上drag-select=true的标签*/
function select_element(ele) {
    var ele_selected = $(ele).attr('drag-select');

    /*当前元素已经被选择了*/
    if ( ele_selected === true ) {
        return;
    }

    var old_selected_ele = $('[drag-select=true]');

    for ( var i = 0; i < old_selected_ele.length; i ++ ) {
        console.log("取消旧的选择:", old_selected_ele[i]);
        dis_select_element(old_selected_ele[i]);
    }

    console.log("新的选择：", ele);
    $(ele).attr('drag-select', true);
    show_editor_box(ele);
}

/*鼠标左键双击选择事件*/
/*绑定可拖拽元素的鼠标左键点击事件*/
$(document).on("click", '.dragable', function () {
    console.log("click");
    //select_element(this);
    bindResize(this);
});

$(window).resize(function(){
    var ele_selected = $('[drag-select=true]');
    //show_editor_box(ele_selected);
});

$(document).ready(function() {
    //绑定需要拖拽改变大小的元素对象

});
var mode = 'move';

window.document.onkeydown = function (evt){
    evt = (evt) ? evt : window.event
    if (evt.keyCode && evt.keyCode == 17) { // L_CTRL
        mode = 'resize';
    }
};
window.document.onkeyup = function(evt){
    evt = (evt) ? evt : window.event
    if (evt.keyCode ) {
        if (evt.keyCode == 17) { // L_CTRL
            mode = 'move';
            console.log("move");
        } else if ( evt.keyCode == 46 ) { // DEL
            $('.element_selected').remove();
        }
   }

};
function bindResize(el){
    //初始化参数
    var els = el.style,
        //鼠标的 X 和 Y 轴坐标
        x = y = 0;
    //邪恶的食指
    $(el).mousedown(function(e){
        //按下元素后，计算当前鼠标与对象计算后的坐标
        x = e.clientX - el.offsetWidth,
        y = e.clientY - el.offsetHeight;
        //在支持 setCapture 做些东东
        el.setCapture ? (
            //捕捉焦点
            el.setCapture(),
            //设置事件
            el.onmousemove = function(ev){
                mouseMove(ev || event)
            },
            el.onmouseup = mouseUp
        ) : (
            //绑定事件
            $(document).bind("mousemove",mouseMove).bind("mouseup",mouseUp)
        )
        // 添加选择焦点
        $(el).addClass('element_selected');

        //防止默认事件发生
        e.preventDefault()
    });
    //移动事件
    function mouseMove(e){
        //宇宙超级无敌运算中...
        if ( mode == 'resize' ) {
            if ( e.clientX - x >= 3 ) {
                els.width = e.clientX - x + 'px';
            }

            if ( e.clientY - y >= 3 ) {
                els.height = e.clientY - y + 'px'
            }
        } else {
            var client = get_window_size();
            els.left = (parseFloat(els.left.split('%')[0]) / 100.0 * client.width + e.movementX) / client.width * 100.0 + '%';
            els.top = (parseFloat(els.top.split('%')[0]) / 100.0 * client.height + e.movementY) / client.height * 100.0 + '%';
            console.log(els.left, els.top, e.movementX, e.movementY);
        }
    }
    //停止事件
    function mouseUp(){
        // 删除选择焦点
        $(el).removeClass('element_selected');

        //在支持 releaseCapture 做些东东
        el.releaseCapture ? (
            //释放焦点
            el.releaseCapture(),
            //移除事件
            el.onmousemove = el.onmouseup = null
        ) : (
            //卸载事件
            $(document).unbind("mousemove", mouseMove).unbind("mouseup", mouseUp)
        )
    }
}
