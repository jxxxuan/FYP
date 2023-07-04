<?php

	if(getSession('user_role') == ADMIN_ROLE || !getSession('loggedin')){
		redirect('authentication/sign-in');
	}

	if(isPostMethod()) {
		foreach($_POST as $key => $value){
			setSession([$key => $value]);
		}
	}
	
	$selected_dt = [];
	if(isset($_SESSION['selected_dt'])){
		$selected_dt = $_SESSION['selected_dt'];
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
	
?>
<form method="post">
	<div class='container'>
		
		
		<div class='box'>
		<h2>Maid</h2>
		<?php 
			if (!isset($_SESSION['booked_maid_id'])):
		?>
				<a type='button' href='<?php echo route("member/maid_explorer");?>' class='button booking-button'>choose a maid</a>
		
		<?php 
			else:
				$maid = $db->table('maid')->where('maid_id',$_SESSION['booked_maid_id'])->row();
				$member = $db->table('member')->where('member_id',$maid['member_id'])->row();
		?>
				<table>
					
					<tbody>
						<tr>
							<td>Member Name:</td>
							<td><?php echo $member['member_name']; ?></td>
						</tr>
						<tr>
							<td>Maid Age:</td>
							<td><?php echo $maid['maid_age']; ?></td>
						</tr>
						<tr>
							<td>Maid Gender:</td>
							<td><?php echo $maid['maid_gender']; ?></td>
						</tr>
						<tr>
							<td>Member Contact:</td>
							<td><?php echo $member['member_contact']; ?></td>
						</tr>
						<tr>
							<td>Maid Skill:</td>
							<td><?php echo $maid['maid_skill']; ?></td>
						</tr>
					</tbody>
				</table>
				
		<?php
			endif;
		?>
		</div>
		
		<div class='box'>
			<h2>Service Plan</h2>
			<?php 
				if (!isset($_SESSION['booked_service_id'])):
			?>
					<a type='button' href='<?php echo route("service/service_explorer");?>' class='button booking-button'>choose a service package</a>
			
			<?php 
				else:
					$service = $db->table('service')->where('service_id',getSession('booked_service_id'))->row();
			?>
					
					<table>
						<tbody>
							<tr>
								<td>Service Title:</td>
								<td><?php echo $service['service_title']; ?></td>
							</tr>
							<tr>
								<td>Type:</td>
								<td><?php echo $service['service_type']; ?></td>
							</tr>
							<tr>
								<td>Description:</td>
								<td><?php echo $service['service_description']; ?></td>
							</tr>
							<tr>
								<td>Price per hour:</td>
								<td><?php echo $service['service_price']; ?></td>
							</tr>
						</tbody>
					</table>
					
			<?php
				endif;
			?>
		</div>
		
		
			<?php 
				if (isset($_SESSION['booked_service_id']) && isset($_SESSION['booked_maid_id'])){
					echo '<div class="box">';
						$_GET['id'] = $maid['maid_id'];
						require_once getView('maid.time_slot');
					echo '</div>';
				}
			?>
		
		
		
		<div class='box'>
			<h2>Booking details</h2>
			<div class="input-box">
			<label for="phone">Address:</label>
			<input name='address' value="<?php echo $db->table('member')->where('member_id',getSession('member_id')) -> row()['member_address']?>"></input>
		</div>
	</div>
	
	<div class='booking-section'>
		<button type='button' class="booking-button button" onclick='confirm_booking()'>CONFIRM BOOKING</button>
	</div>
	
</form>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="<?php echo route('utils/booking.js');?>"></script>