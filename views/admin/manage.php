<?php
require_once getView('layout.side-bar');
?>

<div class="text-center page">
<?php
	if(isset($_GET['table'])){
		if($_GET['table'] == 'member'){
			require_once getView('admin.member.view');
		}else if($_GET['table'] == 'maid'){
			require_once getView('admin.maid.view');
		}else if($_GET['table'] == 'service'){
			require_once getView('admin.service.view');
		}else if($_GET['table'] == 'booking'){
			require_once getView('admin.booking.view');
		}else if($_GET['table'] == 'maid_application'){
			require_once getView('admin.maid.process_application');
		}else if($_GET['table'] == 'rating'){
			require_once getView('admin.rating.view');
		}else if($_GET['table'] == 'payment'){
			require_once getView('admin.payment.view');
		}
	}else{
		require_once getView('admin.member.view');
	}
?>
</div>


<script src=<?php echo route("utils/side-bar.js");?>></script>