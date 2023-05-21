<?php
	foreach($_GET as $key => $value) {
		setSession([$key => $value]);
	}
	$db = new Database();
	$current_date = date('Y-m-d H:i');
	
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
				<table class="time-slot-table">
					
					<?php
						// Set the timezone to your local timezone
						date_default_timezone_set('Asia/Kuala_Lumpur');

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
	<a href="#" class="booking-button button">Cancel Booking</a>
</div>
<script>
	function select(button) {
		if (check_valid(button)) {
			button.classList.toggle('selected');
		}
	}

	function check_valid(button) {
		if (button.classList.contains('not-available') || button.classList.contains('passed')) {
			// Button is not available
			return false;
		} else {
			// Button is available
			return true;
		}
	}
	/*
	function get_all_selected_date() {
		var selectedButtons = document.querySelectorAll('.time-slot-button.selected');
		var selectedDates = [];

		selectedButtons.forEach(function(button) {
			var dateText = button.getAttribute('data-date');
			selectedDates.push(dateText);
		});
		
		return selectedDates;

	}*/
	function get_all_selected_date() {
		var selectedButtons = document.querySelectorAll('.time-slot-button.selected');
		var selectedDates = [];

		// Get the date text from the <th> elements
		var thElements = document.querySelectorAll('th:not(:first-child)');
		thElements.forEach(function(thElement, index) {
			var dateText = thElement.innerText.trim();
			var button = selectedButtons[index];

			if (button) {
				button.setAttribute('data-date', dateText);
				selectedDates.push(dateText);
			}
		});

		// Get the date text from the first row
		var firstRowButtons = document.querySelectorAll('tbody tr:first-child .time-slot-button');
		firstRowButtons.forEach(function(button) {
			var dateText = button.closest('tr').querySelector('th').innerText.trim();
			button.setAttribute('data-date', dateText);
		});

		return selectedDates;
	}

	
	function splitDateTimeList(datetimeList) {
		datetimeList.sort();

		let result = [];
		let temp = [];

		for (let i = 0; i < datetimeList.length; i++) {
			const [date, time] = datetimeList[i].split(' ');

			if (i === 0 || isConsecutive(datetimeList[i - 1], datetimeList[i])) {
				temp.push(datetimeList[i]);
			} else {
				result.push(temp);
				temp = [datetimeList[i]];
			}

			if (i === datetimeList.length - 1) {
				result.push(temp);
			}
		}
		return result;
	}

	function isConsecutive(datetime1, datetime2) {
		const time1 = getTime(datetime1);
		const time2 = getTime(datetime2);

		return time2.getHours() - time1.getHours() === 1;
	}

	function getTime(datetime) {
		const [, time] = datetime.split(' ');
		const [hour, minute] = time.split(':');

		const date = new Date();
		date.setHours(hour);
		date.setMinutes(minute);

		return date;
	}

	function comfirm_booking(){
		var selectedDates = get_all_selected_date();
		console.log(selectedDates);
		selectedDates = splitDateTimeList(selectedDates);
		console.log(selectedDates);
	}
	

</script>
