<?php
	function expandDateTimeRange($startDateTime, $endDateTime) {
		$expandedRange = array();
		$currentDateTime = strtotime($startDateTime);
		while ($currentDateTime < strtotime($endDateTime)) {
			$expandedRange[] = date('Y-m-d H', $currentDateTime);
			$currentDateTime = strtotime('+1 hour', $currentDateTime);
		}
		return $expandedRange;
	}

	date_default_timezone_set('Asia/Kuala_Lumpur');
	if(isset($_GET['view_date'])){
		$view_date = $_GET['view_date'];
	}else{
		$view_date = date('Y-m-d H:i');
	}
	$current_date = date('Y-m-d H:i');
	if(isset($_GET['id'])){
		$maid_id = $_GET['id'];
	}else{
		echo 'no maid id';
	}
	
	$mode = 'edit';
	if(isset($_GET['mode'])){
		if($_GET['mode'] == 'view'){
			$mode = 'view';
		}
	}
	
	$db = new Database();
	$pending_booking = $db->table('booking')->where('maid_id',$maid_id) -> where('booking_status','Pending')->rows();
	$accepted_booking = $db->table('booking')->where('maid_id',$maid_id) -> where('booking_status','Confirm')->rows();
	$working_booking = $db->table('booking')->where('maid_id',$maid_id) -> where('booking_status','Working')->rows();
	$bookings = array_merge($accepted_booking,$working_booking,$pending_booking);
	$booked_time = array();
	
	foreach ($bookings as $booking) {
		if(strtotime($booking['booking_arrive_datetime']) > strtotime($current_date)){
			$booked_start_time = strtotime($booking['booking_arrive_datetime']);
			$booked_end_time = strtotime($booking['booking_leave_datetime']);
			$expandedRange = expandDateTimeRange($booking['booking_arrive_datetime'], $booking['booking_leave_datetime']);
			$booked_time = array_merge($booked_time, $expandedRange);
		}
	}
?>
<h2>Time Slots</h2>
<button onclick='previous_week("<?php echo $view_date; ?>")'><<<<<</button>
<button onclick='next_week("<?php echo $view_date; ?>")'>>>>>></button>

<table class="time-slot-table">
	
	<?php
		// Get the current week's start and end date
		$view_week_start = strtotime('monday this week', strtotime($view_date));
		$view_week_end = strtotime('sunday this week', strtotime($view_date));
	?>

	<thead>
		<tr>
			<th>Time</th>
			<th>Monday <?php echo '<br>' . date('Y-m-d', $view_week_start); ?></th>
			<th>Tuesday <?php echo '<br>' . date('Y-m-d', strtotime('+1 day', $view_week_start)); ?></th>
			<th>Wednesday <?php echo '<br>' . date('Y-m-d', strtotime('+2 days', $view_week_start)); ?></th>
			<th>Thursday <?php echo '<br>' . date('Y-m-d', strtotime('+3 days', $view_week_start)); ?></th>
			<th>Friday <?php echo '<br>' . date('Y-m-d', strtotime('+4 days', $view_week_start)); ?></th>
			<th>Saturday <?php echo '<br>' . date('Y-m-d', strtotime('+5 days', $view_week_start)); ?></th>
			<th>Sunday <?php echo '<br>' . date('Y-m-d', strtotime('+6 days', $view_week_start)); ?></th>
		</tr>
	</thead>
	<tbody>
		<?php
			for ($i = strtotime('8:00'); $i <= strtotime('18:00'); $i += 3600) {
				echo "<tr>";
				echo "<td>" . date('H:i', $i) . "</td>";
				for ($days = $view_week_start; $days <= $view_week_end; $days = strtotime('+1 day', $days)) {
					$dayDate = date('Y-m-d', $days);
					$dateTime = strtotime($dayDate . ' ' . date('H:i', $i));
					$buttonClass = '';
					
					if (in_array(date('Y-m-d H',$dateTime), $booked_time)) {
						$buttonClass = 'not-available';
					}else if(strtotime(date('Y-m-d H:i',$dateTime)) < strtotime($current_date)){
						$buttonClass = 'passed';
					}else if(isset($_SESSION['selected_dt']) && in_array(date('Y-m-d H:i',$dateTime),$_SESSION['selected_dt'])){
						$buttonClass = 'selected';
					}else{
						$buttonClass = 'available';
					}
					
					if($mode == 'view'){
						//echo "<td><button type='button' class='button time-slot-button $buttonClass'></td>";
						echo "<td class='$buttonClass'></td>";
					}else{
						echo "<td><button type='button' class='button full-width-button $buttonClass' onclick='select(this)'></button></td>";
					}
				}
				echo "</tr>";
			}
		?>
	</tbody>
</table>

<script src=<?php echo route('utils/booking.js')?>></script>