<head>
	<title>Member Regiatration Form</title>
</head>
<body>

<h1>Member Regiatration Form</h1>

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
	}else{
		echo "<p>You can't register in this time.</p>";
	}
	
	#redirect('');
}
?>

<form method="POST" action="maid_registration" enctype="multipart/form-data">
	<label for="email">Email:</label>
	<input type="email" name="email" id="email" required><br><br>
	
	<label for="password">Password:</label>
	<input type="password" id="password" name="password" required><br><br>
	
	<label for="confirm_password">Confirm Password:</label>
	<input type="password" id="confirm_password" name="confirm_password" required><br><br>

	<input type="submit" value="Submit">
</form>


</body>