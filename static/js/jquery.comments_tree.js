/*
    build tree - function that allow create DOM tree
    heap consist of object that must contain follow fields parent_id , id , depth( since 0 )

    options : 
        heap : couple of objects
        callback_draw_node : is function, that calls when node must be draw.
                             params : node object from the heap with selectors
*/
var tagsToReplace = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;'
};

function replaceTag(tag) {
    return tagsToReplace[tag] || tag;
}

function safe_tags_replace(str) {
    return str.replace(/[&<>]/g, replaceTag);
}

function sel2id(str){
    return str.slice(1);
}
function trim(str) {
    var new_str = "";
    var count_beside = 0;
    var begin = 0;
    for (begin = 0; begin < str.length && str.charAt(begin) == '\n'; begin++){}

    for (var end = str.length - 1; end >= 0 && begin < end && str.charAt(end) == '\n'; end--){}
    
    str = str.slice(begin, end + 1);
    for (var i = 0; i < str.length; i++) {
        if (str.charAt(i) == '\n') {
            count_beside += 1;
            if (count_beside > 2) continue;
        }
        else count_beside = 0;
        new_str += str.charAt(i);
    }
    return new_str;
}

$.fn.build_tree = function(options) {    
    options = $.extend({
        content_class : 'content',
        container_class : 'container',
        root_container_class : 'root_container',
        callback_draw_node : function(node){},
        obj : this,
        heap : null
	}, options);
    var indentifier = this.selector;
    // external functions
    this.nodes = options.heap;

    function get_node(field, id) {
        for(var i = 0; i < options.heap.length; i++)
            if (options.heap[i][field] == id) return options.heap[i];
        return false;
    }

    this.get_node_by_id =function(id){
        return get_node('id', id);
    };
    function add_node_to_heap(node) {
        node = calc_node_selectors(node);
        node.has_nested = false;
        get_node('id', node.parent_id).has_nested = true;
        options.heap.push(node);
    }
    this.append_node = function(node) {
        add_node_to_heap(node);
        $(node.parent_container_selector).append(get_node_html(node));
        options.callback_draw_node(node);
    };
    this.prepend_node = function(node) {
        add_node_to_heap(node);
        $(node.parent_container_selector).prepend(get_node_html(node));
        options.callback_draw_node(node);
    };

    function calc_node_selectors(node){
        node.selector = indentifier + '_node_' + node.id;
        node.li_id = node.selector.slice(1);
        node.content_selector = indentifier + '_content_' + node.id;
        node.content_id = node.content_selector.slice(1);
        node.container_selector = indentifier + '_container_' + node.id;
        node.container_id = node.container_selector.slice(1);
        if (! node.parent_id){
            node.parent_selector = indentifier + '_node_root';
            node.parent_container_selector = indentifier + '_container_root';
        } else {
            node.parent_selector = indentifier + '_node_' + node.parent_id;
            node.parent_container_selector = indentifier + '_container_' + node.parent_id;
        }
        return node;
    }
    
    function parse_heap(){
        var i=0;
        for (i=0;i<options.heap.length;i++){
            options.heap[i] = calc_node_selectors(options.heap[i]);
            options.heap[i].has_nested = false;
        }
    }

    function get_node_html(node){
        var li = $('<li></li>')
                .attr({ id : sel2id(node.selector) })
                .addClass();
        li.append('<div class="' + options.content_class+ '" id="'+node.content_id+'"></div>');
        li.append($('<ul class="' + options.container_class + '"></ul>').attr({ id : node.container_id }) );
        return li;
    }
    function render(){
        var i = 0, max_depth = 0, j = 0;
        $(options.obj).html('');

        $(options.obj).append('<ul id="' + indentifier.slice(1) + '_container_root"></ul>')
                      .addClass(options.root_container_class);
        for(i = 0; i < options.heap.length; i++)
            if (max_depth < options.heap[i].depth) max_depth = options.heap[i].depth;
        var depth = 0;
        for(depth = 0; depth <= max_depth; depth++) {
            for(j = 0; j < options.heap.length; j++) {
                if (depth == options.heap[j].depth) {
                    $(options.heap[j].parent_container_selector).append(get_node_html(options.heap[j]));
                    if ( options.heap[j].parent_id ) get_node('id', options.heap[j].parent_id).has_nested = true;
                    options.callback_draw_node(options.heap[j]);
                }
            }
        }
    }
    parse_heap();
    render();
    return this;
};

