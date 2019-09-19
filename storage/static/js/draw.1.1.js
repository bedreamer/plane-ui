// coding: utf8
// v1.1
// 判断数组中是否有元素
var DictHave = function (dict, e) {
    for ( var idx in dict ) {
        if ( dict[idx] === e ) return true;
    }
    return false;
};

// 根据用户参数，类参数和默认参数获取设置值
function getOptionValue(name, default_value, default_options, user_options) {
    if ( user_options && user_options[name] ) {
        return user_options[name];
    }
    if ( default_options && default_options[name] ) {
        return default_options[name];
    }
    return default_value;
}

// 测算文本的像素长度
function MeasurTextInPixel(txt, font_size) {
    var width = 0;
    for ( var i = 0; i < txt.length; i ++ )  {
        if ( txt[i].charCodeAt() < 128 ) {
            width += (font_size / 2);
        } else {
            width += font_size;
        }
    }
    return width;
}


var CanvasObject = {
    // Canvas对象
    newCanvasObject: function (manager, type, left, top, width, height, default_options, user_options) {
        var object = {};

        // 对象管理单元
        object.manager = manager;
        object.id = manager.getid();
        object.type = type;

        object.left = getOptionValue('left', left, default_options, user_options);
        object.top = getOptionValue('top', top, default_options, user_options);
        object.width = getOptionValue('width', width, default_options, user_options);
        object.height = getOptionValue('height', height, default_options, user_options);

        object.strokeStyle = getOptionValue("strokeStyle", "#000000", default_options, user_options);
        object.fillStyle = getOptionValue("fillStyle", "#000000", default_options, user_options);

        object.font_size = getOptionValue("font_size", 10, default_options, user_options);
        object.font_faimly = getOptionValue("font_faimly", "san-seirf", default_options, user_options);
        object.default_font = [object.font_size, "px ", object.font_faimly].join("");
        object.font = getOptionValue("font", object.default_font, default_options, user_options);
        object.getfont = function() {return [this.font_size, "px ", this.font_faimly].join("");}
        object.lineWidth = getOptionValue("lineWidth", 1, default_options, user_options);

        // 元素可以被选择，编辑模式下可用，正常模式下需要设置为false
        object.selectable = (manager.mode == 'normal') ? false : true;
        // 元素可以通过鼠标拖拽进行大小变化, 端点，线段，标签，数据都无法通过拖拽改变大小
        object.resizable = getOptionValue("resizable", false, default_options, user_options);

        object.filter = getOptionValue("filter", "none", default_options, user_options);
        object.globalAlpha = getOptionValue("globalAlpha", 1, default_options, user_options);
        object.globalCompositeOperation = getOptionValue("globalCompositeOperation", "source-over", default_options, user_options);
        object.imageSmoothingEnabled = getOptionValue("imageSmoothingEnabled", true, default_options, user_options);
        object.imageSmoothingQuality = getOptionValue("imageSmoothingQuality", "low", default_options, user_options);
        object.lineCap = getOptionValue("lineCap", "butt", default_options, user_options);
        object.lineDashOffset = getOptionValue("lineDashOffset", 0, default_options, user_options);
        object.lineJoin = getOptionValue("lineJoin", "miter", default_options, user_options);
        object.miterLimit = getOptionValue("miterLimit", 10, default_options, user_options);
        object.shadowBlur = getOptionValue("shadowBlur", 0, default_options, user_options);
        object.shadowColor = getOptionValue("shadowColor", "rgba(0, 0, 0, 0)", default_options, user_options);
        object.shadowOffsetX = getOptionValue("shadowOffsetX", 0, default_options, user_options);
        object.shadowOffsetY = getOptionValue("shadowOffsetY", 0, default_options, user_options);
        object.textAlign = getOptionValue("textAlign", "start", default_options, user_options);
        object.textBaseline = getOptionValue("textBaseline", "hanging", default_options, user_options);

        object.default_options = default_options;
        object.user_options = user_options;

        // 标示对象是否被选择
        object.selected = false;

        // 由继承的对象定义
        object.on_normal_save = function () {};
        // 选择判定, 编辑模式返回当前对象，否则返回null
        object.on_select_in = function () {
            if ( ! this.selectable ) return null;
            this.selected = true;
            return this;
        };
        // 取消选择
        object.on_select_out = function() {
            if ( ! this.selectable ) return null;
            this.selected = false;
            return this;
        };
        // 判定鼠标位置是否在对象内部
        object.on_is_mouse_in = function (x, y) {
            if ( ! this.selectable ) return null;
            if ( x < this.left - 10 ) return null;
            if ( y < this.top - 10 ) return null;
            if ( x > this.left + this.width + 10 ) return null;
            if ( y > this.top + this.height + 10 ) return null;
            return this;
        };
        // 返回对象的位置信息
        object.on_get_position = function () {
            return {left: this.left, top: this.top};
        };
        // 设置对象的新位置
        object.on_set_position = function (left, top) {
            this.left = left;
            this.top = top;
        };

        // 复制对象事件
        object.on_copy = function () {return []};
        // 对象旋转事件
        object.on_rotate = function (e) {};
        // 删除事件, 返回需要删除的对象
        object.on_delete = function (e) {return this;}

        // 保存通用数据信息
        object.on_normal_save = function () {
            return {
                id: this.id,
                type: this.type,
                left: this.left, top: this.top, width: this.width, height: this.height,
                font_size: this.font_size, font_faimly: this.font_faimly,
                font: this.font, default_font: this.default_font,
                lineWidth: this.lineWidth,
                strokeStyle: this.strokeStyle, fillStyle: this.fillStyle
            };
        };
        // 还原通用数据信息
        object.on_normal_restore = function (data) {
            this.id = data.id;
            this.type = data.type;
            this.left = data.left; this.top = data.top; this.width = data.width; this.height = data.height;
            this.font_size = data.font_size; this.font_faimly = data.font_faimly;
            this.font = data.font; this.default_font = data.default_font;
            this.lineWidth = data.lineWidth;
            this.strokeStyle = data.strokeStyle; this.fillStyle = data.fillStyle;
        };

        // 配置事件
        object.on_config_save = function (config) {
            this.width = config.width;
            this.height = config.height;
        };
        // 准备配置
        object.on_config_prepare = function () {};

        // 对象事件 对象拖拽, 删除, 选择，取消选择
        return object;
    },
    // 端点对象
    newNode: function(manager, x, y, user_options) {
        var radius = 2;
        var default_options = {
            radius: radius,
            fillStyle: "#ffffff",
            strokeStyle: "#8ceece",
            lineWidth: 2
        };
        var node = CanvasObject.newCanvasObject(manager, 'node', x - radius, y - radius, radius * 2, radius * 2, default_options, user_options);

        node.radius = getOptionValue("radius", radius, this.default_options, user_options);
        node.x = x;
        node.y = y;

        // 作为起点的线段
        node.begin_segments = null;
        // 作为终点的线段
        node.end_segments = null;

        node.on_delete = function(){return this.begin_segments ? this.begin_segments : this.end_segments;};
        node.on_save = function () {
            var me = {};
            me.normal = this.on_normal_save();
            me.x = this.x; me.y = this.y; me.radius = radius;
            return me;
        };
        node.on_restore = function (data) {
            this.x = data.x; this.y = data.y; this.radius = data.radius;
            this.on_normal_restore(data.normal);
        };
        node.on_move = function (x, y) {};
        node.on_render = function () {
            if ( this.selected )
            {
                var r = this.radius + this.lineWidth + 2;
                var path_begin = [this.x - r, this.y - r]; // (x-r, y-r)
                var frame_path = [
                    [this.x + r, this.y - r], // (x+r, y-r)
                    [this.x + r, this.y + r], // (x+r, y+r)
                    [this.x - r, this.y + r], // (x-r, y+r)
                    [this.x - r, this.y - r], // (x-r, y-r)
                ];
                this.manager.renderFrame(path_begin, frame_path);
            }
            this.manager.renderCircle(this.x, this.y, this.radius, this.fillStyle, this.strokeStyle, this.lineWidth);
        };
        // 返回对象的位置信息
        node.on_get_position = function () {
            return {left: this.x, top: this.y};
        };
        // 设置对象的新位置
        node.on_set_position = function (left, top) {
            this.x = this.left = left;
            this.y = this.top =  top;
            this.begin_segments && this.begin_segments.on_set_begin_position(left, top);
            this.end_segments && this.end_segments.on_set_end_position(left, top);
        };

        return node;
    },
    // 线段对象
    newSegment: function(manager, fx, fy, tx, ty, user_options) {
        var default_options = {strokeStyle: "#95224c", lineWidth: 6};
        var terminal_strockStyle = getOptionValue("terminal_strockStyle", '#ffffff', this.default_options, user_options);
        var terminal_fillStyle = getOptionValue("terminal_fillStyle", '#000000', this.default_options, user_options);
        var segment = CanvasObject.newCanvasObject(manager, 'segment', fx, fy, 1, 1, default_options, user_options);

        if ( ! user_options ) user_options = {};
        user_options.fillStyle = terminal_fillStyle;
        user_options.strokeStyle = terminal_strockStyle;
        var begin = CanvasObject.newNode(manager, fx, fy, user_options);
        var end = CanvasObject.newNode(manager, tx, ty, user_options);
        segment.fx = fx;
        segment.fy = fy;
        segment.tx = tx;
        segment.ty = ty;

        segment.begin = begin;
        segment.begin.begin_segments = segment;

        segment.end = end;
        segment.end.end_segments = segment;

        segment.on_save = function () {
            var me = {};
            me.normal = this.on_normal_save();
            me.fx = this.fx; me.fy = this.fy; me.tx = this.tx; me.ty = this.ty;
            me.begin = this.begin.on_save();
            me.end = this.end.on_save();
            return me;
        };
        segment.on_restore = function (data) {
            this.on_normal_restore(data.normal);
            this.fx = data.fx; this.fy = data.fy; this.tx = data.tx; this.ty = data.ty;
            this.begin.on_restore(data.begin);
            this.end.on_restore(data.end);
        };
        segment.on_render = function () {
            this.manager.renderLine(this.fx, this.fy, this.tx, this.ty, this.strokeStyle, this.lineWidth);
            this.begin.on_render();
            this.end.on_render();
        };
        segment.on_set_begin_position = function(x, y) {
            this.fx = x;
            this.fy = y;
        };
        segment.on_set_end_position = function(x, y) {
            this.tx = x;
            this.ty = y;
        };
        segment.on_is_mouse_in = function (x, y) {
            var fn = this.begin.on_is_mouse_in(x, y);
            if ( fn ) return fn;
            fn = this.end.on_is_mouse_in(x, y);
            if ( fn ) return fn;
            return null;
        };
        segment.on_click = function () {};

        return segment;
    },
    // 图标对象
    newIcon: function (manager, left, top, src, user_options) {
        var default_width = default_height = 20;
        var default_options = {
            width: default_width,
            height: default_height,
            resizable: true, // 图标需要通过鼠标拖拽来改变大小
            rotate_deg: 0,   // 旋转角度
        };
        var icon = CanvasObject.newCanvasObject(manager, 'icon', left, top, default_width, default_height, default_options, user_options);

        icon.src = src;
        icon.rotate_deg = getOptionValue('rotate_deg', 0, default_options, user_options);
        icon.img = new Image();
        icon.img.iconobject = icon;
        icon.img_ready = false;
        icon.img_need_render = false;
        icon.img.onload = function() {
            this.iconobject.img_ready = true;
            if ( this.iconobject.img_need_render ) {
                this.iconobject.on_render();
            }
        };
        icon.img.src = src;
        icon.on_save = function () {};
        icon.on_render = function () {
            if ( this.selected ) {
                var path_begin = [this.left, this.top]; // (x-r, y-r)
                var frame_path = [
                    [this.left + this.width, this.top], // (x+r, y-r)
                    [this.left + this.width, this.top + this.height], // (x+r, y+r)
                    [this.left, this.top + this.height], // (x-r, y+r)
                    [this.left, this.top], // (x-r, y-r)
                ];
                this.manager.renderFrame(path_begin, frame_path);
            }
            if ( this.img_ready ) {

                this.manager.renderImage(this.left, this.top, this.width, this.height, this.rotate_deg, this.img);
            } else {
                this.img_need_render = true;
            }
        };
        icon.on_copy = function () {
            var new_left = this.left + this.width + 10;
            var new_top = this.top + 10;
            var copy = CanvasObject.newIcon(this.manager, new_left, new_top, this.src, this.user_options);
            copy.rotate_deg = this.rotate_deg;
            copy.height = this.height;
            copy.width = this.width;
            return [copy]
        };
        icon.on_rotate = function (e, delta_deg) {this.rotate_deg += delta_deg;};
        icon.on_save = function () {
            var me = {};
            me.normal = this.on_normal_save();
            me.src = this.src;
            me.rotate_deg = this.rotate_deg;
            return me;
        };
        icon.on_restore = function (data) {
            this.on_normal_restore(data.normal);
            this.src = data.src;
            this.rotate_deg = data.rotate_deg;
        };
        icon.on_config_prepare = function () {
            var config = {};
            config.width = this.width;
            config.height = this.height;
            config.data = this.src;
            return config;
        };
        icon.on_config_save = function (config) {
            this.width = config.width;
            this.height = config.height;
            this.src = config.data;
            this.img_ready = false;
            this.img.src = config.data;
        };

        return icon;
    },
    // 标签对象
    newLable: function (manager, left, top, txt, user_options) {
        var default_options = {
            font_faimly: "san-serif",
            font_size: 15,
            fillStyle: "#ffffff",
        };
        var lable = CanvasObject.newCanvasObject(manager, 'lable', left, top, 0, default_options.font_size, default_options, user_options);

        lable.txt = txt;
        lable.set = function (txt) {
            this.txt = txt;
            this.width = MeasurTextInPixel(txt, this.font_size);
        };
        lable.set(txt);
        lable.on_save = function () {};
        lable.on_render = function () {
            if ( this.selected ) {
                var path_begin = [this.left - 3, this.top - 3];
                var frame_path = [
                    [this.left + this.width + 3, this.top - 3],
                    [this.left + this.width + 3, this.top + this.font_size + 3],
                    [this.left - 3, this.top + this.font_size + 3],
                    [this.left - 3, this.top - 3],
                ];
                this.manager.renderFrame(path_begin, frame_path);
            }
            this.manager.renderText(this.left, this.top, this.txt, this.width, this.getfont(), this.fillStyle, this.textBaseline);
        };
        lable.on_copy = function () {
            var new_left = this.left + this.width + 10;
            var new_top = this.top + 10;
            var new_txt = this.txt + '_copy';
            var copy = CanvasObject.newLable(this.manager, new_left, new_top, new_txt, this.user_options);
            copy.font = this.font;
            copy.font_size = this.font_size;
            copy.font_faimly = this.font_faimly;
            return [copy]
        };
        lable.on_save = function () {
            var me = {};
            me.normal = this.on_normal_save();
            me.txt = this.txt;
            return me;
        };
        lable.on_restore = function (data) {
            this.on_normal_restore(data.normal);
            this.set(data.txt);
        };
        lable.on_config_prepare = function () {
            var config = {};
            config.width = this.width;
            config.height = this.height;
            config.color = this.fillStyle;
            config.data = this.txt;
            config.font_size = this.font_size;
            return config;
        };
        lable.on_config_save = function (config) {
            this.width = config.width;
            this.height = config.height;
            this.fillStyle = config.color;
            this.font_size = config.font_size;
            this.set(config.data);
        };

        return lable;
    },
    // 数据对象
    newData: function (manager, left, top, key, default_value, user_options) {
        var default_options = {
            font_faimly: "san-serif",
            font_size: 10,
            fillStyle: "#49caee",
        };
        var default_width = default_options.font_size * String(default_value).length;
        var data = CanvasObject.newCanvasObject(manager, 'data', left, top, default_width, default_options.font_size, default_options, user_options);

        data.txt = String(default_value);
        data.key = key;
        data.set = function (txt) {
            this.txt = txt;
            this.width = txt.length * this.font_size;
        };
        data.on_save = function () {};
        data.on_render = function () {
            if ( this.selected ) {
                var r = 2 + this.width / 2;
                var center = {x: this.left + this.width / 2, y: this.top + this.height/2};
                var path_begin = [center.x - r, center.y - r]; // (x-r, y-r)
                var frame_path = [
                    [center.x + r, center.y - r], // (x+r, y-r)
                    [center.x + r, center.y + r], // (x+r, y+r)
                    [center.x - r, center.y + r], // (x-r, y+r)
                    [center.x - r, center.y - r], // (x-r, y-r)
                ];
                this.manager.renderFrame(path_begin, frame_path);
            }

            this.manager.renderText(this.left, this.top, String(this.txt), this.width, this.getfont(), this.fillStyle, this.textBaseline);
        };
        data.on_save = function () {
            var me = {};
            me.normal = this.on_normal_save();
            me.txt = this.txt;
            me.key = this.key;
            return me;
        };
        data.on_restore = function (d) {
            this.on_normal_restore(d.normal);
            this.key = d.key;
            this.set(d.txt);
        };
        data.on_config_prepare = function () {
            var config = {};
            config.width = this.width;
            config.height = this.height;
            config.data = this.key;
            config.font_size = this.font_size;
            return config;
        };
        data.on_config_save = function (config) {
            this.width = config.width;
            this.height = config.height;
            this.key = config.data;
            this.font_size = config.font_size;
        };

        return data;
    },
};

