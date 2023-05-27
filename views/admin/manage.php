<?php
require_once getView('layout.side-bar');
?>
<div class = 'manage-table'>
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
		}else{
			require_once getView('admin.maid_approval_process');
		}
		
	}
?>
</div>






