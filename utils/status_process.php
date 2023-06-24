<?php
require_once 'helper.php';
require_once 'Database.php';

if(isPostMethod()){
	
	if($_POST['func'] == 'working'){
		update_status($_POST['booking_id'],'Working');
	}else if($_POST['func'] == 'payment'){
		update_status($_POST['booking_id'],'Payment');
	}else if($_POST['func'] == 'rating'){
		update_status($_POST['booking_id'],'Rating');
	}
	redirect('member/member_booking_status?booking_id='.$_POST['booking_id']);
}

function update_status($booking_id,$status){
	$db = new Database();
	$db -> table('booking') -> where('booking_id',$booking_id) -> update(['booking_status'=>$status]);
	
}
?>