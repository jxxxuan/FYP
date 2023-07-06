<?php
if (isPostMethod()) {
    $database = new Database();
	$adminid = 1;
	$members = $database -> table('member') -> rows();
	$admins = $database -> table('admin') -> rows();
	
	foreach($members as $member){
		$emails[] = $member['member_email'];
	}
	
	foreach($admins as $admin){
		$emails[] = $admin['admin_email'];
	}
	
	$image = 'uploads/members/default.jpg';
	$status = 'Active';
	
	if(!($_POST['password'] === $_POST['confirm_password'])){
		echo '<script>alert("confirm password and password are not match");</script>';
	}else if(in_array($_POST['email'],$emails)){
		echo '<script>alert("This email account was registed");</script>';
	}else{
		$result = $database->table('member')->insert([
			'member_name' => $_POST['fullname'],
			'member_password' => $_POST['password'],
			'member_email' => $_POST['email'],
			'member_contact' => $_POST['contact'],
			'member_address' => $_POST['address'],
			'member_image' => $image,
			'member_status' => $status,
			'admin_id' => $adminid
		]);
		if ($result) {
			echo '<script>alert("sign up successful");
			window.location.href="sign-in"</script>';
		}
		
	}
	
	
}
?>

<div class="s">
	<div class="container2">
		<div class="form-box2">
			<h2>SIGN UP</h2>
			<form method="post" enctype="multipart/form-data">
				<div class="input-box2">
					<input type="text" id="fullname" name="fullname" pattern='[A-Za-z\s]{4,}'required><br><br>
					<label for="fullname">Full name:</label>
				</div>
				
				<div class="input-box2">
					<input type="email" id="email" name="email" required><br><br>
					<label for="email">Email:</label>
				</div>
				
				<div class="input-box2">
					<input type="text" id="contact" name="contact" pattern="^(\+?6?01)[0-46-9]-*[0-9]{7,8}$" required><br><br>
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