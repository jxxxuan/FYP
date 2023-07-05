<?php
	$db = new Database;
	$maid = $db->table('maid')->where('member_id',getsession('id'))->row();

	if(isset($maid)){
		setFlash('message','You already apply for maid, please wait for the response!');
		redirect('home');
	}
?>
    
<div class="s">
	<div class="container3">
		<div class="form-box p1">
			<h2>Maid Application Form</h2>
			<form method="POST" action="../utils/maid_application.php" enctype="multipart/form-data">
				
				<div class="input-box3">					
					<input type="number" name="age" id="age" min="0" required>
					<label for="age">Age:</label>
				</div>

				<div class="input-box-option">
					<label for="gender">Gender:</label>
					<input type="radio" name="gender" id="gender" value="Male" required>Male
					<input type="radio" name="gender" id="gender" value="Female" required>Female

				<div class="input-box3">
					<input type="text" name="skill" id="skill" required>
					<label for="skill">Skill:</label>
				</div>

				<div class="input-box3">
					<input type="text" name="experience" id="experience" min="0" required >
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

				<input type="submit" value="Submit" class="black-button button">
			</form>
		</div>
	</div>
</div>

