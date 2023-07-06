<?php
	if(getSession('user_role') == ADMIN_ROLE || !getSession('loggedin')){
		redirect('authentication/sign-in');
	}

	if(isPostMethod()) {
		foreach($_POST as $key => $value){
			setSession([$key => $value]);
		}
	}
	$db = new Database();
?>
<form action='../utils/booking_process.php' method="post">
	<div class='container'>
		
		<div class='box'>
		<h2>Maid</h2>
		<?php 
			if (!isset($_SESSION['booked_maid_id'])):
		?>
				<a type='button' href='<?php echo route("member/maid_explorer");?>' class='button booking-button'>choose a maid</a>
		
		<?php 
			else:
				echo "<input type='hidden' name='booked_maid_id' value=".$_SESSION['booked_maid_id'].">";
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
					echo "<input type='hidden' name='booked_service_id' value=".$_SESSION['booked_service_id'].">";
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
					
			?>
					
					
					<label for="booking_date">Booking Date: </label>
					<input type="date" id="booking_date" name="booking_date" min="<?php echo date('Y-m-d'); ?>" required>
					
					<div class="input-box-option">
					  <label for="booking_arrive_time">From</label>
					  <select name="booking_arrive_time" id="booking_arrive_time" type="time" min="08:00" max="17:00">
						<option value="" selected disabled></option>
						<?php if ($maid['availability_start'] <= '08:00:00' && $maid['availability_end'] >= '08:00:00') echo '<option value="08:00" >8 am</option>'; ?>
						<?php if ($maid['availability_start'] <= '09:00:00' && $maid['availability_end'] >= '09:00:00') echo '<option value="09:00" >9 am</option>'; ?>
						<?php if ($maid['availability_start'] <= '10:00:00' && $maid['availability_end'] >= '10:00:00') echo '<option value="10:00" >10 am</option>'; ?>
						<?php if ($maid['availability_start'] <= '11:00:00' && $maid['availability_end'] >= '11:00:00') echo '<option value="11:00" >11 am</option>'; ?>
						<?php if ($maid['availability_start'] <= '12:00:00' && $maid['availability_end'] >= '12:00:00') echo '<option value="12:00" >12 pm</option>'; ?>
						<?php if ($maid['availability_start'] <= '13:00:00' && $maid['availability_end'] >= '13:00:00') echo '<option value="13:00" >1 pm</option>'; ?>
						<?php if ($maid['availability_start'] <= '14:00:00' && $maid['availability_end'] >= '14:00:00') echo '<option value="14:00" >2 pm</option>'; ?>
						<?php if ($maid['availability_start'] <= '15:00:00' && $maid['availability_end'] >= '15:00:00') echo '<option value="15:00" >3 pm</option>'; ?>
						<?php if ($maid['availability_start'] <= '16:00:00' && $maid['availability_end'] >= '16:00:00') echo '<option value="16:00" >4 pm</option>'; ?>
						<?php if ($maid['availability_start'] <= '17:00:00' && $maid['availability_end'] >= '17:00:00') echo '<option value="17:00" >5 pm</option>'; ?>
					  </select>
					</div>
					
					<div class="input-box-option">
					  <label for="booking_leave_time">Until</label>
					  <select name="booking_leave_time" id="booking_leave_time" type="time" min="09:00" max="18:00">
						<option value="" selected disabled></option>
						<?php if ($maid['availability_end'] >= '09:00:00' && $maid['availability_start'] <= '09:00:00') echo '<option value="09:00" >9 am</option>'; ?>
						<?php if ($maid['availability_end'] >= '10:00:00' && $maid['availability_start'] <= '10:00:00') echo '<option value="10:00" >10 am</option>'; ?>
						<?php if ($maid['availability_end'] >= '11:00:00' && $maid['availability_start'] <= '11:00:00') echo '<option value="11:00" >11 am</option>'; ?>
						<?php if ($maid['availability_end'] >= '12:00:00' && $maid['availability_start'] <= '12:00:00') echo '<option value="12:00" >12 pm</option>'; ?>
						<?php if ($maid['availability_end'] >= '13:00:00' && $maid['availability_start'] <= '13:00:00') echo '<option value="13:00" >1 pm</option>'; ?>
						<?php if ($maid['availability_end'] >= '14:00:00' && $maid['availability_start'] <= '14:00:00') echo '<option value="14:00" >2 pm</option>'; ?>
						<?php if ($maid['availability_end'] >= '15:00:00' && $maid['availability_start'] <= '15:00:00') echo '<option value="15:00" >3 pm</option>'; ?>
						<?php if ($maid['availability_end'] >= '16:00:00' && $maid['availability_start'] <= '16:00:00') echo '<option value="16:00" >4 pm</option>'; ?>
						<?php if ($maid['availability_end'] >= '17:00:00' && $maid['availability_start'] <= '17:00:00') echo '<option value="17:00" >5 pm</option>'; ?>
						<?php if ($maid['availability_end'] >= '18:00:00' && $maid['availability_start'] <= '18:00:00') echo '<option value="18:00" >6 pm</option>'; ?>
					  </select>
					</div>
						
			<?php
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
	</div>
	
	<div class='booking-section'>
		<button type='submit' class="booking-button button">CONFIRM BOOKING</button>
	</div>
	
</form>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="<?php echo route('utils/booking.js');?>"></script>