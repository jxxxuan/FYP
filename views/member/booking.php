<?php
	foreach($_GET as $key => $value) {
		setSession([$key => $value]);
	}
	$db = new Database();
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
				$booked_time[] = date("H", strtotime($booking['booking_arrive_time']));
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
				<table class="time-slot-table">
					
					<?php
						// Set the timezone to your local timezone
						date_default_timezone_set('Asia/Kuala_Lumpur');

						$date = '2023-5-30';
						// Get the current week's start and end date
						$current_week_start = strtotime('monday this week',strtotime($date));
						$current_week_end = strtotime('sunday this week',strtotime($date));
					
						// Define the start and end time for the time slots
						$start_time = strtotime('8:00');
						$end_time = strtotime('18:00');
					?>
					<thead>
						<tr>
							<th>Time</th>
							<th>Monday <?php echo '<br>'.date('Y-m-d', strtotime('+0 days',$current_week_start));?></th>
							<th>Tuesday <?php echo '<br>'.date('Y-m-d', strtotime('+1 days',$current_week_start));?></th>
							<th>Wednesday <?php echo '<br>'.date('Y-m-d', strtotime('+2 days',$current_week_start));?></th>
							<th>Thursday <?php echo '<br>'.date('Y-m-d', strtotime('+3 days',$current_week_start));?></th>
							<th>Friday <?php echo '<br>'.date('Y-m-d', strtotime('+4 days',$current_week_start));?></th>
							<th>Saturday <?php echo '<br>'.date('Y-m-d', strtotime('+5 days',$current_week_start));?></th>
							<th>Sunday <?php echo '<br>'.date('Y-m-d', strtotime('+6 days',$current_week_start));?></th>
						</tr>
					</thead>
					<tbody>
					
					<?php
						echo $current_week_start;
						echo $current_week_end;
						/*
						for($days = $current_week_start;$days < $current_week_end;strtotime('+1 days',$current_week_start)){
							
							for ($i = $start_time; $i <= $end_time; $i += 3600) {
								echo "<tr>";
								echo "<td>".date('H:i', $i)."</td>";
								
									if(in_array(date('H', $i),$booked_time)){
										echo "<td><button class='button time-slot-button not-available' onclick='select(this)'>".date('H', $i)."</td>";
									}else{
										echo "<td><button class='button time-slot-button' onclick='select(this)'>".date('H', $i)."</td>";
									}
								
							}
							echo "</tr>";
							
						}*/
					?>
					</tbody>
				</table>
			</section>
	<?php
		endif;
	?>
	<a href="#" class="booking-button button">Confirm Booking</a>
	<a href="#" class="booking-button button">Cancel Booking</a>
</div>
<script>
	function select(button){
		button.classList.toggle('selected');
	}
	function check_valid(button){
		
	}
</script>