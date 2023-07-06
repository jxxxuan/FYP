<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$payments = $db->table('payment')->rows();
$flash = getFlash('message');

<?php
if(count($bookings) > 0){
?>
	<h2>PAYMENT LIST</h2>
	<table class="admin-table box">
		<thead>
			<tr>
				<th>Payment ID</th>
				<th>Booking ID</th>
				<th>Member ID</th>
				<th>Payemnt type</th>
				<th>Payemnt price</th>
				<th>Bank name</th>
				<th>Bank card holder name</th>
				<th>Bank card number</th>
			</tr>
		</thead>

		<tbody>
			<?php foreach ($bookings as $booking) { ?>
				<tr>
					<td><?php echo $booking['booking_id']; ?></td>
					<td><?php echo $booking['booking_datetime']; ?></td>
					<td><?php echo $booking['booking_datetime']; ?></td>
					<td><a href=<?php echo route('member/member_profile',$booking['member_id'])?>><?php echo $booking['member_id']; ?></a></td>
					<td><?php echo $booking['booking_datetime']; ?></td>
					<td><?php echo $booking['booking_status']; ?></td>
					<td><?php echo $booking['booking_arrive_datetime']; ?></td>
					<td><?php echo $booking['booking_address']; ?></td>
					<td><?php echo $booking['booking_leave_datetime']; ?></td>
				</tr>
			<?php } ?>
		</tbody>
	</table>
<?php
}else{
?>
	<h2 class='box text-center'>No booking found</h2>
<?php
}
?>

<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>
	
</script>
