<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('');
}

$db = new Database();

if (isPostMethod()) {
	$db -> table('maid') -> where('member_id',$_POST['id']) ->update(['maid_background_check_status'=> $_POST['action']]);
	if($_POST['action'] == 'Approved'){
		setFlash('message', 'Successfully approve');
	}else{
		setFlash('message', 'Successfully reject');
	}
}

$maids = $db->table('maid')->where('maid_background_check_status', 'Pending')->rows();
$flash = getFlash('message');
?>

<?php
if(count($maids) > 0){
?>
	<h2>MAID APPLICATION</h2>
	<table class="admin-table box">
		<thead>
			<tr>
				<th>Member ID</th>
				<th>Image</th>
				<th>Name</th>
				<th>Age</th>
				<th>Gender</th>
				<th>Contact</th>
				<th>Address</th>
				<th>Email</th>
				<th>Experience</th>
				<th>Skill</th>
				<th>Availability</th>
				<th>Action</th>
			</tr>
		</thead>

		<tbody>
			<?php
			foreach ($maids as $maid) {
				$member = $db->table('member')->where('member_id', $maid['member_id'])->row();
			?>
				<tr>
					<td><?php echo $maid['member_id']; ?></td>
					<td><a href=<?php echo route('member/member_profile',$maid['member_id'])?>><img class="border border-circle" src="<?php echo route($member['member_image']); ?>" alt="Member Image" style="height:100px;width:100px;"></a></td>
					<td><?php echo $member['member_name']; ?></td>
					<td><?php echo $maid['maid_age']; ?></td>
					<td><?php echo $maid['maid_gender']; ?></td>
					<td><?php echo $member['member_contact']; ?></td>
					<td><?php echo $member['member_address']; ?></td>
					<td><?php echo $member['member_email']; ?></td>
					<td><?php echo $maid['maid_experience'].' years'; ?></td>
					<td><?php echo $maid['maid_skill']; ?></td>
					<td><?php echo date('H:i', strtotime($maid['availability_start'])); ?>:<?php echo date('H:i', strtotime($maid['availability_end'])); ?></td>
					<form method='post'>
					<input type="hidden" name="id" value="<?php echo $maid['member_id']; ?>">
					<td>
						<select name='action'>
							<option value="Pending">Pending</option>
							<option value="Approved">Approved</option>
							<option value="Rejected">Rejected</option>
						</select>
					</td>
					<td><input type='submit' value=Update onclick="return confirmation();"></td>
					</form>
				</tr>
			<?php } ?>
		</tbody>
	</table>
<?php
}else{
?>
	<h2 class='text-center box'>No maid application found</h2>
<?php
}
?>
<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>
	
    function confirmation() {
		return confirm('Are you sure you want to take this action?');
    }
</script>



