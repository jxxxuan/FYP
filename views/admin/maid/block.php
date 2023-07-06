<?php
	if (!authenticated(ADMIN_ROLE)) {
		redirect('authentication/sign-in');
	}
	
	$db = new Database();
	
	
	$maid = $db -> table('maid') -> where('maid_id',$_GET['id']) -> row();
	$member = $db -> table('member') -> where('member_id',$maid['member_id']) -> row();

	if($member['member_status'] == 'Block'){
		$result = $db -> table('member') -> where('member_id',$maid['member_id']) -> update(['member_status'=>'Active']);
		if ($result) {
			setFlash('message', 'Successfully active');
		}
	}else{
		$result = $db -> table('member') -> where('member_id',$maid['member_id']) -> update(['member_status'=>'Block']);
		if ($result) {
			setFlash('message', 'Successfully blocked');
		}
	}
	
	
	redirect('admin/manage?table=maid');
?>