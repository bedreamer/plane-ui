// v1.0

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

// 绘制对象
var Draw = {

    Object: {
        T_CIRCLE: 0, // 圆类型
        T_LINE: 1,　　// 线类型
        T_RECT: 2,   // 矩形类型
        T_TEXT: 3,　　// 文本类型
        T_NODE: 4,   // 连接点
        T_SEGMENT: 5, //线段
        getSupportedTypes: function() {
            return ['circle', 'line', 'rect', 'text', 'node', 'segment'];
        },
        getTypeName: function(type) {
            var types = this.getSupportedTypes();
            return type >= types.length ? 'unsupported':types[type];
        },

        // 对象累计计数器, 用于计算ID
        __object_total_counter: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        __newID: function(type) {
            if ( type >= this.__object_total_counter.length ) {
                console.error("invalid object type,", type);
                return null;
            }

            var prefix = this.getSupportedTypes();
            if ( type >= prefix.length ) {
                console.error("type not supported,", type);
                return null;
            }

            this.__object_total_counter[type] += 1;
            return prefix[type] + '_' + this.__object_total_counter[type].toString();
        },

        // 生成一个对象
        newObject: function (type, left, top, width, height, default_options, user_options) {
            var object = {};
            // 唯一ID
            object.id = this.__newID(type);
            // 对象类型
            object.type = type;
            // 对象类型名
            object.typename = this.getTypeName(type);
            // 魔数
            object.__magic_number_X08stXA9kVd9klaL = true;

            object.left = getOptionValue('left', left, default_options, user_options);
            object.top = getOptionValue('top', top, default_options, user_options);
            object.width = getOptionValue('width', width, default_options, user_options);
            object.height = getOptionValue('height', height, default_options, user_options);
            // 旋转角
            object.rotate = getOptionValue('rotate', 0, default_options, user_options);

            // 填充色
            object.color = getOptionValue('color', '#000000', default_options, user_options);
            // 边框颜色
            object.bordercolor = getOptionValue('bordercolor', '#000000', default_options, user_options);
            // 边框宽度
            object.borderwidth = getOptionValue('borderwidth', 0, default_options, user_options);

            // 字体
            object.font_faimly = getOptionValue('font_faimly', 'sans-serif', default_options, user_options);
            object.font_style = getOptionValue('font_style', '', default_options, user_options);
            object.font_size = getOptionValue('font_size', 10, default_options, user_options);

            // 渲染对象
            object.on_render = function (ctx) {};
            // 移动事件
            object.on_move = function(ctx, x, y) {};

            // 判定(x,y)是否在这个对象的范围内
            object.have_coordinary = function (x, y) {return false;};
            // 返回刷新区域
            object.refresh_rect = function () {return [0, 0, 0, 0];};

            // 保存对象, 返回只包含字符串/数字/布尔值的字典对象
            object.save = function () {};
            // 恢复对象
            object.restor = function (param_list) {};

            return object;
        },

        // 生成一个圆
        newCircle: function (x, y, radius, user_options) {
            var default_options = {color: '#ffffff', bordercolor: '#000000', borderwidth: 2};
            var circle = this.newObject(this.T_CIRCLE,　x - radius, y - radius, x + radius, y + radius, default_options, user_options);

            circle.x = x;
            circle.y = y;
            circle.radius = radius;

            // 绘制圆
            circle.on_render = function (ctx) {
                ctx.save();
                ctx.fillStyle = this.color;
                ctx.strokeStyle = this.bordercolor;
                ctx.lineWidth = this.borderwidth;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2, true);
                ctx.fill();
                ctx.stroke();
                ctx.restore();
            };
            // 对象位置移动事件
            circle.on_move = function(ctx, x, y) {
                this.x = x;
                this.y = y;
            };

            // 判定坐标是否在圆的范围内
            circle.have_coordinary = function (x, y) {
                if ( x < this.x - this.radius - this.borderwidth - 3) return false;
                if ( x > this.x + this.radius + this.borderwidth + 3) return false;
                if ( y < this.y - this.radius - this.borderwidth - 3) return false;
                if ( y > this.y + this.radius + this.borderwidth + 3) return false;
                return true;
            };
            // 返回刷新区域
            circle.refresh_rect = function () {
                return [this.x - this.radius - this.borderwidth, this.y - this.radius - this.borderwidth,
                this.radius * 2, this.radius * 2];
            };

            return circle;
        },
        // 生成一条线
        newLine: function (fx, fy, tx, ty, width, user_options) {
            var default_options = {color: '#000000', bordercolor: '#000000', borderwidth: width};
            var line = this.newObject(this.T_LINE,　Math.min(fx, tx), Math.min(fy, ty),
                Math.max(fx, tx), Math.max(fy, ty), default_options, user_options);

            line.fx = fx;
            line.fy = fy;
            line.tx = tx;
            line.ty = ty;
            line.width = width;

            // 绘制线
            line.on_render = function (ctx) {
                ctx.save();

                ctx.fillStyle = this.color;
                ctx.strokeStyle = this.color;
                ctx.lineWidth = this.borderwidth;
                ctx.beginPath();
                ctx.moveTo(this.fx, this.fy);
                ctx.lineTo(this.tx, this.ty);
                ctx.stroke();
                ctx.restore();
            };

            return line;
        },
        // 生成一个连接点
        newNode: function(x, y, user_options) {
            var node = this.newCircle(x, y, 3, user_options);

            // 开始线段列表
            node.segments_begin = new Array();
            // 开始线段列表
            node.segments_end = new Array();

            // 移动事件
            node.on_move = function(ctx, x, y) {
                this.x = x;
                this.y = y;
                for ( var i = 0; i < this.segments_begin.length; i ++ ) {
                    this.segments_begin[i].fx = x;
                    this.segments_begin[i].fy = y;
                }
                for ( var i = 0; i < this.segments_end.length; i ++ ) {
                    this.segments_end[i].tx = x;
                    this.segments_end[i].ty = y;
                }
            };
            node.on_save = function () {
            };
            node.on_restore = function (param_list) {
            };
            return node;
        },
        // 生成一个线段
        newSegment: function(fx, fy, tx, ty, user_options) {
            var default_line_width = 3;
            var segment = this.newLine(fx, fy, tx, ty, default_line_width, user_options);
            var begin = this.newNode(fx, fy);
            var end = this.newNode(tx, ty);

            segment.begin = begin;
            segment.end = end;
            segment.rend_line = segment.on_render;

            // 将线段内容注册到连接点内部,用于事件绑定
            begin.segments_begin.push(segment);
            end.segments_end.push(segment);

            segment.on_render = function (ctx) {
                this.rend_line(ctx);
                this.begin.on_render(ctx);
                this.end.on_render(ctx);
            };

            return segment;
        },
        // 生成一个矩形
        newRect: function (left, top, width, height, options) {
        },
        // 生成一个文本
        newText: function (txt, left, top, user_options) {
            var default_options = {color: '#000000',
                bordercolor: '#000000',
                borderwidth: 0,
                font_size: 10,
                font_style: '',
                font_faimly: 'sans-serif',
            };
            var text = this.newObject(this.T_TEXT,　left, top, this.width, 14, default_options, user_options);
            text.txt = txt;

            text.width = text.txt.length * text.font_size;
            text.height = text.font_size;

            text.font = function() {
                return [this.font_style, this.font_size + 'px', this.font_faimly].join(" ");
            };

            // 绘制线
            text.on_render = function (ctx) {
                ctx.save();
                ctx.fillStyle = this.color;
                ctx.font = this.font();
                console.log(ctx.font);
                ctx.fillText(this.txt, this.left, this.top);
                ctx.restore();
            };
            // 响应移动事件
            text.on_move = function(ctx, x, y) {
                this.left = x;
                this.top = y;
            };

            // 判断坐标是否在字符串内部
            text.have_coordinary = function (x, y) {
                if ( x < this.left - 3) return false;
                if ( x > this.left + this.width + 3) return false;
                if ( y < this.top - this.height/2 - 3) return false;
                if ( y > this.top + this.height/2 + 3) return false;
                return true;
            };

            return text;
        },
    },

    // 对象列表
    __object_list: new Array(),

    // CANVAS 对象
    __canvas__: null,
    // context
    __ctx__: null,
    // 选择的对象列表
    __selected_objects: new Array(),
    // 点击命令栈
    __click_command: new Array(),

    // 绑定CANVAS对象
    bind: function(id, user_options) {
        this.__canvas__ = document.getElementById(id);
        this.__canvas__.width = getOptionValue('width', 500, null, user_options);
        this.__canvas__.height = getOptionValue('height', 500, null, user_options);
        this.__ctx__ = this.__canvas__.getContext('2d');
        this.__canvas__.target = this;

        this.__canvas__.onmousedown = function (e){
            this.target.onmousedown(e);
            this.onmousemove = function (ev) { this.target.onmousemove(ev); }
        };
        this.__canvas__.onmouseup = function (e) {
            this.target.onmouseup(e);
            this.onmousemove = null;
        };
        this.__canvas__.onclick = function (e) { this.target.onclick(e); };
        this.__canvas__.ondblclick = function (e) { this.target.ondblclick(e); };

        return this;
    },

    onmousemove: function(e) {
        for ( var i = 0; i < this.__selected_objects.length; i ++ ) {
            var object = this.__selected_objects[i];
            object.on_move(this.__ctx__, e.layerX, e.layerY);
        }
        this.renderAll();
    },
    onmousedown: function(e) {
        var object = this.objectAt(e.layerX, e.layerY);
        if ( object ) {
            this.__selected_objects.push(object);
        }
    },
    onmouseup: function(e) {
        var objects = this.objectAt(e.layerX, e.layerY);
        this.__selected_objects = new Array();
    },
    onclick: function(e) {
        var objects = this.objectAt(e.layerX, e.layerY);
        if ( this.been_edit ) {
            var new_value = $("#id_been_edit").val();
            if ( new_value === '' ) {
                $("#id_been_edit").focus();
            } else {
                this.been_edit.txt = new_value;
                this.been_edit = null;
                this.renderAll();
                $("#id_float").html('');
            }
        }
    },
    ondblclick: function(e) {
        var objects = this.objectAt(e.layerX, e.layerY);
        if ( objects && objects.typename === 'text') {
            var html = ['<input id="id_been_edit" style="height:',
                objects.height > 15 ? objects.height : 15,
                'px" type="text" value="', objects.txt,
                '" onreturn></div>'].join("");
            $("#id_float").html(html);
            $("#id_float").css("position", "absolute");
            $("#id_float").css("left", objects.left + (e.clientX - e.layerX) + 'px');
            $("#id_float").css("top", objects.top + (e.clientY - e.layerY) - objects.height + 'px');

            $("#id_layer").html(["(", e.layerX, ',', e.layerY, ")"].join(""));
            this.been_edit = objects;
        }
    },

    // 对象事件注册函数
    on: function(event, callback) {

    },

    // 返回处于位置,(x,y)处的对象
    objectAt: function(x, y) {
        for ( idx in this.__object_list ) {
            var object = this.__object_list[idx];
            if ( object.have_coordinary(x, y) === true ) {
                return object;
            }
        }
        return null;
    },

    // 将对象添加到对象列表中
    append: function () {
        for ( var idx in arguments) {
            var objects = arguments[idx];
            if ( objects === null || objects === undefined ) {
                continue;
            }
            if ( objects.__magic_number_X08stXA9kVd9klaL === true ) {
                this.__object_list.push(objects);
            }
        }

        // 重新绘制全部对象
        this.renderAll();
    },

    // 重新绘制全部对象
    renderAll: function () {
        var width = this.__canvas__.width;
        var height = this.__canvas__.height;
        this.__ctx__.clearRect(0, 0, width, height);

        for ( idx in this.__object_list ) {
            var object = this.__object_list[idx];
            object.on_render(this.__ctx__);
        }
    },

    // 开始画线段
    beginSegment: function (user_options) {
        this.__canvas__.style.cursor = 'crosshair';

        // 选开始的点
        this.__canvas__.onmousedown = function (e) {
            var segment = this.target.Object.newSegment(e.layerX, e.layerY, e.layerX, e.layerY, user_options);
            this.target.append(segment.begin);
            this.target.append(segment);
            this.target.append(segment.end);
            this.target.new_segment = segment;
            this.onmousemove = function (e) {
                this.target.new_segment.end.on_move(this.__ctx__, e.layerX, e.layerY);
                this.target.renderAll();
            };
        };

        // 选中结束的点
        this.__canvas__.onmouseup = function (e) {
            this.onmousemove = function (ev) { this.target.onmousemove(ev); };
            this.onmousedown = function (ev) { this.target.onmousedown(ev); };
            this.onmouseup = function (ev) { this.target.onmouseup(ev); };
            this.target.new_segment.end.on_move(this.__ctx__, e.layerX, e.layerY);
            this.target.new_segment = null;
            this.style.cursor = 'default';
        };
    },

    // 开始画标签
    beginLable: function (txt, font) {
        this.__canvas__.style.cursor = 'crosshair';
        this.new_text = txt;
        this.new_text_font = font;
        this.__canvas__.onclick = function (e) {
            var text = draw.Object.newText(this.target.new_text, e.layerX, e.layerY, this.target.new_text_font);
            draw.append(text);
            this.style.cursor = 'default';
            this.onclick = function (e) {this.target.onclick(e);};
            this.target.new_text = this.target.new_text_font = null;
        };
    },

    // 保存对象
    save: function () {
        var data = {
            __object_total_counter: this.__object_total_counter,
            line: new Array(),
            node: new Array(),
        }
    },

    // 恢复对象
    restor: function (param_list) {
    },
};



var draw = null;
$(document).ready(function () {
    draw = Draw.bind('c', {width: 700, height: 600});

    $('#link').click(function () {
        var user_option = {color: $("#id_color").val(), borderwidth: Number($('#id_line_width').val())};
        draw.beginSegment(user_option);
    });

    $('#lable').click(function () {
        var font = {font_size: Number($('#id_font_size').val()), color: $("#id_font_color").val()};
        draw.beginLable("测试标签", font);
    });
});
