<?php include("dataconnection.php"); ?>
<!DOCTYPE html>
<html>
<head>
	<title>User Registration</title>
</head>
<body>
	<h1>User Registration</h1>
	<form method="post" action="">
		<label for="email">Email:</label>
		<input type="email" id="email" name="email" required><br><br>

		<label for="password">Password:</label>
		<input type="password" id="password" name="password" required><br><br>
		
		<label for="confirm_password">Confirm Password:</label>
		<input type="password" id="confirm_password" name="confirm_password" required><br><br>
		
		<input type="submit" name="register" value="Register">
	</form>

	<?php

		// Check if registration form is submitted
		if(isset($_POST['register'])) {
			$email = mysqli_real_escape_string($connect, $_POST['email']);
			$password = mysqli_real_escape_string($connect, $_POST['password']);
			$confirm_password = mysqli_real_escape_string($connect, $_POST['confirm_password']);

			//Check if email exist
			$sql = "SELECT * FROM maid WHERE email='$email'";
			$result = mysqli_query($connect, $sql);

			if (mysqli_num_rows($result) > 0) {
				// Check if passwords match
				if($password != $confirm_password) {
					echo "<p>Passwords do not match.</p>";
				} else {
					// Hash password
					//$hashed_password = password_hash($password, PASSWORD_DEFAULT);

					// Insert user data into database
					$sql = "INSERT INTO maid (password) VALUES ('$password')";
					if(mysqli_query($connect, $sql)) {
						echo "<p>Registration successful.</p>";
					} else {
						echo "<p>Error: " . mysqli_error($connect) . "</p>";
					}
				}
			}else{
				echo "Sorry, your application has not been approved";
			}

			
		}
	?>
</body>
</html>