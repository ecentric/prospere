/*
    Plugin for represent notifications
    There are two types of notifications: 
        1. New Comment, action_type = 'AC'
        2. New document, action_type = 'AD'
    Format of server response for get_notification_url
    {
      "notifications": [
        {
          "action": "\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435", 
          "action_type": "AC", 
          "id": 54, 
          "link": [
            "/user/nick/"
          ], 
          "object_id": 210, 
          "text": "asdf asdf ", 
          "username": "nick"
        }
      ], 
      "success": "True"
    }

*/

/* Find Comment tree and callback */
$.find_comment_tree = function(options, callback) {
    options = $.extend({
        interval : 100,
        count : 10,
        comment_tree : document.comment_tree
    }, options);
    var count_checks = 0;
    var interval_id = setInterval(get_comment_tree, options.interval);
    function get_comment_tree() {
        count_checks += 1;
        if (options.comment_tree != undefined) {
            clearInterval(interval_id);
            callback(options.comment_tree);
        }
        if (count_checks > options.count - 1)
            clearInterval(interval_id);
    }
}

$.fn.notification = function(options) {

    options = $.extend({
        // Styles
        notif_style : {
            /* background 3d3d3d dcdcdc*/
            'background-color' : '#dcdcdc',
            'width' : '202px',
            'margin' : '0 auto 0 auto',
            'margin-bottom' : '5px',
            'color' : '#1e1e1e',/*#e5e5e5*/
            'text-align' : 'left', 'font' : 'normal 17px Times New Roman, serif', 'overflow' : 'hidden',
            '-webkit-border-radius' : '3px', '-moz-border-radius' : '3px', 'border-radius' : '3px'
        },
        notif_content_style : {
            'width' : '180px',
            'padding' : '5px', 
            'padding-left' : '10px'
        },
        username_style : { 'color' : '#2b5a17', 'cursor' : 'default' },
        notif_top_style : {
            'width' : '160px', 'overflow' : 'hidden',
            'float' : 'left'
        },
        delete_notif_style : {
            'background' : 'transparent url(/static/images/delete_notif.png)', 
            'background-position' : '0px 0px',
            'width' : '10px', 'height' : '10px', 'float' : 'right', 'cursor' : 'pointer',
            'margin-top' : '4px'
        },
        delete_notif_style_hover : {
            'background-position' : '-10px 0px'
        },
        notif_a_style : {
            'font' : 'normal 1.0em Times New Roman, serif', 'display' : 'block', 'color' : '#1e1e1e',
            'overflow' : 'hidden', 'clear' : 'both', 'padding' : '0px'
        },
        notif_a_style_hover : { 'background' : 'transparent' },


        get_notifications_url : '',
        delete_notification_url : '',
        delete_notifications : true,
        csrf : null,
        self : this
    }, options);
    // Already deleted notifications
    var deleted_notif = new Array();
    // comment tree object
    var comment_tree;
    // main function
    $(function(){
        $.ajaxSetup({cache: false}); 
        $.get(options.get_notifications_url, {}, function(data){
                if (data.success){
                    options.notifications = data.notifications;
                    render();
                }
            }
        );
    });
    function get_notification(field, value) {
        for(var i = 0; i < options.notifications.length; i++)
            if (options.notifications[i][field] == value) return options.notifications[i];
        return false;
    }
    function html_notif_id(id) { 
        return 'notif_' + String(id);
    }
    function render() {
        for (var i = 0; i < options.notifications.length; i++){
            var notif = options.notifications[i];
            if (!check_notification(notif)) continue;

            var html_notif = $('<div id="' + html_notif_id(notif.id) + '"></div>').css(options.notif_style);
            html_notif.hover(function(){ $(this).css({'background-color' : '#bfbfbf'}) },
                function(){ $(this).css({'background-color' : '#dcdcdc'}) })
            var content = $('<div></div>').css(options.notif_content_style);
            html_notif.append(content);

            var top_part = $('<div></div>').css(options.notif_top_style);
            content.append(top_part);
            top_part.append('<span style="' + map2HtmlStyle(options.username_style) + '">' + notif.username + '</span>');
            top_part.append('<span style="cursor: default;"> - ' + notif.action + '</span>');

            content.append($('<div style="' + map2HtmlStyle(options.delete_notif_style) + '" title="Удалить"></div>')
                .hover( function(){$(this).css(options.delete_notif_style_hover);}, 
                        function(){$(this).css(options.delete_notif_style);})
                .click({ 'id' : notif.id }, delete_clicked ) );
            var link = $('<a href="' + notif.link + '" style="' + map2HtmlStyle(options.notif_a_style) 
                         + '" title="Просмотреть">' + notif.text + '</a>').hover(
                            function(){$(this).css(options.notif_a_style_hover); });
            link.click({ 'notif' : notif }, a_clicked);
            content.append(link);
            options.self.append(html_notif);
        }
        $.find_comment_tree({}, check_comment_notifications);
        options.self.show(100);
    }
    // Check if notif is document notif and notif link is current url than delete notif.
    function check_notification(notif) {
        var url = document.location.pathname;
        if (url == notif.link && notif.action_type == 'AD') {
            delete_notification(notif.id);
            return false;
        }
        return true;
    }
    // Check notifications after getting comment_tree pointer
    function check_comment_notifications(tree) {
        var first_notif = null;
        var url = document.location.pathname;
        comment_tree = tree;
        for (var i = 0; i < options.notifications.length; i++) {
            var notif = options.notifications[i];
            if (url == notif.link && notif.action_type == 'AC') {
                if (first_notif == null) first_notif = notif;
                comment_tree.set_comment_as_new(notif.object_id, function(id){
                    delete_notification(get_notification('object_id', id).id);
                });
            }
        }
        if (first_notif != null)
            scroll_to_comment(first_notif);
    }
    function scroll_to_comment(notif) {
        if (comment_tree != undefined) 
            comment_tree.scroll_to(notif.object_id);
    }
    // handlers
    function a_clicked(event) {
        var url = document.location.pathname;
        var notif = event.data.notif;
        if (url == notif.link) {
            if (notif.action_type == 'AC')
                scroll_to_comment(notif);
            return false;
        }
    }
    function delete_clicked(event) {
        if (comment_tree != undefined) 
            comment_tree.set_comment_as_old(get_notification('id', event.data.id).object_id);
        delete_notification(event.data.id);
    }
    // ajax query
    function delete_notification(id) {
        for (var i = 0; i < deleted_notif.length; i++ )
            if (id == deleted_notif[i] ) return;
        deleted_notif.push(id);
        $.post(options.delete_notification_url, { 'csrfmiddlewaretoken' : options.csrf, 'id' : id }, 
            function(data){
                if (data.success){
                    for(var i = 0; i < options.notifications.length; i++)
                        if (id == options.notifications[i].id) {
                            options.notifications.splice(i, 1);
                            break;
                        }
                    $('#' + html_notif_id(id)).remove();
                }
            }
        ).error(function(){is_blocked = false;});
    }
    
    // Utils
    function map2HtmlStyle(map) {
        var s = '';
        for(var k in map) s += k + ' : ' + map[k] + ';';
        return s;        
    }
    var tagsToReplace = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;'
    };

    function replaceTag(tag) { return tagsToReplace[tag] || tag; }

    function safe_tags_replace(str) { return str.replace(/[&<>]/g, replaceTag); }

    function sel2id(str){ return str.slice(1); }
}
