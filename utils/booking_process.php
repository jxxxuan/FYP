<?php
require_once 'Database.php';
require_once 'helper.php';
session_start();
date_default_timezone_set('Asia/Kuala_Lumpur');

if (isPostMethod()){
	$db = new Database();
	$current_date = date('Y-m-d H:i');
	if (!isset($_POST['booked_maid_id'])) {
		echo '<script>
			alert("Please select a maid");
			window.location.href = "../member/booking";
			</script>';
	}else if (!isset($_POST['booked_service_id'])) {
		echo '<script>
			alert("Please select a service package");
			window.location.href = "../member/booking";
			</script>';
	}else if(!isset($_POST['booking_arrive_time'])|| !isset($_POST['booking_leave_time'])){
		echo '<script>
			alert("Please select a time");
			window.location.href = "../member/booking";
			</script>';
	}else{
		$id = $db -> table('booking') -> insert([
			'service_id' => $_POST['booked_service_id'],
			'maid_id' => $_POST['booked_maid_id'],
			'member_id' => getSession('member_id'),
			'booking_datetime' => $current_date,
			'booking_status' => 'Pending',
			'booking_arrive_datetime' => $_POST['booking_date'].' '.$_POST['booking_arrive_time'],
			'booking_address' => $_POST['address'],
			'booking_leave_datetime' => $_POST['booking_date'].' '.$_POST['booking_leave_time']
		]);
		unset($_SESSION['booked_maid_id']);
		unset($_SESSION['booked_service_id']);
		redirect('member/view_bookings');
	}
}
?>



