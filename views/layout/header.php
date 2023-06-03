<?php
$authenticated = authenticated();
$userRole = getSession('user_role');
?>

<script>
    (function($) {
	var namespace = 'blur';
	var methods = {
		init: function(options){
			options = $.extend({
			    'upper':'blur-upper',
			    'contents':'blur-contents',
		        'clone':'blur-contents-clone',
		        'svgBlur':30
	    	}, options);
			return this.each(function(){
			    var _this = this;
			    var $this = $(this);
			    var data = $this.data(namespace);
			    if (!data) {
			        options = $.extend({
			        }, options);
			        $this.data(namespace, {
			        	options: options
			        });

			        $this.append('<svg class="blur-svg"><filter id="blur-svg-filter"><feGaussianBlur stdDeviation="10" /></filter></svg>');

			        methods.clone.apply(_this);

			        $(window).on('scroll',function(){
			            methods.scrollY.apply(_this);
			        });

			    }
			}); // end each
		},

	    clone: function(){
	    	var $this = $(this);
			var options = $this.data(namespace).options;
		    var $cloneWrap = $('<div>').addClass(options.clone);
			var $clone = $('.' + options.contents).clone();

			$cloneWrap.append($clone);
			$('.' + options.upper).append($cloneWrap);
			$('.' + options.clone).css({
			    '-webkit-filter':'blur('+options.svgBlur+'px)',
			    'filter':'url(#blur-svg-filter)'
			});
			$('.blur-svg').css({
			    'position': 'absolute',
		        'top':'0'
		    });
		},

	    scrollY: function(){
	    	var $this = $(this);
			var options = $this.data(namespace).options;
			translation = 'translate3d(0,' + (-$(window).scrollTop() + 'px') + ',0)';
			$('.' + options.clone).css({
			    '-webkit-transform': translation,
			    '-moz-transform': translation,
			    'transform': translation
			});
		},

	    destroy: function(){
	    	return this.each(function(){
			    var $this = $(this);
			    $(window).unbind('.'+namespace);
			    $this.removeData(namespace);
			});
		}
	};

	$.fn.blur = function(method){
		if ( methods[method] ) {
			return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
	    } else if ( typeof method === 'object' || ! method ) {
			return methods.init.apply( this, arguments );
		} else {
			$.error( 'Method ' +  method + ' does not exist on jQuery.'+namespace);
		}
	};

})(jQuery);

    //Call the plugin
    $(document).ready(function() {
        $('.blur').blur();
    });
</script>

<header>
    
	<a href="<?php echo route(''); ?>">
		<img src="<?php echo asset('image\logo.png'); ?>" class ="logo" alt="Maid Logo" />
	</a>
    
    <nav class="navigation"> 
        <a class="nav-link" href="<?php echo route(''); ?>">HOME</a>
        <a class="nav-link" href="<?php echo route('member/maid_explorer'); ?>">MAIDS</a>
		<a class="nav-link" href="<?php echo route('service/service_explorer'); ?>">SERVICES</a>
        <?php if ($authenticated) : ?>
            <?php if ($userRole === ADMIN_ROLE) : ?>
				<a href="<?php echo route('admin/manage'); ?>">
					<img src="<?php echo asset('image/header/default-avatar.svg'); ?>" alt="user" width="36" />
				</a>
            <?php elseif ($userRole === MEMBER_ROLE) : ?>
				<a href="<?php echo route('member/member_profile'); ?>">
					<img src="<?php echo asset('image/header/default-avatar.svg'); ?>" alt="user" width="36" />
				</a>
			<?php elseif ($userRole === MAID_ROLE) : ?>
				<a href="<?php echo route('maid/maid_profile'); ?>">
					<img src="<?php echo asset('image/header/default-avatar.svg'); ?>" alt="user" width="36" />
				</a>
            <?php endif; ?>
        <?php endif; ?>

            <?php if (!($authenticated)) : ?>
                <a class="nav-link" href="<?php echo route('authentication/sign-in'); ?>">SIGN IN</a>
				<a class="nav-link" href="<?php echo route('authentication/sign-up'); ?>">SIGN UP</a>
            <?php endif; ?>
        
    </nav>
</header>