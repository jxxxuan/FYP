<?php
require_once '../../utils/Database.php';

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
	
	if ($_SERVER['REQUEST_METHOD'] === 'POST') {
		echo count($_REQUEST);
		if(!isset($_POST['booking_time'])){
			echo 'sdfc';
			$datetimes = $_POST['booking_time'];
		}
	}
	if(isset($_POST['booking_time'])){
		echo '<script>console.log("asdc")</script>';
		$datetimes = $_POST['booking_time'];
	}
	
	foreach($datetimes as $datetime){
		$db -> table('booking') -> insert([
			'service_id' => $_SESSION['service_id'],
			'maid_id' => $_SESSION['maid_id'],
			'member_id' => $_SESSION['id'],
			'booking_date_time' => $current_date,
			'booking_status' => 'pending',
			'booking_arrive_time' => $datetime[0],
			'booking_addres' => $_POST['address'],
			'booking_leave_time' =>$datetime[1],
		]);
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


