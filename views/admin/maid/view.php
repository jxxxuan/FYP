<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$maids = $db->table('maid')->rows();
$flash = getFlash('message');

if(count($maids) > 0){
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
				<th>Status</th>
			</tr>
		</thead>

		<tbody>
			<?php 
			foreach ($maids as $maid) { 
				$maidinfo = $db->table('member')->where('member_id', $maid['member_id'])->row();
				$action = $maidinfo['member_status'] === 'Block' ? 'Active' : 'Block';
			?>
				<tr>
					<td><?php echo $maid['maid_id']; ?></td>
					<td><a href=<?php echo route('maid/maid_profile?maid_id='.$maid['maid_id'])?>><img class="border border-circle" src="<?php echo route($maidinfo['member_image']); ?>" alt="Member Image" style="height:100px;width:100px;"></a></td>
					<td><?php echo $maidinfo['member_name']; ?></td>
					<td><?php echo $maid['maid_age']; ?></td>
					<td><?php echo $maid['maid_gender']; ?></td>
					
					<td><?php echo $maid['maid_experience']; ?></td>
					<td><?php echo $maid['maid_skill']; ?></td>
					<td><?php echo date('H:i', strtotime($maid['availability_start'])); ?></td>
					<td><?php echo date('H:i', strtotime($maid['availability_end'])); ?></td>
					<td><?php echo $maidinfo['member_status']; ?></td>
					<td><a href="<?php echo route('admin/maid/block', $maid['maid_id']); ?>" onclick="return confirmation();"><?php echo $action?></a></td>
				</tr>
			<?php } ?>

		</tbody>
	</table>
<?php
}else{
?>
	<h2 class='text-center box'>No maid found</h2>
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

