<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$maids = $db->table('maid')->rows();
$flash = getFlash('message');
?>

<h2>MAID LIST</h2>
<table class="admin-table box">
	<thead>
		<tr>
			<th>Maid ID</th>
			<th>Image</th>
			<th>Name</th>
			<th>Age</th>
			<th>Gender</th>
			<th>Experience</th>
			<th>Skill</th>
			
			<th>Availability Start</th>
			<th>Availability End</th>
			
		</tr>
	</thead>

	<tbody>
		<?php 
			foreach ($maids as $maid) { 
				$member = $db->table('member')->where('member_id', $maid['member_id'])->row();
		?>
				<tr>
					<td><?php echo $maid['maid_id']; ?></td>
					<td><img src="<?php echo route($member['member_image']); ?>" alt="Member Image" style="height:100px;width:100px;"></td>
					<td><?php echo $member['member_name']; ?></td>
					<td><?php echo $maid['maid_age']; ?></td>
					<td><?php echo $maid['maid_gender']; ?></td>
					
					<td><?php echo $maid['maid_experience']; ?></td>
					<td><?php echo $maid['maid_skill']; ?></td>
					<td><?php echo date('H:i', strtotime($maid['availability_start'])); ?></td>
					<td><?php echo date('H:i', strtotime($maid['availability_end'])); ?></td>
					
					<td><a href="<?php echo route('admin/maid/delete', $maid['maid_id']); ?>" onclick="return confirmation();">Delete</a></td>
				</tr>
		<?php } ?>

	</tbody>
</table>

<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>

    function confirmation() {
        return confirm('Do you want to delete this record?');
    }
</script>
