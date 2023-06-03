<?php
$id = $_GET['id'] ?? null;

if ($id === null) {
    redirect('admin/manage?table=member');
}

$db = new Database();
$member = $db->table('member')->where('member_id', $id)->row();

if (isPostMethod()) {
	$result = $db->table('member')
    ->where('member_id', $id)
    ->update([
        'member_name' => $_POST['member_name'],
        'member_email' => $_POST['member_email'],
        'member_contact' => $_POST['member_contact'],
        'member_address' => $_POST['member_address'],
        //'member_image' => $_POST['member_image'],
    ]);

    if ($result) {
        setFlash('message', 'Member successful edit!');
    }
	
    redirect('admin/manage?table=member');
	
}
require_once getView('layout.side-bar');
?>

<div class='box profile'>

	<section>
		<form method="post">
			<div class="input-box">
				<label for="name">Name:</label>
				<input type="text" id="member_name" name="member_name" value="<?php echo $member['member_name']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="email">Email:</label>
				<input type="email" id="member_email" name="member_email" value="<?php echo $member['member_email']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="contact">Contact:</label>
				<input type="text" id="member_contact" name="member_contact" value="<?php echo $member['member_contact']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="address">Address:</label>
				<input type="text" id="member_address" name="member_address" value="<?php echo $member['member_address']; ?>" required>
			</div>
			
			<!--
			<div class="input-box">
				<label for="image">Image:</label>
				<input type="text" id="member_image" name="member_image" value="<?php echo $member['member_image']; ?>" required>
			</div>
			-->
			
			<button class="button black-button" type="submit">Update Profile</button>
		</form>
	</section>

</div>