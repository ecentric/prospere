(function($) {
    $.fn.filestyle = function(options) {              
        var settings = {}
        if(options) {
            $.extend(settings, options);
        };            
        return this.each(function() {
            
            var self = this;
            var style = $.extend({
                                "width": settings.imagewidth + "px",
                                "height": settings.imageheight + "px",
                                "background": "url(" + settings.image + ") 0px 0px no-repeat",
                                "overflow": "hidden",
                                "cursor": "pointer"
                            }, options.style)
            var wrapper = $("<div id='filestyle_wrapper'>")
                            .css(style);
        
            $(self).wrap(wrapper);
            $(self).css({
                        "position": "relative",
                        "height": settings.imageheight + "px",
                        "width": settings.width + "px",
                        "display": "inline",
                        "cursor": "pointer",
                        "opacity": "0.0"
                    });

            if ($.browser.mozilla) {
                if (/Win/.test(navigator.platform)) {
                    $(self).css("margin-left", "-142px");                    
                } else {
                    $(self).css("margin-left", "-168px");                    
                };
            } else {
                $(self).css("margin-left", settings.imagewidth - settings.width + "px");                
            };

            $(self).bind("change", function() {
                $('#'+wrapper[0].id).css({"background": "url(" + 
                    settings.image + ") 0px -" + settings.imageheight + "px no-repeat"});
            });
        });
    };
})(jQuery);
