<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$bookings = $db->table('booking')->rows();
$flash = getFlash('message');

if (isPostMethod() && isset($_POST['status'])){
	$status = $_POST['status'];
	$bookings = $db->table('booking')
		-> Where('booking_status',$status)
		-> rows();
} else {
	$bookings = $db-> table('booking')
		-> rows();
}	
?>

<form class='box' action="" method="post">
	<div style='text-align:left'>
		<label for="status">booking status: </label>
		<select name="status" id="status">
			<option value="Pending" <?php if (isset($_POST['status']) && $_POST['status'] === 'Pending') echo 'selected'; ?>>Pending</option>
			<option value="Reject" <?php if (isset($_POST['status']) && $_POST['status'] === 'Reject') echo 'selected'; ?>>Reject</option>
			<option value="Confirm" <?php if (isset($_POST['status']) && $_POST['status'] === 'Confirm') echo 'selected'; ?>>Confirm</option>
			<option value="Working" <?php if (isset($_POST['status']) && $_POST['status'] === 'Working') echo 'selected'; ?>>Working</option>
			<option value="Completed" <?php if (isset($_POST['status']) && $_POST['status'] === 'Completed') echo 'selected'; ?>>Completed</option>
		</select>

		<button type="submit">Filter</button>
	</div>
</form>

<?php
if(count($bookings) > 0){
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
					<td><a href=<?php echo route('service/service',$booking['service_id'])?>><?php echo $booking['service_id']; ?></a></td>
					<td><a href=<?php echo route('member/member_profile',$booking['member_id'])?>><?php echo $booking['member_id']; ?></a></td>
					<td><a href=<?php echo route('maid/maid_profile?maid_id='.$booking['maid_id'])?>><?php echo $booking['maid_id']; ?></a></td>
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
