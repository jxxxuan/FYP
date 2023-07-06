<?php
	if (!authenticated(ADMIN_ROLE)) {
		redirect('authentication/sign-in');
	}
	
	$db = new Database();
	
	$member = $db -> table('member') -> where('member_id',$_GET['id']) -> row();

	if($member['member_status'] == 'Block'){
		$result = $db -> table('member') -> where('member_id',$_GET['id']) -> update(['member_status'=>'Active']);
		if ($result) {
			setFlash('message', 'Successfully active');
		}
	}else{
		$result = $db -> table('member') -> where('member_id',$_GET['id']) -> update(['member_status'=>'Block']);
		if ($result) {
			setFlash('message', 'Successfully blocked');
		}
	}
	
	
	redirect('admin/manage?table=member');
?>