// Canvas管理器
var Manager = {
    newCanvasManager: function(canvas_dom_id, user_options) {
        var manager = {};
        manager.canvas = document.getElementById(canvas_dom_id);
        if ( !manager.canvas ) {
            console.error(['could not found <canvas id="', canvas_dom_id, '"></canvas> lable!'].join(""));
            return null;
        }
        //{{ 截获canvas的全部输入事件
        manager.canvas.manager = manager;
        manager.canvas.onclick = function (e) {this.manager.on_click(e);};
        manager.canvas.onmousedown = function (e) {this.manager.on_mousedown(e);};
        manager.canvas.onmouseup = function (e) {this.manager.on_mouseup(e);};
        manager.canvas.onmousemove = function (e) {this.manager.on_mousemove(e);};
        manager.canvas.ondblclick = function (e) {this.manager.on_dblclick(e);};
        manager.canvas.onkeydown = function (e) {this.manager.on_keydown(e);}

        manager.onclick_capture = null;
        manager.onmousemove_capture = null;
        manager.ondblclick_capture = null;
        //}}

        manager.ctx = document.getElementById(canvas_dom_id).getContext('2d');
        manager.canvas_dom_id = canvas_dom_id;
        manager.user_options = user_options;

        // 方便计算文本区域
        manager.ctx.textBaseline = getOptionValue('textBaseline', 'hanging', null, user_options);

        manager.canvas_width = getOptionValue('width', 800, null, user_options);
        manager.canvas_height = getOptionValue('height', 800, null, user_options);
        // 设置Canvas画布的宽度和高度适应新的配置项
        manager.canvas.width = getOptionValue('width', 500, null, user_options);
        manager.canvas.height = getOptionValue('height', 500, null, user_options);

        manager.canvas_border_width = getOptionValue('border_width', 1, null, user_options);
        manager.canvas_border_color = getOptionValue('border_color', 1, null, user_options);

        manager.canvas_background_color = getOptionValue('background_color', '#777777', null, user_options);
        manager.canvas_background_image = getOptionValue('background_image', '', null, user_options);
        manager.background_image_object = new Image();
        manager.background_image_object.manager = manager;
        manager.background_image_object_ready = false;
        manager.background_image_object.onload = function() {
            this.manager.background_image_object_ready=true;
            this.manager.renderALL();
        };
        manager.background_image_object.src = manager.canvas_background_image;

        manager.select_box_color = getOptionValue('select_box_color', '#ff0000', null, user_options);

        // 显示模式, edit, normal, preview。normal,preview模式下元素不可编辑
        manager.mode = getOptionValue('mode', 'normal', null, user_options);

        // Canvas对象列表
        manager.objects = {};
        manager.__id_counter__ = 0;
        // 获取对象的id
        manager.getid = function() { this.__id_counter__ += 1; return this.__id_counter__; };

        //{{ 管理对象
        manager.newSegment = function (fx, fy, tx, ty, user_options) {
            var segment = CanvasObject.newSegment(this, fx, fy, tx, ty, user_options);
            return segment;
        };
        manager.newIcon = function (left, top, src, user_options) {
            var icon = CanvasObject.newIcon(this, left, top, src, user_options);
            return icon;
        };
        manager.newLable = function (left, top, txt, user_options) {
            var lable = CanvasObject.newLable(this, left, top, txt, user_options);
            return lable;
        };
        manager.newData = function (left, top, key, default_value, user_options) {
            var data = CanvasObject.newData(this, left, top, key, default_value, user_options);
            return data;
        };
        manager.append = function(object) {this.objects[object.id] = object;};
        //}}

        //{{ 鼠标键盘输入事件
        // 通过点击鼠标达到选择对象的目的
        manager.on_click = function (e) {
            if ( this.onclick_capture ) {
                return this.onclick_capture(e);
            }

            for ( var idx in this.objects ) {
                var object = this.objects[idx].on_is_mouse_in(e.layerX, e.layerY);
                if ( ! object) continue;
                return this.on_select_object(e, object);
            }

            // 如果没有选择到任何对象也通知管理器
            return this.on_select_nothing(e);
        };
        manager.on_mousedown = function (e) {
            var object = null;
            this.mousedown_postion = {left: e.layerX, top: e.layerY};
            for ( var idx in this.objects ) {
                var object = this.objects[idx].on_is_mouse_in(e.layerX, e.layerY);
                if ( object === null ) continue;

                var selected = this.get_selected_objects();
                if ( DictHave(selected, object) === false && e.shiftKey === false ) break;

                for ( var i = 0; i < selected.length; i ++ ) {
                    var target = selected[i];
                    var position = target.on_get_position();
                    target.mousedown_position = position;
                }
                return;
            }

            // 在空白区域按下鼠标，清空选择列表
            this.on_select_nothing(e);
        };
        manager.on_mouseup = function (e) {
            if ( e.shiftKey === true ) return;
            for ( var idx in this.objects ) {
                var object = this.objects[idx].on_is_mouse_in(e.layerX, e.layerY);
                if ( object === null ) continue;

                var selected = this.get_selected_objects();
                if ( DictHave(selected, object) === true && e.shiftKey === false ) break;

                return;
            }

            // 如果shift键没有按下则清除所有已选择的对象
            this.on_select_nothing(e);
        };
        manager.on_mousemove = function (e) {
            if ( this.onmousemove_capture ) {
                return this.onmousemove_capture(e);
            }

            // 左键未按下不做任何处理
            if ( e.buttons === 0 ) return;
            //console.log(e);
            var selected = this.get_selected_objects();
            if ( selected.length === 0 ) return;

            for (var i = 0; i < selected.length; i ++ ) {
                var delta_left = e.layerX - this.mousedown_postion.left;
                var delta_top = e.layerY - this.mousedown_postion.top;
                var new_left = selected[i].mousedown_position.left + delta_left;
                var new_top = selected[i].mousedown_position.top + delta_top;
                selected[i].on_set_position(new_left, new_top);
            }

            this.renderALL();
        };
        // 尝试启动编辑对象的编辑框
        manager.on_dblclick = function (e) {
            var object = null;

            for ( var idx in this.objects ) {
                object = this.objects[idx].on_is_mouse_in(e.layerX, e.layerY);
                if ( ! object ) continue;

                // 捕捉编辑动作
                return this.ondblclick_capture && this.ondblclick_capture(e, object);

                var selected = this.get_selected_objects();
                if (DictHave(selected, object) ) {
                    return;
                } else {
                    this.on_select_nothing(e);
                    this.on_select_object(e, object);
                }

                return this.on_begin_editor(e, object);
            }

            // 双击的位置没有任何元素则将已经选择的列表清空
            this.on_select_nothing(e);
        };

        manager.on_keydown = function (e) {
            if ( e.key === 'c' && e.ctrlKey === true ) {
                this.on_copy(e);
            } else if ( e.key === 'v' && e.ctrlKey === true ) {
                this.on_paste(e);
            } else if ( e.key === 'r' && e.ctrlKey === true ) {
                this.on_rotate(e, 10);
                e.preventDefault();
            } else if ( e.key === 'Delete' || e.keyCode === 46 ) {
                this.on_delete(e);
            }
            //console.log(e);
        };
        manager.on_keyup = function (e) {};
        manager.on_keypress = function (e) {};
        //}}

        //{{ 对象事件
        manager.mouse_select_object = {length: 0};
        manager.on_select_object = function(evt, object) {
            // 多选模式
            if ( evt.shiftKey === true ) {
                if ( this.mouse_select_object[object.id] === undefined ) {
                    // 在选择列表中还未存在过
                    manager.mouse_select_object.length += 1;
                    this.mouse_select_object[object.id] = object;
                    object.on_select_in();
                } else {
                    // 已经存在的则删除
                    manager.mouse_select_object.length -= 1;
                    object.on_select_out();
                    delete this.mouse_select_object[object.id];
                }
            } else {
                manager.mouse_select_object  = {length: 1};
                object.on_select_in();
                this.mouse_select_object[object.id] = object;
            }

            this.renderALL();
        };
        manager.on_select_nothing = function(evt, reason) {
            var selected = this.get_selected_objects();
            for ( var i = 0; i < selected.length; i ++ ) {
                selected[i].on_select_out();
            }
            manager.mouse_select_object = {length: 0};

            this.renderALL();
        };
        manager.get_selected_objects = function() {
            var objects = new Array();
            for ( var idx in this.mouse_select_object ) {
                if ( idx == 'length' ) continue;
                objects.push(this.mouse_select_object[idx]);
            }
            return objects;
        };
        // 双击对象表示请求编辑该对象
        manager.on_begin_editor = function(e, object) {
        };
        // 点击了编辑框上的完成按钮
        manager.on_end_editor = function(object_id) {
        };
        // 取消了编辑
        manager.on_cancel_editor = function(object_id) {
        };

        manager.copyed_list = new Array();
        // 对象拷贝
        manager.on_copy = function() {
            var selected = this.get_selected_objects();
            var copyed_list = new Array();
            for ( var i = 0; i < selected.length; i ++ ) {
                var object_list = selected[i].on_copy();
                if ( ! object_list ) continue;
                for ( var idx = 0; idx < object_list.length; idx ++ ) {
                    copyed_list.push(object_list[idx]);
                }
            }
            this.copyed_list = copyed_list;
        };
        // 对象粘贴
        manager.on_paste = function(e) {
            if ( this.copyed_list.length === 0 ) return;

            e.shiftKey = true;
            for ( var i = 0; i < this.copyed_list.length; i ++ ) {
                var object = this.copyed_list[i];
                this.objects[object.id] = object;
            }
            this.copyed_list = new Array();

            this.renderALL();
        };
        // 旋转对象
        manager.on_rotate = function(e, delta_deg) {
            var selected = this.get_selected_objects();
            if ( selected.length == 0 ) return;
            for ( var i = 0; i < selected.length; i ++ ) {
                selected[i].on_rotate(e, delta_deg);
            }
            this.renderALL();
        };
        // 删除对象
        manager.on_delete = function(e) {
            var selected = this.get_selected_objects();
            if ( selected.length == 0 ) return;
            for ( var i = 0; i < selected.length; i ++ ) {
                var realobject = selected[i].on_delete(e);
                delete this.objects[realobject.id];
            }

            this.on_select_nothing(e, "用户删除");
            this.renderALL();
        };
        // 保存对象
        manager.on_save = function() {
            var backup = {};
            var objects = [];
            for ( var idx in this.objects) {
                var object = this.objects[idx];
                var data = object.on_save();
                objects.push(data);
            }
            backup.objects = objects;
            backup.__id_counter__ = this.__id_counter__;
            backup.canvas_background_color = this.canvas_background_color;
            backup.canvas_background_image = this.canvas_background_image;
            backup.canvas_width = this.canvas_width;
            backup.canvas_height = this.canvas_height;
            return backup;
        };
        // 恢复对象
        manager.on_restore = function(data) {
            this.__id_counter__ = data.__id_counter__;
            this.canvas_background_color = data.canvas_background_color;
            this.canvas_background_image = data.canvas_background_image;
            this.canvas_width = data.canvas_width;
            this.canvas_height = data.canvas_height;
            var objects = [];
            var max_id = this.__id_counter__;
            for ( var i = 0; i < data.objects.length; i ++ ) {
                var item = data.objects[i];
                max_id = max_id > item.normal.id ? max_id : item.normal.id;
                switch ( item.normal.type ) {
                    case 'data':
                        var obj = manager.newData(item.normal.left, item.normal.top, item.key, item.txt, item.normal.user_options);
                        obj.on_restore(item);
                        objects.push(obj);
                        break;
                    case 'lable':
                        var obj = manager.newLable(item.normal.left, item.normal.top, item.txt, item.normal.user_options);
                        obj.on_restore(item);
                        objects.push(obj);
                        break;
                    case 'segment':
                        var obj = manager.newSegment(item.fx, item.fy, item.tx, item.ty, item.normal.user_options);
                        obj.on_restore(item);
                        objects.push(obj);
                        break;
                    case 'icon':
                        var obj = manager.newIcon(item.normal.left, item.normal.top, item.src, item.normal.user_options);
                        obj.on_restore(item);
                        objects.push(obj);
                        break;
                    default:
                        console.error("unsupported type", data[i].normal.type);
                        break;
                }
            }

            for ( var i = 0; i < objects.length; i ++ ) {
                this.append(objects[i]);
            }
            this.renderALL();
        };
        //}}

        //{{ 绘制事件
        manager.renderALL = function () {
            // 首先绘制背景
            this.renderBackground();
            // 绘制全部对象
            for ( var idx in this.objects ) {
                this.objects[idx].on_render();
            }
        };
        manager.renderBackground = function () {
            this.ctx.save();
            if ( this.background_image_object_ready == true ) {
                this.ctx.drawImage(this.background_image_object, 0, 0, this.canvas.width, this.canvas.height);
            } else {
                this.ctx.fillStyle = this.canvas_background_color;
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            }
            this.ctx.restore();
        };
        manager.renderLine = function (fx, fy, tx, ty, strokeStyle, lineWidth) {
            this.ctx.save();
            this.ctx.strokeStyle = strokeStyle;
            this.ctx.lineWidth = lineWidth;
            this.ctx.beginPath();
            this.ctx.moveTo(fx, fy);
            this.ctx.lineTo(tx, ty);
            this.ctx.stroke();
            this.ctx.restore();
        };
        manager.renderCircle = function (x, y, radius, fillStyle, strokeStyle, lineWidth) {
            this.ctx.save();
            this.ctx.fillStyle = fillStyle;
            this.ctx.strokeStyle = strokeStyle;
            this.ctx.lineWidth = lineWidth;
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, Math.PI * 2, true);
            this.ctx.stroke();
            this.ctx.fill();
            this.ctx.restore();
        };
        manager.renderText = function (left, top, txt, width, font, fillStyle, textBaseline) {
            this.ctx.save();
            this.ctx.fillStyle = fillStyle;
            this.ctx.font = font;
            this.ctx.textBaseline = textBaseline;
            this.ctx.fillText(txt, left, top, width);
            this.ctx.restore();
        };
        manager.renderImage = function (left, top, width, height, deg, image_object) {
            this.ctx.save();
            if ( deg != 0 ) {
                this.ctx.translate(left + width / 2, top + height / 2);
                this.ctx.rotate(deg * Math.PI / 180);
                this.ctx.translate(0, 0);
                this.ctx.drawImage(image_object, -width/2, -height/2, width, height);
            } else {
                this.ctx.drawImage(image_object, left, top, width, height);
            }
            this.ctx.restore();
        };
        manager.renderFrame = function (begin, path, deg) {
            this.ctx.save();
            this.ctx.strokeStyle = this.select_box_color;
            this.ctx.lineWidth = 1;
            this.ctx.setLineDash([1, 1]);
            this.ctx.beginPath();
            this.ctx.moveTo(begin[0], begin[1]);
            for ( var i = 0; i < path.length; i ++ ) {
                this.ctx.lineTo(path[i][0], path[i][1]);
            }
            this.ctx.stroke();
            this.ctx.restore();
        };
        //}}

        //{{ 编辑支持
        manager.on_StartSegment = function(user_options) {
            this.canvas.style.cursor = 'crosshair';
            this.onclick_capture = function (e) {
                var object = this.newSegment(e.layerX, e.layerY, e.layerX, e.layerY, user_options);
                this.append(object);
                object.end.mousedown_position = object.end.on_get_position();

                this.onmousemove_capture = function (e) {
                    var delta_left = e.layerX - this.mousedown_postion.left;
                    var delta_top = e.layerY - this.mousedown_postion.top;
                    var new_left = object.end.mousedown_position.left + delta_left;
                    var new_top = object.end.mousedown_position.top + delta_top;
                    object.end.on_set_position(new_left, new_top);
                    this.renderALL();
                };
                this.onclick_capture = function (e) {
                    this.canvas.style.cursor = 'default';
                    this.onclick_capture = null;
                    this.onmousemove_capture = null;
                };
            }
        };
        manager.on_StartLable = function(txt, user_options) {
            this.canvas.style.cursor = 'crosshair';
            this.onclick_capture = function (e) {
                var object = this.newLable(e.layerX, e.layerY, txt, user_options);
                this.append(object);
                this.renderALL();
                this.canvas.style.cursor = 'default';
                this.onclick_capture = null;
            };
        };
        manager.on_StartIcon = function(src, user_options) {
            this.canvas.style.cursor = 'crosshair';
            this.onclick_capture = function (e) {
                var object = this.newIcon(e.layerX, e.layerY, src, user_options);
                this.append(object);
                this.renderALL();
                this.canvas.style.cursor = 'default';
                this.onclick_capture = null;
            };
        };
        manager.on_StartData = function(key, defaultvalue, user_options) {
        };
        manager.on_edit_save = function (config) {
            var object = this.get_selected_objects();
            if ( object.length == 1 ) {
                object[0].on_config_save(config);
                this.renderALL();
            }
        };
        //}}
        return manager;
    },
};
