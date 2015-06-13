/*
    jquery tree
*/
function convert_byte(value){
    var one_mb = 1048576;
    var exp10=Math.pow(10,2);// приводим к правильному множителю
    return (Math.round((value / one_mb)*exp10)/exp10).toString();
}
function hasClass(elem, className) {
    return new RegExp("(^|\\s)"+className+"(\\s|$)").test(elem.className)
}

(function($) {
    $.fn.storage_tree = function(options) {
	    options = $.extend({
		    url_get_tree: '',
            url_change_folder_access: null,
            url_change_document_access: null,
            read_only: true,
            storage_id: null,
            csrf : null,
            url_delete_section : '',
            obj: this
    	}, options);
        options.csrf_hash = options.csrf

        var current_clicked_content, current_node;
        var panel_id = 'node_panel';

    	function unblock_tree(){$(options.freeze_selector).unblock();}
        function block_tree(){
            $(options.freeze_selector).block({ message: 'Подождите пожалуйста...', overlayCSS: { opacity: 0.4,
                    filter:'alpha(opacity=40)', '-moz-opacity': '0.4', '-khtml-opacity': '0.4'}, 
                css: { 
                        border: 'none', 
                        padding: '15px', 
                        backgroundColor: '#000', 
                        '-webkit-border-radius': '10px', 
                        '-moz-border-radius': '10px', 
                        'border-radius' : '10px',
                        opacity: 0.7, filter: 'alpha(opacity=70)', '-moz-opacity': 0.7, '-khtml-opacity': 0.7,
                        color: '#fff' } });
        }

        function get_node(field, val)   {
            for(var i=0;i<options.nodes.length;i++)
                if (options.nodes[i][field] == val) return options.nodes[i];
            return false;
        }
        function get_node_by_content_id(content_id){ return get_node('content_id', content_id); }
        function get_node_by_node_id(node_id){ return get_node('node_id', node_id); }
        function get_node_by_container_id(cont_id){ return get_node('container_id', cont_id); }

        // folders open/close
        function tree_toggle(event) {
            // Open and close folders when user click
            event = event || window.event //event droped
            var clickedElem = event.target || event.srcElement
            if (!hasClass(clickedElem, 'Expand')) {
	            return // клик не там
            }
            // Node, на который кликнули
            var node = clickedElem.parentNode
            if (hasClass(node, 'ExpandLeaf')) {
	            return // клик на листе
            }
            // определить новый класс для узла
            var newClass = hasClass(node, 'ExpandOpen') ? 'ExpandClosed' : 'ExpandOpen'
            // заменить текущий класс на newClass
            // регексп находит отдельно стоящий open|close и меняет на newClass
            var re =  /(^|\s)(ExpandOpen|ExpandClosed)(\s|$)/
            node.className = node.className.replace(re, '$1'+newClass+'$3')
        }
        function open_dir(node){
            var re =  /(^|\s)(ExpandOpen|ExpandClosed)(\s|$)/
            var hnode = window.document.getElementById(node.node_id);
            hnode.className = hnode.className.replace(re, '$1'+'ExpandOpen'+'$3')   
        }
        function check_open_folder(){
            // check anchor and open dir
            var anchor = location.toString().match(/#_(.*)/);
            if (!anchor) return;
            node = get_node_by_node_id(anchor[1])
            if (!node) return;
            while (node.parent_id != 'container_node_0'){
                node = get_node_by_container_id(node.parent_id)
                open_dir(node)
            }
        }

        // onClick handlers
        this.click(function (event) { 
            tree_toggle(event)
        });
        function root_clicked(event){
            if (options.read_only) return;
            event = event || window.event;
            var clicked_content = event.target || event.srcElement;
            if (!$('#'+clicked_content.id).hasClass('Content'))return;

            if ($('#root_content'+' > #node_panel').length == 1){ $('#node_panel').remove(); return;}

            $('#node_panel').remove();
            $('#'+panel_id).html('');
            var panel = '<div style="margin-left:18px;" id="'+panel_id+'"></div>';
            $('#root_content').append(panel);
            $('#'+panel_id).append('<div id="add_folder" title="добавить папку"></div>');
            $('#'+panel_id).append('<br style="clear:both;" />');
            $('#add_folder').click(show_add_root_folder);
        }
        function node_clicked(event){
            event = event || window.event;
            var clicked_content = event.target || event.srcElement;
            
            if (!($('#'+clicked_content.id).hasClass('ContentDir') || $('#'+clicked_content.id).hasClass('ContentLeaf')) )
                return;
            current_clicked_content = clicked_content.id;
            current_node = get_node('content_id', clicked_content.id);
            if (options.read_only){
                if ($('#'+clicked_content.id).hasClass('ContentDir')){
                    var re =  /(^|\s)(ExpandOpen|ExpandClosed)(\s|$)/
                    node = get_node_by_content_id(clicked_content.id)
                    var hnode = window.document.getElementById(node.node_id);
                    var newClass = hasClass(hnode, 'ExpandOpen') ? 'ExpandClosed' : 'ExpandOpen'
                    hnode.className = hnode.className.replace(re, '$1'+newClass+'$3')   
                } else show_document()
            } else {
                if ($('#'+clicked_content.id+' > #node_panel').length == 1){ $('#node_panel').remove(); return;}
                $('#node_panel').remove();
                add_node_panel();
            }
        }
        // panel
        function set_panel_error(content){
            $('#'+panel_id).html('<span id="panel_error" style="font-weight:normal;">'+content+'</span>');
            unblock_tree();
        }
        function add_node_panel(){
            var is_dir = $('#'+current_clicked_content).hasClass('ContentDir');
            var panel = '<div id="'+panel_id+'"></div>';
            $('#'+current_clicked_content).append(panel);
            if (is_dir) show_main_dir_menu(); else show_main_leaf_menu();
        }
        function show_form_folder(value,handler){
            $('#'+panel_id).html('');
            $('#'+panel_id).append('<form><fieldset><input type="text" style="float:left;" value="'+
                value+'" /><div id="save_section"></div></fieldset></form>');
            $("#"+panel_id).find('form').submit(function(){$("#save_section").click(); return false;});
            $("#"+panel_id).find('input').focus();
            $('#save_section').click(handler);
        }
        function show_edit_folder(){
            show_form_folder(get_node_by_content_id(current_clicked_content).name,edit_section);
        }
        function show_add_folder(){
            show_form_folder('',add_internal_section);
        }
        function show_add_root_folder(){
            show_form_folder('',add_root_section);
        }
        function show_main_dir_menu(){
            var node = get_node_by_content_id(current_clicked_content);
            $('#'+panel_id).html('');
            $('#'+panel_id).append('<div id="edit_folder" title="изменить имя"></div>');
            $('#edit_folder').click(show_edit_folder);
            if (node.depth < 5){
                $('#'+panel_id).append('<div id="add_folder" title="добавить папку"></div>');
                $('#add_folder').click(show_add_folder);
            }
            $('#'+panel_id).append('<div id="delete_folder" title="удалить папку"></div>');
            $('#delete_folder').click(delete_section);

            if (node.is_shared){ 
                $('#'+panel_id).append('<div id="hide_folder" title="скрыть папку"></div>'); 
                $('#hide_folder').click(change_folder_access);}
            else {
                parent_node = get_node('id', node.parent);
                if ( !parent_node || parent_node.is_shared) {
                    $('#'+panel_id).append('<div id="share_folder" title="открыть доступ к папке"></div>'); 
                    $('#share_folder').click(change_folder_access); 
                }
            }

            $('#'+panel_id).append('<div id="add_document" title="добавить документ"></div>');
            $('#add_document').click(add_document);
            $('#'+panel_id).append('<br style="clear:both;" />');
        }
        function show_main_leaf_menu(){
            var node = get_node_by_content_id(current_clicked_content);
            $('#'+panel_id).html('');
            $('#'+panel_id).append('<div id="show_document" title="перейти к файлу"></div>');
            $('#show_document').click(show_document);
            $('#'+panel_id).append('<div id="edit_document" title="редактировать файл"></div>');
            $('#edit_document').click(edit_document);
            $('#'+panel_id).append('<div id="delete_document" title="удалить файл"></div>');
            $('#delete_document').click(delete_document);
            if (node.is_shared){ 
                $('#'+panel_id).append('<div id="hide_document" title="скрыть файл"></div>'); 
                $('#hide_document').click(change_document_access);}
            else {
                parent_node = get_node('id', node.parent);
                if (parent_node.is_shared) {
                    $('#'+panel_id).append('<div id="share_document" title="открыть доступ к файлу"></div>'); 
                    $('#share_document').click(change_document_access); 
                }
            }
            $('#'+panel_id).append('<br style="clear:both;" />');
        }
        // render functions
        function render_storage_state(mem_busy) {
            if (options.read_only) return;
            options.mem_busy = mem_busy;
            var mem_free = options.storage_mem_limit - mem_busy;
            $(options.storage_state_selector).html('Свободно ' + convert_byte(mem_free)
                                                   + 'mB из ' + convert_byte(options.storage_mem_limit)+'mB');
            $(options.storage_state_selector).show();
        }
        function calc_id_node(node){
            node.node_id = 'node_'+(node.is_dir ? 'dir_' : 'leaf_') + node.id;
            node.selector = '#' + node.node_id;
            node.content_id = 'content_'+(node.is_dir ? 'dir_' : 'leaf_')+node.id;
            node.content_selector = '#' + node.content_id;
            node.parent_id = 'container_node_' + node.parent;
            node.parent_selector = '#node_dir_' + node.parent;
            if (node.is_dir) node.container_id = 'container_node_'+node.id;

            return node;
        }
        function build_node_html(node){
            var li = $('<li></li>')
                    .attr({ id : node.node_id})
                    .addClass("Node Expand" + (node.is_dir ? 'Closed' : 'Leaf'))
            var suffix = node.is_dir ? 'Dir' : 'Leaf'
            li.append('<div class="Expand"></div>'+
                      '<div class="Content' + suffix 
                            + (!node.is_shared ? ' Hidden'+suffix:'') + '" id="'+node.content_id+'">'+
                      node.name+'</div>')
            if (options.read_only) li.find('#'+node.content_id).addClass('light');
            if (node.is_dir) li.append($('<ul class="Container"></ul>').attr({ id : node.container_id }) )
            return li;
        }
        function render_tree(){
            if (options.nodes.length == 0) { if(!options.read_only) $('#hint').show(); return; }
            else $('#hint').hide();
            nodes = options.nodes;
            /* nodes - unsorter array of nodes
                node -> {name:str, id:int, parent:int, depth:int, is_dir:bool}
            */
            // sort by depth, dir, name and build html elements
            function compare_depth(a,b){
                var c1 = String(a.depth)+(a.is_dir ? 'f' : 'l')+a.name;
                var c2 = String(b.depth)+(b.is_dir ? 'f' : 'l')+b.name;
                if (c1>c2) return 1;
                return -1;
            }
            //calc_id_nodes(nodes);
            nodes.sort(compare_depth)
            var i=0;
            for (i=0;i<nodes.length;i++){
                $('#'+nodes[i].parent_id).append(build_node_html(nodes[i]));
            }
            set_last_nodes();
            $('.ContentLeaf').bind('click',node_clicked);
            $('.ContentDir').bind('click',node_clicked);

            check_open_folder();
        }
        function set_last_nodes(){
            /* find last nodes
                sort parent, dir, name
            */
            function compare_parent(a,b){
                var c1 = String(a.parent)+(a.is_dir ? 'f' : 'l')+a.name
                var c2 = String(b.parent)+(b.is_dir ? 'f' : 'l')+b.name
                if (c1>c2) return 1;
                return -1;
            }
            options.nodes.sort(compare_parent)
            for (i=0;i<options.nodes.length-1;i++){
                if (options.nodes[i].parent != options.nodes[i+1].parent)
                    $('#'+options.nodes[i].node_id).addClass('IsLast');
            } 
            if (options.nodes.length != 0) $("#"+options.nodes[options.nodes.length-1].node_id).addClass('IsLast');
        }

        // Ajax actions and base operations
        function edit_document(){
            var node = get_node_by_content_id(current_clicked_content);
            window.location.hash = '#_'+node.node_id;
            window.location = "/cabinet/edit_document/"+node.id+'/?next='+window.location.pathname+
                              '&node_anchor=_'+get_node_by_content_id(current_clicked_content).node_id;
        }
        function add_document(){
            var node = get_node_by_content_id(current_clicked_content);
            window.location.hash = '#_'+node.node_id;
            window.location = "/cabinet/add_document/"+node.id+'/?next='+window.location.pathname+
                              '&node_anchor=_'+get_node_by_content_id(current_clicked_content).node_id;
        }
        function delete_document(){
            var node = get_node_by_content_id(current_clicked_content);
            if (!confirm("Вы уверены, что хотите удалить?") )return;
            block_tree();
            $.post( options.url_delete_document, { document_id: node.id, csrfmiddlewaretoken : options.csrf_hash},
                function( data ) {
                    if (data.success) {
                        $('#'+node.node_id).remove();
                        var i;
                        for(i=0;i<options.nodes.length;i++)
                            if (node.id == options.nodes[i].id) options.nodes.splice(i,1)
                        set_last_nodes();
                        render_storage_state(options.mem_busy - node.file_size);
                        unblock_tree();
                    } else set_panel_error('Произошла ошибка.');
                }
            ).error(function(){set_panel_error('Произошла ошибка.');});
        }
        function show_document(){
            var node = get_node_by_content_id(current_clicked_content);
            window.location.hash = '#_'+node.node_id;
            window.location = '/document/'+get_node_by_content_id(current_clicked_content).id+'/'
        }
        /* section buttons */
        function add_internal_section(){
            var node = get_node_by_content_id(current_clicked_content);
            add_section(node.id, node.depth+1, node.id);
        }
        function add_root_section(){
            add_section('', 1, 0)
        }
        function add_section(node_id, depth, parent){
            var caption = $('#'+panel_id).find('input').val();
            if (caption.length == 0) return;
            block_tree();
            $.post( options.url_add_section, { owner_section: node_id, storage: options.storage_id, section_caption: caption,
                                               csrfmiddlewaretoken : options.csrf_hash},
                function( data ) {
                    if (data.success) {
                        var new_node = { id : data.id, is_dir : true, name : caption, parent : parent, depth:depth };
                        node = calc_id_node(new_node)
                        options.nodes.push(node)

                        $(options.obj.selector).find('.Container').html('');
                        window.location.hash = '#_'+node.node_id;
                        render_tree();
                        $('#'+panel_id).remove();
                        unblock_tree();
                    }  else set_panel_error('Произошла ошибка.');
                }
            ).error(function(){set_panel_error('Произошла ошибка.');});
        }
        function edit_section(){
            var node = get_node_by_content_id(current_clicked_content);
            var caption = $('#'+panel_id).find('input').val();
            $('#'+panel_id).remove();
            if (caption.length == 0 || caption == $('#'+node.content_id).html()) 
            { add_node_panel(); show_edit_folder(); return;}
            block_tree();
            $.post( options.url_edit_section, { section_id: node.id, section_caption: caption, 
                                                csrfmiddlewaretoken : options.csrf_hash},
                function( data ) {
                    if (data.success) {
                        node.name = caption;
                        $('#'+node.content_id).html(caption);
                        unblock_tree();
                    } else set_panel_error('Произошла ошибка.');
                }
            ).error(function(){set_panel_error('Произошла ошибка.');});
        }
        function delete_section(){
            var node = get_node_by_content_id(current_clicked_content);
            if (!confirm("Вы уверены, что хотите удалить?") )return;
            block_tree();
            $.post( options.url_delete_section, { section_id: node.id, csrfmiddlewaretoken : options.csrf_hash},
                function( data ) {
                    if (data.success) {
                        $('#'+node.node_id).remove();
                        var i;
                        for(i=0;i<options.nodes.length;i++)
                            if (node.id == options.nodes[i].id) options.nodes.splice(i,1)
                        set_last_nodes();
                        unblock_tree();
                    } else set_panel_error('Произошла ошибка. Убедитесь, что папка пуста.');
                }
            ).error(function(){set_panel_error('Произошла ошибка.');});
        }
        function change_access(url, callback) {
            if (!current_node.is_shared) if (!confirm("Сделать доступным всем выбраный объект?") ) return;
            $('#'+panel_id).remove();
            block_tree();
            $.post( url, { id: current_node.id, csrfmiddlewaretoken : options.csrf_hash},
                function( data ) {
                    if (data.success) {
                        callback();
                        unblock_tree();
                    } else set_panel_error('Произошла ошибка.');
                }
            ).error(function(){set_panel_error('Произошла ошибка.');});
        }
        function change_folder_access() {
            change_access(options.url_change_folder_access, function(){
                current_node.is_shared = !current_node.is_shared;
                if (current_node.is_shared) $(current_node.content_selector).removeClass('HiddenDir');
                else { 
                    $(current_node.content_selector).addClass('HiddenDir'); 
                    hide_child_nodes(current_node.selector); 
                }
            });
        }
        function change_document_access() {
            change_access(options.url_change_document_access, function(){
                current_node.is_shared = !current_node.is_shared
                if (current_node.is_shared) $(current_node.content_selector).removeClass('HiddenLeaf');
                else { $(current_node.content_selector).addClass('HiddenLeaf'); hide_child_nodes(current_node.selector)}
            })
        }
        function hide_child_nodes(selector) {
            for (var i = 0; i < options.nodes.length; i++) 
                if (options.nodes[i].parent_selector == selector) {
                    hide_child_nodes(options.nodes[i].selector);
                    if (options.nodes[i].is_dir) $(options.nodes[i].content_selector).addClass('HiddenDir');
                    else $(options.nodes[i].content_selector).addClass('HiddenLeaf');
                    options.nodes[i].is_shared = false;
                }
        }
        function get_tree(url,render_tree) {
            $.ajaxSetup({cache: false}); 
            $(options.freeze_selector).css('height', '70px');
            block_tree();
	        var xhr = jQuery.ajax({
		        type: "GET",
		        url: url,
		        dataType: "json",
		        success: function(data) { 
                    for (i=0;i<data.nodes.length;i++){
                        data.nodes[i] = calc_id_node(data.nodes[i]);
                    }
                    options.nodes = data.nodes;
                    render_tree();
                    render_storage_state(data.mem_busy)
                    unblock_tree();
                    if (options.read_only && data.nodes.length == 0) {
                        $(options.obj.selector).parent().append('<div class="note">Пусто.</div>');
                        $(options.obj.selector).remove();
                    }
                    $(options.freeze_selector).css('height', 'auto');
                },
                error: function(jqXHR, textStatus, errorThrown) {}
	        });
        };
        // main
        $(function(){
            get_tree(options.url_get_tree+'?storage_id='+options.storage_id,render_tree);
            $('#root_content').bind('click',root_clicked);
        });
    };
})(jQuery);
