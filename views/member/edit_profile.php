<?php
	require_once getView('layout.side-bar');
	$db = new Database();
	$member_info = $db -> table('member') -> where('member_id',getSession('id')) -> row();
?>
<div class='page'>
	<div class='box'>

	<?php
		if(isset($_GET['change_psw']) && $_GET['change_psw'] == 'true'):
	?>
			<section>
				<form action="change_password.php" method="post">
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
				<form action="" method="post">
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
						<input type="tel" id="phone" name="phone" value="<?php echo $member_info['member_contact']?>" required>
					</div>
					
					<div class="input-box">
						<label for="address">Address:</label>
						<input type="text" id="address" name="address" value="<?php echo $member_info['member_address']?>" required>
					</div>
					
					<div class="input-box">
						<label for="profile-image">Profile Image:</label>
						<img src="<?php echo $member_info['member_image_file_path']; ?>" alt="Current Profile Image">
						<input type="file" id="profile-image" name="profileImage">
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

<?php
if (isPostMethod()) {
    $result = $database->table('member')
        ->where('member_id', $id)
        ->update([
            'member_username' => $_POST['username'],
            'member_pass' => $_POST['pass'],
            'member_stud_id' => $_POST['student_id'],
            'member_name' => $_POST['name'],
            'member_ic' => $_POST['ic'],
            'member_email' => $_POST['email'],
            'member_phone_num' => $_POST['phone'],
            'member_e_num' => $_POST['ephone']
        ]);

    if ($result) {
        setFlash('message', 'Member successful edit!');
    }

    redirect('member/view');
}

?>
	
<script src=<?php echo route("utils/side-bar.js");?>></script>
	
