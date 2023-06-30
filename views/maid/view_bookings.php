<?php 
    require_once getView("layout.side-bar");

    $database = new Database();
	
    $maidid = getSession('id');
	$bookings = $database-> table('booking')
			-> Where('maid_id',$maidid)
			-> Where('booking_status','pending')
			-> rows();
    
	if (isPostMethod() && isset($_POST['status'])){
		$status = $_POST['status'];
		$bookings = $database->table('booking')
			-> Where('maid_id',$maidid)
			-> Where('booking_status',$status)
			-> rows();

	} else if (isPostMethod() && isset($_POST['action'])) {
		$database -> table('booking') -> where('booking_id',$_POST['id']) ->update(['booking_status'=> $_POST['action']]);

	} 
?>

<div class='page'>
	<form action="" method="post">
		<div>
			<label for="status">booking status: </label>
			<select name="status" id="status">
				<option value="Pending">Pending</option>
				<option value="Reject">Reject</option>
				<option value="Confirm">Confirm</option>
				<option value="Working">Working</option>
				<option value="Completed">Completed</option>
			</select>

			<button type="submit">Filter</button>
		</div>
	</form>


<?php
	if(count($bookings) > 0){
		$count =1 ;
		foreach($bookings as $booking):
			$serviceId = $booking['service_id'];
			$service = $database->table('service')->where('service_id', $serviceId)->row();
?>
			<div class='box d-flex'>
				<a class='d-flex maid-name-card' href=<?php echo route('maid/booking_status?booking_id=').$booking['booking_id'] ?>>
					
					<div class='mx-2 my-1' style="min-width:400px;">
						<h3><?php echo $service['service_type']?></h3>
						<h4 class='mt-1'>Service Title: <?php echo $service['service_title'] ?></h4>
					</div>
					
					<div class='mx-2 my-1'>
						<div>Booking Time: <?php echo $booking['booking_datetime'] ?></div>
						<div class='mt-1'>Arrive Time: <?php echo $booking['booking_arrive_datetime']?></div>
						<div class='mt-1'>Leave Time: <?php echo $booking['booking_leave_datetime'] ?></div>
					</div>

					

				</a>
				<div class='mx-2 my-1'>
					<div class='mt-1'>Booking Status: <?php echo $booking['booking_status'] ?></div>
					<?php 
					if($booking['booking_status'] == "Pending") {?>
						<div class='my-1'>
							<form method='post'>
								<label for="status">Booking Status:</label>
								<input type="hidden" name="id" value="<?php echo $booking['booking_id']; ?>">
								<td>
									<select name='action'>
										<option value="Pending">Pending</option>
										<option value="Comfirm">Comfirm</option>
										<option value="Reject">Reject</option>
									</select>
								</td>
								<td><input type='submit' value=Update></td>
							</form>
						</div>
					<?php
					}?>
					
				</div>
			</div>
			
		<?php
		$count++;
		endforeach;
	}else{
	?>
		<h3>No bookings<h3>
	<?php
	}?>
</div>