$.fn.comments_tree = function(options) {
    options = $.extend({
	    get_comments_url : '',
        post_comments_url : '',
        content_class : 'content',
        container_class : 'container',
        root_container_class : 'root_container',
        csrf : null,
        is_authenticated : false,
        obj: this
	}, options);
    //external functions
    this.set_comment_as_old = function(id){
        var node = get_node('id', id);
        $(node.selector).stop().animate({ backgroundColor : '#F2F2EA' }, 800);
        $(node.selector).unbind('hover');
    };
    this.set_comment_as_new = function(id, callback){
        var node = get_node('id', id);
        $(node.selector).css({'background-color' : '#dcdcdc'});
        $(node.selector).hover(function(){
            options.obj.set_comment_as_old(id);
            callback(node.id);
        });
    };
    this.scroll_to = function(id){
        var node = get_node('id', id);
        $('html, body').animate({scrollTop : $(node.selector).offset().top-250}, 300, 'linear');//, callback);
    };
    // 
    var comments_tree, nodes, current_clicked_node;
    var selector_tree;
    // id must be '', dont_has_parent
    var top_node = { id : '', selector : this.selector + '_top', container_selector : this.selector + '_top_container',
content_selector : this.selector + '_top_content' };
    function get_node(field, id) {
        for(var i = 0; i < comments_tree.nodes.length; i++)
            if (comments_tree.nodes[i][field] == id) return comments_tree.nodes[i];
        return false;
    }
    function get_node_index(field, value){
        for(var i = 0; i < comments_tree.nodes.length; i++)
            if (comments_tree.nodes[i][field] == value) return i;
        return false;
    }
    function delete_node_childs(id){
        var index;
        while(! (( index = get_node_index('parent_id', id) ) === false)) {
            delete_node_childs(comments_tree.nodes[index].id);
            $(comments_tree.nodes[index].selector).remove();
            comments_tree.nodes.splice(index,1);
        }
    }
    function delete_node(node){
        var parent = get_node('id', node.parent_id);
        delete_node_childs(node.id);
        $(node.selector).remove();
        var index = get_node_index('id', node.id);
        comments_tree.nodes.splice(index,1);

        parent.has_nested = false;
        for(var i = 0; i < comments_tree.nodes.length; i++)
            if (comments_tree.nodes[i].parent_id == parent.id) { parent.has_nested = true; break; }
    }
	function unblock_page(){$.unblockUI();}
    function block_page(){
        $.blockUI({ message: 'Подождите пожалуйста..', overlayCSS: { opacity: .4 }, 
        css: {  border: 'none', 
                padding: '15px', 
                backgroundColor: '#000', 
                '-webkit-border-radius': '10px', 
                '-moz-border-radius': '10px', 
                'border-radius' : '10px',
                opacity: .7, 
                color: '#fff' } });
    }

    function get_add_comment_form() {
        var form = $('#add_nested_comment_form');
        if (!form.is('form') ) {
            form = $('<form name="add_nested_comment_form" id="add_nested_comment_form" class="comment_form"><fieldset></fieldset></form>');
            form.find('fieldset').append('<label for="comment_text" class="small_text" style="display:block;">Сообщение:</label>');
            form.find('fieldset').append('<textarea id="comment_text"></textarea>');
            form.find('fieldset').append('<input type="submit" class="button" value="сохранить" />');
        }
        return form;
    }
    function hide_form(form, callback) { 
        callback = callback || function(){};
        form.hide(300,function(){form.remove(); callback();}); 
    }
    function show_form(form) {
        form.hide();form.show(300,function(){$('html, body').animate({scrollTop : form.offset().top-250});});
        form.find('textarea').focus();
    }
    function repair_node(node) {
        $('#' + node.comment_text_id).show(100);
    }
    function top_node_click(event){
        event = event || window.event;
        var clicked_elem = event.target || event.srcElement;
        var form = get_add_comment_form();
        if (current_clicked_node == top_node.id) {
            current_clicked_node = null;
            hide_form(form);
        } else {
            form.remove();
            repair_node( get_node('id', current_clicked_node));
            //current_clicked_node = 'top_node';
            current_clicked_node = top_node.id;
            $(top_node.container_selector).append(form);
            form.find('textarea').val('');
            show_form(form);
            form.submit(post_comment);
        }
    }
    function comment_click(event){            
        event = event || window.event;
        var clicked_comment = event.target || event.srcElement;
        var node = get_node('comment_text_id', clicked_comment.id);
        add_reply_comment(node);

    }
    function reply_comment_click(event){
        event = event || window.event;
        var clicked_reply_button = event.target || event.srcElement;
        var node = get_node('reply_comment_id', clicked_reply_button.id); 
        add_reply_comment(node);
    }
    function add_reply_comment(node){
        var form = get_add_comment_form();
        if (current_clicked_node == node.id){
            repair_node(get_node('id', current_clicked_node));
            current_clicked_node = null;
            hide_form(form);
        } else {
            form.remove();
            repair_node( get_node('id', current_clicked_node));
            current_clicked_node = node.id;
            $(node.container_selector).append(form);
            form.find('textarea').val('');
            show_form(form);
            form.submit(post_comment);
        }
    }
    function edit_comment_click(event) {
        event = event || window.event;
        var clicked_edit_button = event.target || event.srcElement;
        var node = get_node('edit_comment_id', clicked_edit_button.id);
        var form = get_add_comment_form();
        if (current_clicked_node == node.id){
            current_clicked_node = null;
            hide_form(form, function(){$('#' + node.comment_text_id).show(200);});
            
        } else {
            form.remove();
            repair_node( get_node('id', current_clicked_node));
            current_clicked_node = node.id;
            $('#' + node.comment_text_id).hide();
            $(node.content_selector).append(form);
            form.find('textarea').val( $("#" + node.comment_text_id).html().split('<br>').join('\n') );
            show_form(form);
            form.submit(edit_comment);
        }
    }
    function delete_comment_click(event) {
        event = event || window.event;
        var clicked_edit_button = event.target || event.srcElement;
        var node = get_node('delete_comment_id', clicked_edit_button.id);
        current_clicked_node = node.id;
        if (confirm("Вы уверены, что хотите удалить?") ) delete_comment(node);
    }

    function draw_comment(node) {
        node.comment_text_id = "comment_text_" + node.id;
        node.edit_comment_id = "edit_comment_button_" + node.id;
        node.reply_comment_id = "reply_comment_button_" + node.id;
        node.delete_comment_id = "delete_comment_button_" + node.id;
        var comment = $('<div class="comment"></div>');
        comment.append('<div class="legend"></div>');
        if (node.picture)
            comment.find(".legend").append('<img src="' + node.picture + '" alt="Картинка пользователя" />');

        comment.find(".legend").append('<div class="username"></div>');
        if (node.user_id)
            comment.find(".legend").find('.username')
                .append('<a href="/user/' + node.username + '/">' + node.username + '</a>');
        else
            comment.find(".legend").find('.username').append(node.username);
        comment.find(".legend").append('<div class="date">' + node.date + '</div>');
        comment.find(".legend").append('<div class="comment_actions"></div>');
        comment.append('<div class="user_text" id="' + node.comment_text_id + '"></div>');
        
        comment.find(".user_text").html(safe_tags_replace(trim(node.text)).split('\n').join('<br />'));
        $(node.content_selector).append(comment); 
        if (options.is_authenticated) comment.find('.user_text').click(comment_click);
    }
    function set_node_actions() {
        if (!options.is_authenticated) return;
        $(".edit_comment_button").remove();
        $(".reply_comment_button").remove();
        $(".delete_comment_button").remove();
        for (var i = 0; i < comments_tree.nodes.length; i++) {
            $(comments_tree.nodes[i].content_selector).find(".comment_actions")
            .append('<div class="reply_comment_button" id="' + comments_tree.nodes[i].reply_comment_id + 
                    '" title="ответить"></div>');
            if ( !comments_tree.nodes[i].has_nested && comments_tree.nodes[i].user_id == options.user_id) {
                $(comments_tree.nodes[i].content_selector).find(".comment_actions")
                .append('<div class="edit_comment_button" id="' + comments_tree.nodes[i].edit_comment_id + 
                        '" title="редактировать"></div>');
            }
            if (options.absolute_permission || 
                    (!comments_tree.nodes[i].has_nested && comments_tree.nodes[i].user_id == options.user_id))
                $(comments_tree.nodes[i].content_selector).find(".comment_actions")
                .append('<div class="delete_comment_button" id="' + comments_tree.nodes[i].delete_comment_id + 
                        '" title="удалить"></div>');
        }
        $(".edit_comment_button").click(edit_comment_click);
        $(".reply_comment_button").click(reply_comment_click);
        $(".delete_comment_button").click(delete_comment_click);
    }

    function post_form(url, callback) {
        var post = {};
        post = $.extend(post, options.post_fields);
        var form = get_add_comment_form();
        post.comment = form.find('textarea').val();
        post.csrfmiddlewaretoken = options.csrf;
        if (!options.is_authenticated) post['name'] = form.find("#name").val();
        post.comment_id = current_clicked_node;
        block_page();
        $.post(url, post, function(data){
                if (data.success){
                    callback(data);
                    unblock_page();
                } else unblock_page();
        }).error(function(){unblock_page();});
    }
    function post_comment() {
        var form = get_add_comment_form();
        if (form.find('textarea').val().length === 0) return false;
        post_form(options.post_comment_url, function(data) {
            var form = get_add_comment_form();
            if (! data.comment.parent_id ) comments_tree.prepend_node(data.comment);
            else comments_tree.append_node(data.comment);
            form.remove();
            current_clicked_node = null;
            set_node_actions();
        });
        return false;
    }
    function edit_comment() {
        var form = get_add_comment_form();
        if (form.find('textarea').val().length === 0 || 
            form.find('textarea').val() == get_node('id', current_clicked_node).text) return false;
        post_form(options.edit_comment_url, function(data) {
            var form = get_add_comment_form();
            var node = get_node('id', current_clicked_node);
            repair_node(node);
            node.text = form.find('textarea').val();
            form.remove();
            $("#"+node.comment_text_id).html(safe_tags_replace(form.find('textarea').val()).split('\n').join('<br>'));
            current_clicked_node = null;
        });
        return false;
    }
    function delete_comment(node){
        post_form(options.delete_comment_url, function(data) {
            var form = get_add_comment_form();
            var node = get_node('id', current_clicked_node);
            delete_node(node);
            set_node_actions();
        });
        return false;
    }
    // main function
    $(function (){
        var comments = $(options.obj.selector);
        if (options.is_authenticated) {
            comments.append('<div id="' + sel2id(top_node.selector) + '"></div>');
            $(top_node.selector).append('<div id="' 
                                        + sel2id(top_node.content_selector) + '">Добавить сообщение</div>');
            $(top_node.selector).append('<div id="' + sel2id(top_node.container_selector) + '"></div>');
            $(top_node.content_selector).click(top_node_click);
        }

        selector_tree = options.obj.selector + '_tree';
        comments.append('<div id="' + selector_tree.slice(1) + '"></div>');
        $(selector_tree).hide();
        $.ajaxSetup({cache: false}); 
        $.get(options.get_comments_url, {}, function(data){
                if (data.success) {
                    comments_tree = $(selector_tree).build_tree({ heap : data.heap_comments, 
                                                                         callback_draw_node : draw_comment });
                    set_node_actions();
                    $(selector_tree).show(200);
                }
            }
        ).error();
    });
    return this; 
};

