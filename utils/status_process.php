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
	}else if($_POST['func'] == 'payment'){
		$db = new Database();
		$db-> table('payment')-> insert([
            'booking_id' => $booking_id,
            'member_id' => $_POST['member_id'],
            'payment_price' => $_POST['price'],
            'payment_type' => $_POST['type']
        ]);
		
	 	update_status($booking_id,'Completed');
		echo '<script>alert("Payment successful,Thank You!");
		window.location.href = "../member/booking_status?booking_id='.$booking_id.'";</script>';
	}
	else if($_POST['func'] == 'rating'){
		$db = new Database();
		$result = $db ->table('rating')-> insert([
			'member_id' => $_POST['member_id'],
			'maid_id' => $_POST['maid_id'],
			'rating_score' => $_POST['rating'],
			'comment' => $_POST['comment'],
			'booking_id' => $booking_id
		]);

		if($result){
			update_status($booking_id,'Rating');
			echo '<script>alert("Thank You For Your Comment!");
			window.location.href = "../member/booking_status?booking_id='.$booking_id.'";</script>';
		}
	}
	
}

function update_status($booking_id,$status){
	$db = new Database();
	$db -> table('booking') -> where('booking_id',$booking_id) -> update(['booking_status'=>$status]);
	
}
?>