<?php
$db = new Database();
$date = new DateTime();

// Format the datetime object into the MySQL format
$formatted_date = $date->format('Y-m-d H:i:s');

$db -> table('booking') -> insert([
	'service_id'=>1,
	'member_id'=>123,
	'maid_id'=>123,
	'booking_date_time'=>$formatted_date,
	'booking_status'=>'pending',
	'baooking_arrive_time'=>$formatted_date,
	'booking_address'=>'in your heart'
	])
?>