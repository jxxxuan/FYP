<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$bookings = $db->table('booking')->rows();
$flash = getFlash('message');
?>


<h2>BOOKING LIST</h2>
<table class="admin-table box">
	<thead>
		<tr>
			<th>Booking ID</th>
			<th>Service ID</th>
			<th>Member ID</th>
			<th>Maid ID</th>
			<th>Booking Time</th>
			<th>Booking Status</th>
			<th>Booking Arrive Time</th>
			<th>Booking Address</th>
			<th>Booking Leave Time</th>
		</tr>
	</thead>

	<tbody>
		<?php foreach ($bookings as $booking) { ?>
			<tr>
				<td><?php echo $booking['booking_id']; ?></td>
				<td><?php echo $booking['service_id']; ?></td>
				<td><?php echo $booking['member_id']; ?></td>
				<td><?php echo $booking['maid_id']; ?></td>
				<td><?php echo $booking['booking_datetime']; ?></td>
				<td><?php echo $booking['booking_status']; ?></td>
				<td><?php echo $booking['booking_arrive_datetime']; ?></td>
				<td><?php echo $booking['booking_address']; ?></td>
				<td><?php echo $booking['booking_leave_datetime']; ?></td>
			</tr>
		<?php } ?>
	</tbody>
</table>
<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>
	
</script>
