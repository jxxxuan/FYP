<?php
require_once 'Database.php';
require_once 'helper.php';

if (isPostMethod() && isset($_POST['action'])) {
	$database = new Database();
	$confirm_booking = $database -> table('booking') -> where('booking_status','Confirm') -> rows();
	$confirm_datetime = [];
	if($_POST['action'] == 'Confirm'){
		foreach($confirm_booking as $booking){
			$confirm_datetime = array_merge(expandDateTimeRange($booking['booking_arrive_datetime'],$booking['booking_leave_datetime']),$confirm_datetime);
			
		}
		
		$pending_booking = $database -> table('booking') -> where('booking_id',$_POST['id']) -> row();
		$pending_datetime = expandDateTimeRange($pending_booking['booking_arrive_datetime'],$pending_booking['booking_leave_datetime']);
		
		$reject = 0;
		foreach($pending_datetime as $dt){
			if(in_array($dt,$confirm_datetime)){
				$reject = 1;
				break;
			}
		}
		if($reject){
			echo "<script>alert('you can not accept more than one booking at the same time.')</script>";
			echo "<script>window.history.back();</script>";
		}else{
			$database -> table('booking') -> where('booking_id',$_POST['id']) -> update(['booking_status'=> $_POST['action']]);
			echo "<script>alert('booking has been confirm')</script>";
			echo "<script>window.location.href = '../maid/view_bookings';</script>";
		}
	}else if($_POST['action'] == 'Reject'){
		$database -> table('booking') -> where('booking_id',$_POST['id']) -> update(['booking_status'=> $_POST['action']]);
		echo "<script>alert('booking has been reject')</script>";
		echo "<script>window.location.href = '../maid/view_bookings';</script>";
	}else{
		echo "<script>window.history.back();</script>";
	}
}

function expandDateTimeRange($startDateTime, $endDateTime) {
	$expandedRange = array();
	$currentDateTime = strtotime($startDateTime);
	while ($currentDateTime < strtotime($endDateTime)) {
		$expandedRange[] = date('Y-m-d H', $currentDateTime);
		$currentDateTime = strtotime('+1 hour', $currentDateTime);
	}
	return $expandedRange;
}
function expandDatetimeArray($datetimeArray) {
    $expandedArray = [];

    foreach ($datetimeArray as $index => $datetime) {
        $expandedArray[] = $datetime;

        if (isset($datetimeArray[$index + 1])) {
            $currentDatetime = new DateTime($datetime);
            $nextDatetime = new DateTime($datetimeArray[$index + 1]);

            while ($currentDatetime < $nextDatetime) {
                $currentDatetime->add(new DateInterval('PT1H')); // Add 1 hour to the current datetime
                $expandedArray[] = $currentDatetime->format('Y-m-d H:i:s');
            }
        }
    }

    return $expandedArray;
}
?>