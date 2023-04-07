
<head>
	<title>Maid Application Form</title>
</head>
<body>

<h1>Maid Application Form</h1>

<?php
if (isPostMethod()) {
	$background_check_status = "pending";
	
	$database = new Database();
	$id = $database -> table('maid_application') -> insert([
                'name' => $_POST['name'],
                'age' => $_POST['age'],
				'gender' => $_POST['gender'],
                'contact' => $_POST['contact'],
				'email' => $_POST['email'],
                'address' => $_POST['address'],
				'experience' => $_POST['experience'],
                'skill' => $_POST['skill'],
				'availability_start' => $_POST['availability_start'],
                'availability_end' => $_POST['availability_end'],
				'background_check_status' => $background_check_status
            ]);

	
	if (isset($_FILES['profile-image'])) {
		$profileImage = $_FILES['profile-image'];
		$targetDir = 'uploads/';
		$targetFile = $targetDir . basename($id . '.jpg');

		if (!move_uploaded_file($profileImage['tmp_name'], $targetFile)) {
		  echo "Sorry, there was an error uploading your file.";
		}
		$database -> table('maid_application') -> where('application_id',$id) -> update(['image_file_path' => $targetFile]);
	}
	redirect('');
}
?>

<form method="POST" action="maid_application" enctype="multipart/form-data">
	<label for="name">Name:</label>
	<input type="text" name="name" id="name" required><br><br>

	<label for="age">Age:</label>
	<input type="number" name="age" id="age" required><br><br>

	<label for="gender">Gender:</label>
	<input type="radio" name="gender" id="gender" value="Male" required>Male
	<input type="radio" name="gender" id="gender" value="Female" required>Female<br><br>

	<label for="contact">Contact:</label>
	<input type="text" name="contact" id="contact" required><br><br>
	
	<label for="email">Email:</label>
	<input type="email" name="email" id="email" required><br><br>

	<label for="address">Address:</label>
	<textarea name="address" id="address" required></textarea><br><br>

	<label for="skill">Skill:</label>
	<input type="text" name="skill" id="skill" required><br><br>
	
	<label for="experience">Experience:</label>
	<input type="number" name="experience" id="experience"><br><br>
	
	<label for="availability">Availability from</label>
	<select name="availability_start" id="availability_start">
	  <option value="6am">6 am</option>
	  <option value="7am">7 am</option>
	  <option value="8am">8 am</option>
	  <option value="9am">9 am</option>
	  <option value="10am">10 am</option>
	  <option value="11am">11 am</option>
	  <option value="12pm">12 pm</option>
	</select>
	<br>
	<label for="availability">Availability until</label>
	<select name="availability_end" id="availability_end">
	  <option value="2pm">2 pm</option>
	  <option value="3pm">3 pm</option>
	  <option value="4pm">4 pm</option>
	  <option value="5pm">5 pm</option>
	  <option value="6pm">6 pm</option>
	  <option value="7pm">7 pm</option>
	  <option value="8pm">8 pm</option>
	</select>
	<br>
	
	<label for="profile-image">Profile Image:</label>
	<input type="file" name="profile-image" id="profile-image">

	<input type="submit" value="Submit">
</form>



</body>


