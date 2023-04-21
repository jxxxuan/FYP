<head>
	<title>Maid Regiatration Form</title>
</head>

<?php
if (isPostMethod()) {
	
	$database = new Database();
	$rows = $database -> table('maid_application') -> where('email',$_POST['email']) -> rows();
	if (count($rows) != 0){
		if($_POST['password'] != $_POST['confirm_password']) {
			echo "<p>Passwords do not match.</p>";
		} else {
			// Hash password
			//$hashed_password = password_hash($password, PASSWORD_DEFAULT);

			// Insert user data into database
			$row = $rows[0];
			$database -> table('maid') -> insert([
				'name' => $row['name'],
                'age' => $row['age'],
				'gender' => $row['gender'],
                'contact' => $row['contact'],
				'maid_email' => $row['email'],
                'address' => $row['address'],
				'experience' => $row['experience'],
                'skill' => $row['skill'],
				'availability_start' => $row['availability_start'],
                'availability_end' => $row['availability_end'],
				'image_file_path' => $row['image_file_path'],
				'maid_password' => $_POST['password']
			]);
		}
		redirect('authentication/sign-in');
	}else{
		echo "<p>You can't register in this time.</p>";
	}
	
	
}
?>


<section class="s">
	<div class="container1">
		<div class="form-box login">
			<h2>Maid Regiatration</h2>
			<form method="POST" action="maid_registration" enctype="multipart/form-data">
				<div class="input-box1">					
					<input type="email" name="email" id="email" required>
					<label for="email">Email:</label>
				</div>
				
				<div class="input-box1">					
					<input type="password" id="password" name="password" required>
					<label for="password">Password:</label>
				</div>
				
				<div class="input-box1">
					<input type="password" id="confirm_password" name="confirm_password" required>
					<label for="confirm_password">Confirm Password:</label>
				</div>
						
				<input type="submit" value="Submit" class="button">
			</form>
		</div>
	</div>
</section>
