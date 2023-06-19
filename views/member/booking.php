<?php
	if(isPostMethod()) {
		foreach($_POST as $key => $value){
			setSession([$key => $value]);
		}
	}
	$db = new Database();
	
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
	
?>
<form method="post">
	<div class='container'>
		<div class='box'>
			<h2>Service Plan</h2>
			<?php 
				if (!isset($_SESSION['service_id'])):
			?>
					<a type='button' href='<?php echo route("service/service_explorer");?>' class='button booking-button'>choose a service package</a>
			
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
		</div>
		
		<div class='box'>
		<h2>Maid</h2>
		<?php 
			if (!isset($_SESSION['maid_id'])):
		?>
				<a type='button' href='<?php echo route("member/maid_explorer");?>' class='button booking-button'>choose a maid</a>
		
		<?php 
			else:
				$maid = $db->table('maid')->where('maid_id',$_SESSION['maid_id'])->row();
				$member = $db->table('member')->where('member_id',$maid['member_id'])->row();
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
							<td><?php echo $member['member_name'];?></td>
							<td><?php echo $maid['maid_age'];?></td>
							<td><?php echo $maid['maid_gender'];?></td>
							<td><?php echo $member['member_contact'];?></td>
							<td><?php echo $maid['maid_skill'];?></td>
						</tr>
					</tbody>
				</table>
				
				<section>
					
					<?php
						$_GET['id'] = $maid['maid_id'];
						//$_GET['mode'] = 'view';
						require_once getView('maid.time_slot');
					?>
				</section>
		<?php
			endif;
		?>
		</div>
		
		<textarea class='box text-box' type='text' name='address' placeholder='address'></textarea>
	</div>
	
	<div class='booking-section'>
		<button type='button' class="booking-button button" onclick='confirm_booking()'>CONFIRM BOOKING</button>
	</div>
	
</form>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="<?php echo route('utils/booking.js');?>"></script>