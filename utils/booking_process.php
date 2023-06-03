<?php
header('Content-Type: application/json');

require_once 'Database.php';
$db = new Database();
session_start();
date_default_timezone_set('Asia/Kuala_Lumpur');
$current_date = date('Y-m-d H:i');
		
		
if (!isset($_SESSION['maid_id'])) {
	//echo '<script>if(confirm("Please select a maid")) { window.location.href = "../member/booking"; }</script>';
	exit();
} else if (!isset($_SESSION['service_id'])) {
	//echo '<script>if(confirm("Please select a service")){ window.location.href = "../member/booking"; }</script>';
	exit();
} else {
	$input = file_get_contents('php://input');
	$data = json_decode($input, true);
	$booking_datetime = $data['booking_datetime'];
	$address = $data['address'];
	
	foreach($booking_datetime as $datetime){
		$id = $db -> table('booking') -> insert([
			'service_id' => $_SESSION['service_id'],
			'maid_id' => $_SESSION['maid_id'],
			'member_id' => $_SESSION['id'],
			'booking_date_time' => $current_date,
			'booking_status' => 'pending',
			'booking_arrive_time' => $datetime[0],
			'booking_address' => $address,
			'booking_leave_time' =>$datetime[1],
		]);
		echo $id;
	}
		
	/*
	unset($_SESSION['maid_id']);
	unset($_SESSION['service_id']);
	
	header('Location: ../member/member_booking_status');
	exit();
	*/
}
/*
if ($_POST['confirm'] === 'Confirm Booking') {
	
    
} else {
	
    unset($_SESSION['maid_id']);
    unset($_SESSION['service_id']);
    header('Location: ../member/booking');
    exit();
	
}
*/
?>



