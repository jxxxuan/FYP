<?php


if (isPostMethod()) {
    $database = new Database();
	
	$result = $database->table('member')->insert([
		'member_first_name' => $_POST['first_name'],
		'member_last_name' => $_POST['last_name'],
		'member_password' => $_POST['password'],
		'member_email' => $_POST['email'],
		'member_contact' => $_POST['contact'],
	]);
	
	if ($result) {
		redirect('authentication/sign-in');
	}
	
	/*
	$result = $database->table('member')
		->where('email',$_POST['email'])
		->row();
		
	if ($result !== null) {
		setFlash('message', "This email was register");
	}else{
		if($_POST['password'] != $_POST['confirm_password']) {
			setFlash('message', "Passwords do not match.");
		}else{
			$result = $database->table('member')->insert([
				'first_name' => $_POST['first_name'],
				'last_name' => $_POST['last_name'],
				'password' => $_POST['password'],
				'email' => $_POST['email'],
				'contact' => $_POST['contact'],
			]);
			echo $result;
			echo "f";
			if ($result) {
				redirect('authentication/sign-in');
			}
		}
	}*/
}
?>

<div class="pt-3 pb-3">
    <form method="post" action="">
		<label for="first name">First name:</label>
		<input type="text" id="first_name" name="first_name" required><br><br>
		
		<label for="last name">Last name:</label>
		<input type="text" id="last_name" name="last_name" required><br><br>
		
		<label for="email">Email:</label>
		<input type="email" id="email" name="email" required><br><br>
		
		<label for="contact">Contact:</label>
		<input type="text" id="contact" name="contact" required><br><br>

		<label for="password">Password:</label>
		<input type="password" id="password" name="password" required><br><br>
		
		<label for="confirm_password">Confirm Password:</label>
		<input type="password" id="confirm_password" name="confirm_password" required><br><br>
		
		<input type="submit" name="register" value="Register">
	</form>
</div>
