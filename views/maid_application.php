<script>
	const container = document.querySelector('.container3');
	const p1Link = document.querySelector('.p1-link');
	const p2Link = document.querySelector('.p2-link');

	p2Link.addEventListener('click', ()=> {
		container.classList.add('active');
	});

	p1Link.addEventListener('click', ()=> {
		container.classList.remove('active');
	});
</script>
    
<div class="s">
	<div class="container3">
		<div class="form-box p1">
			<h2>Maid Application Form</h2>
			<form method="POST" action="maid_application" enctype="multipart/form-data">
				<div class="input-box3">
					<input type="text" name="name" id="name" required>
					<label for="name">Name:</label>
				</div>

				<div class="input-box3">					
					<input type="number" name="age" id="age" required>
					<label for="age">Age:</label>
				</div>

				<div class="input-box-option">
					<label for="gender">Gender:</label>
					<input type="radio" name="gender" id="gender" value="Male" required>Male
					<input type="radio" name="gender" id="gender" value="Female" required>Female

				<div class="input-box3">
					<input type="text" name="contact" id="contact" required>
					<label for="contact">Contact:</label>
				</div>

				<div class="input-box3">					
					<input type="email" name="email" id="email" required>
					<label for="email">Email:</label>
				</div>

				<div class="input-box3">
					<input type="text" name="address" id="address" required>
					<label for="address">Address:</label>
				</div>

				<!-- <input type="button" value="Next" class="button p1-link">
				<button class="button"><a href="#" class="p2-link">Next</a></button> 
				!-->

				<div class="input-box3">
					<input type="text" name="skill" id="skill" required>
					<label for="skill">Skill:</label>
				</div>

				<div class="input-box3">
					<input type="number" name="experience" id="experience" required>
					<label for="experience">How many years have you been a maid?:</label>
				</div>

				<div class="input-box-option">
					<label for="availability">Availability from</label>
					<select name="availability_start" id="availability_start" type="time" min="06:00" max="12:00">
						<option value="06:00">6 am</option>
						<option value="07:00">7 am</option>
						<option value="08:00">8 am</option>
						<option value="09:00">9 am</option>
						<option value="10:00">10 am</option>
						<option value="11:00">11 am</option>
						<option value="12:00">12 pm</option>
					</select>
				</div>

				<div class="input-box-option">
					<label for="availability">Availability until</label>
					<select name="availability_end" id="availability_end" type="time" min="14:00" max="20:00">
						<option value="14:00">2 pm</option>
						<option value="15:00">3 pm</option>
						<option value="16:00">4 pm</option>
						<option value="17:00">5 pm</option>
						<option value="18:00">6 pm</option>
						<option value="19:00">7 pm</option>
						<option value="20:00">8 pm</option>
					</select>
				</div>

				<div class="input-box3">
					<input type="file" name="profile-image" id="profile-image">
					<label for="profile-image">Profile Image:</label>
				</div>

				<input type="submit" value="Submit" class="button">
			</form>
		</div>
	</div>
</div>
<!--
	<div class ="form-box p2">
		<h2>Maid Application Form</h2>
		<form method="POST" action="maid_application" enctype="multipart/form-data">
			<div class="input-box3">
				<input type="text" name="skill" id="skill" required>
				<label for="skill">Skill:</label>
			</div>

			<div class="input-box3">
				<input type="number" name="experience" id="experience" required>
				<label for="experience">How many years have you been a maid?:</label>
			</div>

			<div class="input-box-option">
				<label for="availability">Availability from</label>
				<select name="availability_start" id="availability_start" type="time" min="06:00" max="12:00">
					<option value="06:00">6 am</option>
					<option value="07:00">7 am</option>
					<option value="08:00">8 am</option>
					<option value="09:00">9 am</option>
					<option value="10:00">10 am</option>
					<option value="11:00">11 am</option>
					<option value="12:00">12 pm</option>
				</select>
			</div>

			<div class="input-box-option">
				<label for="availability">Availability until</label>
				<select name="availability_end" id="availability_end" type="time" min="14:00" max="20:00">
					<option value="14:00">2 pm</option>
					<option value="15:00">3 pm</option>
					<option value="16:00">4 pm</option>
					<option value="17:00">5 pm</option>
					<option value="18:00">6 pm</option>
					<option value="19:00">7 pm</option>
					<option value="20:00">8 pm</option>
				</select>
			</div>

			<div class="input-box3">
				<input type="file" name="profile-image" id="profile-image">
				<label for="profile-image">Profile Image:</label>
			</div>

			<input type="submit" value="Submit" class="button">
		</form>
	</div>
</div>
!-->

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
				'experience' => $_POST['experience'].'years',
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
	redirect();
}
?>


