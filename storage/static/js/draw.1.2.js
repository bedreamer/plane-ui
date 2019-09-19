// coding: utf8

function MagicValue(name, display_txt, default_value) {
    this.name = name;
    this.display_text = display_txt;
    this.type = typeof default_value;
    return this;
}

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

// Canvas 画笔
function CanvasPainter(user_options) {
    this.id = getOptionValue('id', 'id_default_painter', null, user_options);
    this.canvas = document.getElementById(dom_id);
    this.ctx = this.canvas.getContext('2d');

    this.width = getOptionValue('width', 300, null, user_options);
    this.height = getOptionValue('height', 300, null, user_options);
    return this;
}
