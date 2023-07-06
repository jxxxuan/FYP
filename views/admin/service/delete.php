<?php
	if (!authenticated(ADMIN_ROLE)) {
		redirect('authentication/sign-in');
	}

	$db = new Database();
	
	$result1 = $db->table('service')->where('service_id', $_GET['id'])->delete();
	$result2 = $db->table('booking')->where('service_id', $_GET['id'])->delete();
	
	if($result1 && $result1){
		setFlash('message', 'Service successfully deleted');
	}else{
		setFlash('message', 'Service unsuccessfully deleted');
	}
	redirect('admin/manage?table=service');

?>
