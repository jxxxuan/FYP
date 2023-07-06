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
				<th>Status</th>
				
			</tr>
		</thead>

		<tbody>
			<?php 
				foreach ($members as $member) {
					$action = $member['member_status'] === 'Block' ? 'Active' : 'Block';
			?>
					<tr>
						<td><?php echo $member['member_id']; ?></td>
						<td><a href=<?php echo route('member/member_profile',$member['member_id'])?>><img class="border border-circle" src="<?php echo route($member['member_image']); ?>" alt="Member Image" style="height:100px;width:100px;"></a></td>
						<td><?php echo $member['member_name']; ?></td>
						
						
						<td><?php echo $member['member_contact']; ?></td>
						<td><?php echo $member['member_address']; ?></td>
						<td><?php echo $member['member_email']; ?></td>
						<td><?php echo $member['member_status']; ?></td>
						
						<td><a href="<?php echo route('admin/member/block', $member['member_id']); ?>" onclick="return confirmation();"><?php echo $action?></a></td>
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
        return confirm('Do you want to block this member?');
    }
</script>
