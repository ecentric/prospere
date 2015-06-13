/*
 * jquery.uploadProgress
 *
 */
$(document).ready(function(){ 	
    $(function(){
        $.extend($.fn, {
            progressbar: function(handler) { 
                $(this).each( function() { 
                    if(handler < 1) handler = handler * 100;                   
                    var colbaWidth = $('#progressbar').width();
                    var statusWidth = colbaWidth * handler / 100;
                    $(this).css({
                        'width': statusWidth+'px',
                        'font-size': '5pt',
                        'border-width': '1px',
                        'float':'left'
                    })              
                });
                return $(this);
        	}
        });       
    });	
});	
(function($) {
  $.fn.uploadProgress = function(options) {
	options = $.extend({
		interval: 1000,
        progressBar: '#indicator',
        progressBarContainer: '#progressbar',
	    progressUrl: '/upload/progress/',
        validation: function() {return true},
		start: function() {},
		uploading: function() {},
		complete: function() {},
		success: function() {},
		error: function() {},
		uploadProgressPath: "/static/js/jquery.uploadProgress.js",
		jqueryPath: "/static/js/jquery.mini.js",
        timer: ""
	}, options);


	$(function() {

		/* tried to add iframe after submit (to not always load it) but it won't work. 
		safari can't get scripts properly while submitting files */
		if($.browser.safari && top.document == document) {
			/* iframe to send ajax requests in safari 
			   thanks to Michele Finotto for idea */
			iframe = document.createElement('iframe');
			iframe.name = "progressFrame";
			$(iframe).css({width: '0', height: '0', position: 'absolute', top: '-3000px'});
			document.body.appendChild(iframe);
			
			var d = iframe.contentWindow.document;
			d.open();
			/* weird - safari won't load scripts without this lines... */
			d.write('<html><head></head><body></body></html>');
			d.close();
			
			var b = d.body;
			var s = d.createElement('script');
			s.src = options.jqueryPath;
			// must be sure that jquery is loaded 
			s.onload = function() {
				var s1 = d.createElement('script');
				s1.src = options.uploadProgressPath;
				b.appendChild(s1);
			}
			b.appendChild(s);
		}
	});
  
	return this.each(function(){
		$(this).bind('submit', function() {
			var uuid = "";
			for (i = 0; i < 32; i++) { uuid += Math.floor(Math.random() * 16).toString(16); }
			
            /* update uuid */
            options.uuid = uuid;
			/* start callback */
            if (!options.validation()) return false;
			options.start();

			/* patch the form-action tag to include the progress-id 
                           if X-Progress-ID has been already added just replace it */
            if(old_id = /X-Progress-ID=([^&]+)/.exec($(this).attr("action"))) {
                var action = $(this).attr("action").replace(old_id[1], uuid);
                $(this).attr("action", action);
            } else {
                var sptr;
                if($(this).attr("action").search(/\/\?/)==-1) sptr = "?"; else sptr = "&";
			    $(this).attr("action", jQuery(this).attr("action") + sptr + "X-Progress-ID=" + uuid);
			}
			var uploadProgress = $.browser.safari ? progressFrame.jQuery.uploadProgress : jQuery.uploadProgress;
			options.timer = setInterval(function() { uploadProgress(this, window, options); }, options.interval);
		});
	});

  };
    jQuery.uploadProgress = function(e, wind, options) {
	    var xhr = jQuery.ajax({
		    type: "GET",
		    url: options.progressUrl,
		    dataType: "json",
		    beforeSend: function(xhr) {
			    xhr.setRequestHeader("X-Progress-ID", options.uuid);
		    },
		    success: function(upload) {
			    if (upload.state == 'uploading') {
                    options.upload_started = true;
                    if(upload.received > upload.size) upload.received = upload.size;
				    upload.percents = Math.floor((upload.received / upload.size)*1000)/10;
			      	options.uploading(upload);
			    }
			    if (upload.state == 'done' || upload.state == 'error') {
				    e.clearInterval(options.timer);
				    options.complete(upload);
			    }
			    if (upload.state == 'done') {
				    options.success(upload);
			    }
			    if (upload.state == 'error') {
                    if (upload.status == 302 && !options.upload_started) {
                        if(navigator.appName == "Microsoft Internet Explorer"){
                            wind.document.execCommand('Stop');
                        } else {
                            wind.stop();
                        }
				        options.error(upload);
                    }
   			    }
		    },
            error: function(jqXHR, textStatus, errorThrown) {
		    }
	    });
    };

})(jQuery);
