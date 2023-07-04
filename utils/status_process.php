<?php
require_once 'helper.php';
require_once 'Database.php';

$booking_id = $_POST['booking_id'];

if(isPostMethod()){
	
	if($_POST['func'] == 'confirm'){
		update_status($booking_id,'Confirm');
		redirect('maid/booking_status?booking_id='.$booking_id);
	}else if($_POST['func'] == 'working'){
		update_status($booking_id,'Working');
		redirect('maid/booking_status?booking_id='.$booking_id);
	}
	// else if($_POST['func'] == 'payment'){
	// 	update_status($booking_id,'Completed');
	// 	redirect('member/member_pay?booking_id='.$booking_id);
	// }
	else if($_POST['func'] == 'rating'){
		update_status($booking_id,'Rating');
	}
	
}

function update_status($booking_id,$status){
	$db = new Database();
	$db -> table('booking') -> where('booking_id',$booking_id) -> update(['booking_status'=>$status]);
	
}
?>