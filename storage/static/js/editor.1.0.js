// coding: utf8

var manager = null;
$(document).ready(function () {
    manager = Manager.newCanvasManager('c', {
        width: 1280,
        height: 600,
        mode: 'edit',
        background_image: "/static/imgs/backgroud-3.png",
    });
    window.onkeydown = manager.canvas.onkeydown;

    $(".segment").click(function () {
        var strockStyle = $(this).css("background-color");
        var lineWidth = Number($(this).css("height").split('p')[0]);
        var user_options = {strokeStyle: strockStyle, lineWidth: lineWidth, termial_strokeStyle: strockStyle};
        manager.on_StartSegment(user_options);
    });

    $("#id_save").click(function () {
        var name = $("input[name=id]").val();
        if ( name === "" || ! name ) {
            alert("填写ID!!");
            return;
        }
        var objects = manager.on_save();
        var json = JSON.stringify(objects);
        $.ajax({
            url: "/polls/__editor/test/",
            type: "POST",
            data: {name: 'test', content: json},
            headers: { "X-CSRFtoken":$.cookie("csrftoken")},
            success: function (arg) {
                alert('save success!');
            },
            fail: function () {
                alert('save fail!');
            }
        });
    });

    $("#id_restore").click(function () {
        var name = $("input[name=id]").val();
        if ( name === "" || ! name ) {
            alert("填写ID!!");
            return;
        }
        $.ajax({
            url: "/polls/__editor/test/",
            type: "GET",
            data: {name: name},
            headers: { "X-CSRFtoken":$.cookie("csrftoken")},
            success: function (data, status) {
                var name = data.name;
                var content = data.content;
                var object = JSON.parse(content);
                manager.on_restore(object);
            },
            fail: function () {
                alert('save fail!');
            }
        });
    });

    $(".labletext").click(function () {
        manager.on_StartLable("标签")
    });

    $(".yaoce").click(function () {
    });

    $(".yaoxin").click(function () {
    });

    $(".icon").click(function () {
        var src = $(this).css("background-image").split('"')[1];
        manager.on_StartIcon(src);
    });

    // 关闭编辑框
    $(".ke-icon-close").click(function () {
        $(".edior_box").toggle();
    });
    // 保存编辑内容
    $(".ke-icon-ok").click(function () {
        $(".edior_box").toggle();
        var config = {};
        config.color = $("input[name=color]").val();
        config.data = $("input[name=data]").val();
        config.width = Number($("input[name=width]").val());
        config.height = Number($("input[name=height]").val());
        config.data = $("input[name=data]").val();
        config.font_size = Number($('select[name=font_size] option:selected').val());
        manager.on_edit_save(config);
    });

    manager.ondblclick_capture = function (e, object) {
        $(".edior_box").show();

        var box_width = Number($('.edior_box').css('width').split('p')[0]);
        var box_height = Number($('.edior_box').css('height').split('p')[0]);
        var target_left = e.clientX - box_width / 2;
        var target_top = e.clientY - box_height - 20;

        $(".edior_box").css("left", target_left + 'px');
        $(".edior_box").css("top", target_top + 'px');
        var config = object.on_config_prepare();

        config.font_size && $('select[name=font_size] option:selected').val(config.font_size);
        $("input[name=color]").val(config.color);
        $("input[name=width]").val(config.width);
        $("input[name=height]").val(config.height);
        $("input[name=data]").val(config.data);
    }
});


