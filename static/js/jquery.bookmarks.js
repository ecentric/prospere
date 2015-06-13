$(function(){
	$.fn.bookmark_chock = function(options) {
	    options = $.extend({
	    	chock_caption_selector: null,
            chock_caption_text_selector: null,
	    	chock_selector: null,
	    	chock_substance_selector: null,
            get_bookmarks_url : '',
	    	user_id: null
    	}, options);
    	var is_bookmarks_rendered = false;
        var caption_text;
        function block_caption(){
            caption_text = $(options.chock_caption_text_selector).html();
            $(options.chock_caption_text_selector).html('Загрузка...');
            $(options.chock_caption_selector).unbind('click');
        }
        function unblock_caption(){
            $(options.chock_caption_text_selector).html(caption_text);
            $(options.chock_caption_selector).click(
            	function(){change_chock_state(options.chock_substance_selector);});
        }
    	function change_chock_state(selector){
        	if ($(selector).is(':visible')) $(selector).hide(200);
            else {
            	if (!is_bookmarks_rendered){
                    block_caption();
                    get_user_bookmarks(options.get_bookmarks_url, options.user_id,render);
                    is_bookmarks_rendered = true;
            	}
           		else $(selector).show(200);
        	}
    	}
        $(options.chock_caption_selector).click(
        	function(){change_chock_state(options.chock_substance_selector);});
        
        function render(bookmarks){
            $(options.chock_substance_selector).html('');
        	if (bookmarks.length === 0){
        		$(options.chock_substance_selector).append('<div class="note">Пусто.</div>');
                unblock_caption();
                $(options.chock_substance_selector).show(200);
        		return;
        	}

            var i;
            for(i = 0; i < bookmarks.length ; i++){
                var bmrk = '<div style="margin-bottom:5px;margin-top:5px;"><img " src="'+bookmarks[i].picture+'" />';
                bmrk += '<a href="/user/'+bookmarks[i].name+'/">'+bookmarks[i].name+'</a><br class="clear" /></div>';
            	$(options.chock_substance_selector).append(bmrk);
            }
            $(options.chock_substance_selector).show(200);
            unblock_caption();
    	}
    };
});

$(function(){
    $.fn.bookmark_autocomplete = function(options){
        options = $.extend({
            get_bookmarks_url : '',
            text_input_selector : '',
            user_id : null,
            user_page : '',
            self : this
    	}, options);

        var bookmarks = null;
        var ac;
        function demand_data(me){
            ac = me;
            get_autocomplete_values(options.user_id, receive_bookmarks);
        }

        function receive_bookmarks(data){
            ac.add_data(data);
            bookmarks = data;
        }
        $(options.text_input_selector).autocompleteArray([],{
            delay:10,
			minChars:1,
			matchSubset:1,
            matchCase : true,
			autoFill:true,
			maxItemsToShow:10,
            width:275,
            selectOnly:false,
            selectFirst:false,
            callback_demand_data:demand_data,
            callback_demand_submit:function submit_form(){$('#go').click();}}
        );

        this.submit(function(){
            var query = $(options.text_input_selector).val();
            if (query.length<3) return false;
            var username = null;
            if (bookmarks) {
                var i;
                for(i = 0;i<bookmarks.length;i++){
                    if (bookmarks[i] == query) {
                        username = query;
                        break;
                    }
                }
                if (username) {
                    window.location = options.user_page.replace('0', username);
                    return false;
                }
            }
            return true;
        });

        var callback_autocomplete = null;
        function get_autocomplete_values(id, callback){
            callback_autocomplete = callback;
            get_user_bookmarks(options.get_bookmarks_url, id, parse_autocomplete_values);
        }
        function parse_autocomplete_values(data){
            var parsed_values = [];
            var i;
            for(i=0;i<data.length;i++)
                parsed_values.push(data[i].name);
            callback_autocomplete(parsed_values);
        }
	};
});

var cashe = new Object();

function get_user_bookmarks(url, id, callback){
    if (cashe[id]) return callback(cashe[id]);
    cashe[id] = [];
    $.ajaxSetup({cache: false}); 
	$.get(url, { id : id }, function(data){
		if (data.success)
		{ 
        	function compare(a,b){
                if (a.name > b.name) return 1;
                return -1;
            }
            data.bookmarks.sort(compare);
            cashe[id] = data.bookmarks;
            callback(data.bookmarks);
		} else delete cashe[id];
	}).error(function(){delete cashe[id];});
}

