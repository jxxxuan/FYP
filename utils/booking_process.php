<?php
header('Content-Type: application/json');

require_once 'Database.php';
require_once 'helper.php';
session_start();
date_default_timezone_set('Asia/Kuala_Lumpur');

		
if (isPostMethod()){
	$input = file_get_contents('php://input');
	$data = json_decode($input, true);
	
	if($data['func']  == 'cancel'){
		cancel($data['cancel_dt']);
	}else if($data['func']  == 'select'){
		select($data['selected_dt']);
	}else if($data['func']  == 'book'){
		book($data);
	}
	
}
function cancel($datetime){
	if(isset($_SESSION['selected_dt'])){
		foreach($datetime as $dt){
			if (($key = array_search($dt, $_SESSION['selected_dt'])) !== false) {
				unset($_SESSION['selected_dt'][$key]);
			}
		}
	}
}

function select($date){
	if(!isset($_SESSION['selected_dt'])){
		$_SESSION['selected_dt'] = [];
	}
	$_SESSION['selected_dt'] = array_unique(array_merge($_SESSION['selected_dt'],$date));
}

function book($data){
	$db = new Database();
	$current_date = date('Y-m-d H:i');
	if (!isset($_SESSION['maid_id'])) {
		echo '<script>if(confirm("Please select a maid")) { window.location.href = "../member/booking"; }</script>';
		exit();
	} else if (!isset($_SESSION['service_id'])) {
		echo '<script>if(confirm("Please select a service")){ window.location.href = "../member/booking"; }</script>';
		exit();
	} else {
		foreach($data['booking_datetime'] as $datetime){
			$id = $db -> table('booking') -> insert([
				'service_id' => $_SESSION['service_id'],
				'maid_id' => $_SESSION['maid_id'],
				'member_id' => $_SESSION['id'],
				'booking_datetime' => $current_date,
				'booking_status' => 'pending',
				'booking_arrive_datetime' => $datetime[0],
				'booking_address' => $data['address'],
				'booking_leave_datetime' =>$datetime[1],
			]);
			echo $id;
		}
		
		unset($_SESSION['maid_id']);
		unset($_SESSION['service_id']);
		unset($_SESSION['selected_dt']);
		
	}
}
?>



