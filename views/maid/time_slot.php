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