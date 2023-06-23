<?php 
    require_once getView("layout.side-bar");

    $database = new Database();
    $memberid = getSession('id');
    $bookings = $database -> table('booking') -> where('member_id',$memberid) -> rows();
?>

<?php
$count =1 ;
foreach($bookings as $booking):
    $serviceId = $booking['service_id'];
    $service = $database->table('service')->where('service_id', $serviceId)->row();
?>
	<a class='d-flex box maid-name-card' href="<?php echo route('') ?>">
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
	</a>
<?php
$count++;
endforeach;
?>
</div>






