<?php
	if (!authenticated(ADMIN_ROLE)) {
		redirect('authentication/sign-in');
	}
	
	$db = new Database();
	
	$db -> table('payment') -> where('maid_id',$_GET['id']) -> delete();
	$db -> table('rating') -> where('maid_id',$_GET['id']) -> delete();
	$db -> table('favourite_list') -> where('maid_id',$_GET['id']) -> delete();
	$db -> table('booking') -> where('maid_id',$_GET['id']) -> delete();
	$db -> table('maid') -> where('maid_id',$_GET['id']) -> delete();
	
	if ($result) {
        setFlash('message', 'Successfully deleted');
    }
	redirect('admin/manage?table=maid');
?>