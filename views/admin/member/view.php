<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$members = $db->table('member')->rows();
$flash = getFlash('message');

if(count($members) > 0){
?>

	<h2>MEMBER LIST</h2>
	<table class="admin-table box">
		<thead>
			<tr>
				<th>Member ID</th>
				<th>Image</th>
				<th>Name</th>
				<th>Contact</th>
				<th>Address</th>
				<th>Email</th>
				
			</tr>
		</thead>

		<tbody>
			<?php 
				foreach ($members as $member) {
			?>
					<tr>
						<td><?php echo $member['member_id']; ?></td>
						<td><img src="<?php echo route($member['member_image']); ?>" alt="Member Image" style="height:100px;width:100px;"></td>
						<td><?php echo $member['member_name']; ?></td>
						
						
						<td><?php echo $member['member_contact']; ?></td>
						<td><?php echo $member['member_address']; ?></td>
						<td><?php echo $member['member_email']; ?></td>
						
						<td><a href="<?php echo route('admin/member/delete', $member['member_id']); ?>" onclick="return confirmation();">Delete</a></td>
					</tr>
			<?php } ?>

		</tbody>
	</table>
<?php
}else{
?>
	<h2 class='box text-center'>No member found</h2>
<?php
}
?>

<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>

    function confirmation() {
        return confirm('Do you want to delete this record?');
    }
</script>
