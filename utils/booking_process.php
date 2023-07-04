<?php
header('Content-Type: application/json');

require_once 'Database.php';
require_once 'helper.php';
session_start();
date_default_timezone_set('Asia/Kuala_Lumpur');

$response = [];
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
	echo json_encode($response);
}

function cancel($datetime){
	if(isset($_SESSION['selected_dt'])){
		foreach($datetime as $dt){
			if (($key = array_search($dt, $_SESSION['selected_dt'])) !== false) {
				unset($_SESSION['selected_dt'][$key]);
			}
		}
	}
	$_SESSION['total_hour_selected'] = count($datetime);
}

function select($date){
	if(!isset($_SESSION['selected_dt'])){
		$_SESSION['selected_dt'] = [];
	}
	$_SESSION['selected_dt'] = array_unique(array_merge($_SESSION['selected_dt'],$date));
}

function book($data){
	global $response;
	$db = new Database();
	$current_date = date('Y-m-d H:i');
	if (!isset($_SESSION['booked_maid_id'])) {
		$response = ["func" => "alert",
					"content" => "please select a maid"];
		
		
	} else if (!isset($_SESSION['booked_service_id'])) {
		$response = ["func" => "alert",
					"content" => "please select a service"];
	} else if (!isset($_SESSION['selected_dt'])) {
		$response = ["func" => "alert",
					"content" => "please select a time"];
	}else {
		
		$selectedDates = splitDateTimeList($_SESSION['selected_dt']);
		$booking_time = [];
		foreach ($selectedDates as $datetime) {
			$booking_time[] = get_begin_end($datetime);
		}
		
		foreach($booking_time as $datetime){
			$id = $db -> table('booking') -> insert([
				'service_id' => getSession('booked_service_id'),
				'maid_id' => getSession('booked_maid_id'),
				'member_id' => getSession('member_id'),
				'booking_datetime' => $current_date,
				'booking_status' => 'Pending',
				'booking_arrive_datetime' => $datetime[0],
				'booking_address' => $data['address'],
				'booking_leave_datetime' =>$datetime[1],
			]);
		}
		unset($_SESSION['booked_maid_id']);
		unset($_SESSION['booked_service_id']);
		unset($_SESSION['selected_dt']);
	}
	
}

function splitDateTimeList($datetimeList) {
	sort($datetimeList);

	$result = array();
	$temp = array();

	for ($i = 0; $i < count($datetimeList); $i++) {
		[$date, $time] = explode(' ', $datetimeList[$i]);

		if ($i === 0 || isConsecutive($datetimeList[$i - 1], $datetimeList[$i])) {
			$temp[] = $datetimeList[$i];
		} else {
			$result[] = $temp;
			$temp = array($datetimeList[$i]);
		}

		if ($i === count($datetimeList) - 1) {
			$result[] = $temp;
		}
	}
	return $result;
}

function get_begin_end($datetimelist) {
	$begin = new DateTime($datetimelist[0]);
	if (count($datetimelist) === 1) {
		$end = new DateTime($datetimelist[0]);
	} else {
		$end = new DateTime($datetimelist[count($datetimelist) - 1]);
	}
	$end->modify('+1 hour');
	$end = $end->format('Y-m-d H:i');
	$begin = $begin->format('Y-m-d H:i');
	return array($begin, $end);
}

function isConsecutive($datetime1, $datetime2) {
    $time1 = getTime($datetime1);
    $time2 = getTime($datetime2);

    return $time2->format('G') - $time1->format('G') === 1;
}

function getTime($datetime) {
    [, $time] = explode(' ', $datetime);
    [$hour, $minute] = explode(':', $time);

    $date = new DateTime();
    $date->setTime($hour, $minute);

    return $date;
}



?>



