
console.log("it's works!")



jQuery(document).ready(function($){
    // 弹出编辑选择框，确定是编辑元素或是编辑
    $('.cls_group').click(function (){
        console.log(this.offsetLeft, this.offsetTop, this.clientWidth, this.clientHeight);
    });

    $('.cls_group').dblclick(function (){
        //console.log($(this).attr('gid'));
        var src = '/polls/bind/' + $(this).attr('gid') + '/';
        console.log(src);
        $('#id_iframe').attr('src', src);
        $('#id_group_editor').modal({
            keyboard: true
        });
        /*
        var x = this.offsetLeft, y = this.offsetTop, width = this.clientWidth, height = this.clientHeight;
        var gid = $(this).attr('gid');
        var txt = $(this).attr('name');
        var pid = $('#id_body').attr('pid');

        $("[name='pid']").val(pid);
        $("[name='gid']").val(gid);

        $("[name='group_x']").val(x);
        $("[name='group_y']").val(y);
        $("[name='group_width']").val(width);
        $("[name='group_height']").val(height);
        $("[name='group_title']").val(txt);
        */
    });
});
