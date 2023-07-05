<?php
if (isPostMethod()) {
    $database = new Database();
	$adminid = 1;
	
	$image = 'uploads/members/default.jpg';
	
	$result = $database->table('member')->insert([
		'member_name' => $_POST['fullname'],
		'member_password' => $_POST['password'],
		'member_email' => $_POST['email'],
		'member_contact' => $_POST['contact'],
		'member_address' => $_POST['address'],
		'member_image' => $image,
		'admin_id' => $adminid
	]);
	
	if ($result) {
		redirect('authentication/sign-in');
	}
	
}
?>

<div class="s">
	<div class="container2">
		<div class="form-box2">
			<h2>SIGN UP</h2>
			<form method="post" enctype="multipart/form-data">
				<div class="input-box2">
					<input type="text" id="fullname" name="fullname" required><br><br>
					<label for="fullname">Full name:</label>
				</div>
				
				<div class="input-box2">
					<input type="email" id="email" name="email" required><br><br>
					<label for="email">Email:</label>
				</div>
				
				<div class="input-box2">
					<input type="text" id="contact" name="contact" required><br><br>
					<label for="contact">Contact:</label>
				</div>

				<div class="input-box2">
					<input type="text" id="address" name="address" required><br><br>
					<label for="address">Address:</label>
				</div>
				
				<div class="input-box2">
					<input type="password" id="password" name="password" required><br><br>
					<label for="password">Password:</label>
				</div>
				
				<div class="input-box2">
					<input type="password" id="confirm_password" name="confirm_password" required><br><br>
					<label for="confirm_password">Confirm Password:</label>
				</div>
				
				<input type="submit" name="register" value="Register" class="button black-button">

				<div class ="register">
					<i>Already have an Account? <a href="<?php echo route('authentication/sign-in'); ?>">Login Here!</a></i>
				</div>
			</form>
		</div>
	</div>
</div>