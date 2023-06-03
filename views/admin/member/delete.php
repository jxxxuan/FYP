<?php
	if (!authenticated(ADMIN_ROLE)) {
		redirect('authentication/sign-in');
	}
	
	$db = new Database();
	
	$db -> table('payment') -> where('member_id',$_GET['id']) -> delete();
	$db -> table('rating') -> where('member_id',$_GET['id']) -> delete();
	$db -> table('favourite_list') -> where('member_id',$_GET['id']) -> delete();
	$db -> table('booking') -> where('member_id',$_GET['id']) -> delete();
	$db -> table('maid') -> where('member_id',$_GET['id']) -> delete();
	$db -> table('member') -> where('member_id',$_GET['id']) -> delete();
	
	if ($result) {
        setFlash('message', 'Successfully deleted');
    }
	redirect('admin/manage?table=member');
?>