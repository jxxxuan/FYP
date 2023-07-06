<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$payments = $db->table('payment')->rows();
$flash = getFlash('message');


if(count($payments) > 0){
?>
	<h2>PAYMENT LIST</h2>
	<table class="admin-table box" style="min-width:90%">
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
			<?php foreach ($payments as $payment) { ?>
				<tr>
					<td><?php echo $payment['payment_id']; ?></td>
					<td><?php echo $payment['member_id']; ?></td>
					<td><?php echo $payment['booking_id']; ?></td>
					<td><?php echo $payment['payment_type']; ?></td>
					<td><?php echo $payment['bank_name']; ?></td>
					<td><?php echo $payment['bank_cardholdername']; ?></td>
					<td><?php echo $payment['bank_cardnum']; ?></td>
					<td><?php echo $payment['payment_price']; ?></td>
				</tr>
			<?php } ?>
		</tbody>
	</table>
<?php
}else{
?>
	<h2 class='box text-center'>No Payments found</h2>
<?php
}
?>

<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>
	
</script>
