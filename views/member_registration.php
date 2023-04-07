head>
	<title>Member Regiatration Form</title>
</head>
<body>

<h1>Member Regiatration Form</h1>

<?php
if (isPostMethod()) {
	
	$database = new Database();
	$database -> table('member') -> insert([
		'member_fullname' => $_POST['fullname'],
		'member_contact' => $_POST['phone_num'],
		'member_email' => $_POST['email'],
		'member_address' => $_POST['address'],
	]);

	if($password != $confirm_password) {
		echo "<p>Passwords do not match.</p>";
	} else {
		// Hash password
		//$hashed_password = password_hash($password, PASSWORD_DEFAULT);

		// Insert user data into database
		$database -> table('member') -> insert([
			'member_password' => $_POST['password']
		]);
	}
	redirect('');
}
?>

<form method="POST" action="maid_application" enctype="multipart/form-data">
	<label for="fullname">Full Name:</label>
	<input type="text" name="fullname" id="fullname" required><br><br>

	<label for="phone_num">Phone Number:</label>
	<input type="text" name="phone_num" id="phone_num" required><br><br>
	
	<label for="email">Email:</label>
	<input type="email" name="email" id="email" required><br><br>

	<label for="address">Address:</label>
	<textarea name="address" id="address" required></textarea><br><br>
	
	<label for="profile-image">Profile Image:</label>
	<input type="file" name="profile-image" id="profile-image">
	
	<label for="password">Password:</label>
	<input type="password" id="password" name="password" required><br><br>
	
	<label for="confirm_password">Confirm Password:</label>
	<input type="password" id="confirm_password" name="confirm_password" required><br><br>

	<input type="submit" value="Submit">
</form>



</body>