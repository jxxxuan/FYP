<?php
	foreach($_GET as $key => $value) {
		setSession([$key => $value]);
	}
	$db = new Database();
	date_default_timezone_set('Asia/Kuala_Lumpur');
	if(isset($_SESSION['current_date'])){
		$current_date = $_SESSION['current_date'];
	}else{
		$current_date = date('Y-m-d H:i');
	}
	
	function expandDateTimeRange($startDateTime, $endDateTime) {
		$expandedRange = array();
		$currentDateTime = strtotime($startDateTime);
		while ($currentDateTime <= strtotime($endDateTime)) {
			$expandedRange[] = date('Y-m-d H', $currentDateTime);
			
			$currentDateTime = strtotime('+1 hour', $currentDateTime);
		}
		return $expandedRange;
	}
	
	function contractDateTimeList($datetimes) {
		$contractedList = array();
		$count = count($datetimes);
		
		if ($count > 0) {
			$contractedList[] = $datetimes[0];
			
			for ($i = 1; $i < $count; $i++) {
				$currentDateTime = strtotime($datetimes[$i]);
				$previousDateTime = strtotime(end($contractedList));
				
				if ($currentDateTime - $previousDateTime > 3600) {
					$contractedList[] = $datetimes[$i];
				}
			}
		}
		return $contractedList;
	}
	function next_week($current_week){
		$current_week = strtotime('+1 week', $current_week);
		
	}
	
	function previous_week($current_week){
		$current_week = strtotime('-1 week', $current_week);
	}
	
	function cancel_booking(){
		unset($_SESSION['maid_id']);
		unset($_SESSION['service_id']);
	}
?>
<div class='container'>
	<h2>Service Plan</h2>
	<?php 
		if (!isset($_SESSION['service_id'])):
	?>
			<a href='<?php echo route("service/service_explorer");?>' class='button booking-button'>choose a service package</a>
	
	<?php 
		else:
			$service = $db->table('service')->where('service_id',$_SESSION['service_id'])->row();
	?>
			<table class='table-container'>
				<thead>
					<tr>
						<th>Title</th>
						<th>Type</th>
						<th>Description</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td><?php echo $service['service_title'];?></td>
						<td><?php echo $service['service_type'];?></td>
						<td><?php echo $service['service_description'];?></td>
					</tr>
				</tbody>
			</table>
	<?php
		endif;
	?>
	
	<h2>Maid</h2>
	<?php 
		if (!isset($_SESSION['maid_id'])):
	?>
			<a href='<?php echo route("member/maid_explorer");?>' class='button booking-button'>choose a maid</a>
	
	<?php 
		else:
			$maid = $db->table('maid')->where('maid_id',$_SESSION['maid_id'])->row();
			$bookings = $db->table('booking')->where('maid_id',$_SESSION['maid_id'])->rows();
			$booked_time = array();
			
			foreach ($bookings as $booking) {
				if(strtotime($booking['booking_arrive_time']) > strtotime($current_date)){
					$booked_start_time = strtotime($booking['booking_arrive_time']);
					$booked_end_time = strtotime($booking['booking_leave_time']);
					$expandedRange = expandDateTimeRange($booking['booking_arrive_time'], $booking['booking_leave_time']);
					$booked_time = array_merge($booked_time, $expandedRange);
				}
			}
	?>
			<table class='table-container'>
				<thead>
					<tr>
						<th>Name</th>
						<th>Age</th>
						<th>Gender</th>
						<th>Contact</th>
						<th>Skill</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td><?php echo $maid['name'];?></td>
						<td><?php echo $maid['age'];?></td>
						<td><?php echo $maid['gender'];?></td>
						<td><?php echo $maid['contact'];?></td>
						<td><?php echo $maid['skill'];?></td>
					</tr>
				</tbody>
			</table>
			
			<section class="box">
				<h2>Time Slots</h2>
				<button src='' onclick='previous_week("<?php echo $current_date; ?>")'>previous</button>
				<button src='' onclick='next_week("<?php echo $current_date; ?>")'>next</button>
    
				
				<table class="time-slot-table">
					
					<?php
						// Get the current week's start and end date
						$current_week_start = strtotime('monday this week', strtotime($current_date));
						$current_week_end = strtotime('sunday this week', strtotime($current_date));
					?>

					<thead>
						<tr>
							<th>Time</th>
							<th>Monday <?php echo '<br>' . date('Y-m-d', $current_week_start); ?></th>
							<th>Tuesday <?php echo '<br>' . date('Y-m-d', strtotime('+1 day', $current_week_start)); ?></th>
							<th>Wednesday <?php echo '<br>' . date('Y-m-d', strtotime('+2 days', $current_week_start)); ?></th>
							<th>Thursday <?php echo '<br>' . date('Y-m-d', strtotime('+3 days', $current_week_start)); ?></th>
							<th>Friday <?php echo '<br>' . date('Y-m-d', strtotime('+4 days', $current_week_start)); ?></th>
							<th>Saturday <?php echo '<br>' . date('Y-m-d', strtotime('+5 days', $current_week_start)); ?></th>
							<th>Sunday <?php echo '<br>' . date('Y-m-d', strtotime('+6 days', $current_week_start)); ?></th>
						</tr>
					</thead>
					<tbody>
						<?php
							for ($i = strtotime('8:00'); $i <= strtotime('18:00'); $i += 3600) {
								echo "<tr>";
								echo "<td>" . date('H:i', $i) . "</td>";
								for ($days = $current_week_start; $days <= $current_week_end; $days = strtotime('+1 day', $days)) {
									$dayDate = date('Y-m-d', $days);
									$dateTime = strtotime($dayDate . ' ' . date('H:i', $i));
									$buttonClass = '';
									
									if (in_array(date('Y-m-d H',$dateTime), $booked_time)) {
										$buttonClass = 'not-available';
									} else if(strtotime(date('Y-m-d H:i',$dateTime)) < strtotime($current_date)){
										$buttonClass = 'passed';
									}
									echo "<td><button class='button time-slot-button $buttonClass' onclick='select(this)'></td>";
								}
								echo "</tr>";
							}
						?>
					</tbody>
				</table>
			</section>
	<?php
		endif;
	?>
	<a href="#" class="booking-button button" onclick='comfirm_booking()'>Confirm Booking</a>
	<a href="#" class="booking-button button" onclick='cancel_booking()'>Cancel Booking</a>
</div>
<script src="<?php echo route('js/booking.js');?>"></script>
