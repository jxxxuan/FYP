<?php 
    require_once getView("layout.side-bar");

    $database = new Database();
    $memberid = getSession('id');

	if (isPostMethod() && isset($_POST['status'])){
		$status = $_POST['status'];
		$bookings = $database->table('booking')
			-> Where('member_id',$memberid)
			-> Where('booking_status',$status)
			-> rows();
	} else {
		$bookings = $database-> table('booking')
			-> Where('member_id',$memberid)
			-> rows();
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
			<a class='d-flex box maid-name-card' href=<?php echo route('member/member_booking_status?booking_id=').$booking['booking_id'] ?>>
				<div><?php echo $count ?></div>
				
				<div class='mx-2 my-1' style="min-width:400px;">
					<h3>"<?php echo $service['service_type']?>"</h3>
					<h4 class='mt-1'>Service Title: "<?php echo $service['service_title'] ?>"</h4>
				</div>
				
				<div class='mx-2 my-1'>
					<div>Booking Time: "<?php echo $booking['booking_datetime'] ?>"</div>
					<div class='mt-1'>Arrive Time: "<?php echo $booking['booking_arrive_datetime']?>"</div>
					<div class='mt-1'>Leave Time: "<?php echo $booking['booking_leave_datetime'] ?>"</div>
				</div>

				<div class='mx-2 my-1'>
					<div class='mt-1'>Booking Status: <?php echo $booking['booking_status'] ?></div>
				</div>
			</a>
<?php

	$count++;
	endforeach;
	}else{
?>
		<h2 class='text-center'>No bookings<h2>
<?php
	}
?>
</div>






