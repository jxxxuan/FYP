<?php
	require_once getView('layout.side-bar');
	$db = new Database();
	$member_info = $db -> table('member') -> where('member_id',getSession('id')) -> row();
?>

<?php
if (isPostMethod()) {

	if(isset($_FILES['member_image']) && $_FILES['member_image']['error'] === UPLOAD_ERR_OK) {
		$image_temp = $_FILES['member_image']['tmp_name'];
		$target_path = 'uploads/members/' . $_FILES['member_image']['name'];
		move_uploaded_file($image_temp, $target_path);

		$member_image = $target_path;
	} else {
		$member_image = $member_info['member_image'];
	}
    $result = $db->table('member')
        ->where('member_id', getSession('id'))
        ->update([
            'member_name' => $_POST['name'],
            'member_email' => $_POST['email'],
            'member_contact' => $_POST['contact'],
            'member_address' => $_POST['address'],
            'member_image' => $member_image
        ]);

    if ($result) {
        setFlash('message', 'Member Profile Successfully Edit!');
    }

    redirect('member/member_profile');
}
require_once getView('layout.side-bar');
?>

<div class='page'>
	<div class='box'>

	<?php
		if(isset($_GET['change_psw']) && $_GET['change_psw'] == 'true'):
	?>
			<section>
				<form action="change_password.php" method="post" >
					<input type='hidden' name='id' value=<?php echo getSession('id');?>>
				
					<div class="input-box">
						<label for="current-password">Current Password:</label>
						<input type="password" id="current-password" name="currentPassword" required>
					</div>
					
					<div class="input-box">
						<label for="new-password">New Password:</label>
						<input type="password" id="new-password" name="newPassword" required>
					</div>
					
					<div class="input-box">
						<label for="confirm-password">Confirm Password:</label>
						<input type="password" id="confirm-password" name="confirmPassword" required>
					</div>
					
					<button type="submit">Change Password</button>
				</form>
			</section>
	<?php
		else:
	?>
			<section>
				<h2>Personal Information</h2>
				<form action="" method="post" enctype="multipart/form-data">
					<input type='hidden' name='id' value=<?php echo getSession('id');?>>
					<div class="input-box">
						<label for="name">Name:</label>
						<input type="text" id="name" name="name" value="<?php echo $member_info['member_name']?>" required>
					</div>

					<div class="input-box">
						<label for="email">Email:</label>
						<input type="email" id="email" name="email" value="<?php echo $member_info['member_email']?>" required>
					</div>
					
					<div class="input-box">
						<label for="phone">Phone:</label>
						<input type="tel" id="phone" name="contact" value="<?php echo $member_info['member_contact']?>" required>
					</div>
					
					<div class="input-box">
						<label for="address">Address:</label>
						<input type="text" id="address" name="address" value="<?php echo $member_info['member_address']?>" required>
					</div>
					
					<div class="input-box">
						<label for="profile-image">Profile Image:</label>
						<img src="<?php echo route($member_info['member_image']); ?>" alt="Current Profile Image" width="100px" height="100px">
						<input type="file" id="member_image" name="member_image">
					</div>
					
					<button class="button black-button" type="submit">Update Profile</button>
					
				</form>

			</section>
			<a href="<?php echo route('member/edit_profile'); ?>?change_psw=true">Change password</a>
	<?php
		endif;
	?>

	</div>
</div>


	
<script src=<?php echo route("utils/side-bar.js");?>></script>
	
