<?php
    require_once getView('layout.side-bar');
    $db = new Database();
    $maid = $db -> table('maid') -> where('maid_id',getSession('id')) -> row();
    $member = $db -> table('member') -> where('member_id',$maid['member_id']) -> row();
?>

<div class='page'>
	<div class='box'>

	<?php
		if(isset($_GET['change_psw']) && $_GET['change_psw'] == 'true'):
	?>
			<section>
				<form action="change_password.php" method="post" >
					<input type='hidden' name='id' value=<?php echo getSession('id');?>>
				
					<div class="input-box">
						<label for="current-password">Current Password:</label>
						<input type="password" id="current-password" name="currentPassword" required>
					</div>
					
					<div class="input-box">
						<label for="new-password">New Password:</label>
						<input type="password" id="new-password" name="newPassword" required>
					</div>
					
					<div class="input-box">
						<label for="confirm-password">Confirm Password:</label>
						<input type="password" id="confirm-password" name="confirmPassword" required>
					</div>
					
					<button type="submit">Change Password</button>
				</form>
			</section>
	<?php
		else:
	?>
        <section>
            <h2>Personal Information</h2>
            <form action="../utils/maid_edit_profile.php" method="post" enctype="multipart/form-data">
                <input type='hidden' name='id' value=<?php echo getSession('id');?>>
                <div class="input-box">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" value="<?php echo $member['member_name']?>" required>
                </div>
                
                <div class="input-box">
                    <label for="phone">Phone:</label>
                    <input type="tel" id="phone" name="contact" value="<?php echo $member['member_contact']?>" required>
                </div>
                
                <div class="input-box">
                    <label for="address">Address:</label>
                    <input type="text" id="address" name="address" value="<?php echo $member['member_address']?>" required>
                </div>


                <div class="input-box">
                    <label for="age">Age:</label>
                    <input type="text" id="age" name="age" value="<?php echo $maid['maid_age']?>" required>
                </div>

                <div class="input-box">
                    <label for="gender">Gender:</label>
                    <input type="text" id="gender" name="gender" value="<?php echo $maid['maid_gender']?>" required>
                </div>

                <div class="input-box">
                    <label for="experince">Experince (years):</label>
                    <input type="number" id="experince" name="experience" value="<?php echo $maid['maid_experience'];?>" required>
                </div>

                <div class="input-box">
                    <label for="skill">Skill:</label>
                    <input type="text" id="skill" name="skill" value="<?php echo $maid['maid_skill']?>" required>
                </div>

                <div class="input-box-option">
				  <label for="availability">Availability from</label>
				  <select name="availability_start" id="availability_start" type="time" min="06:00" max="12:00">
					<option value="06:00"<?php if ($maid['availability_start'] === '06:00:00') echo ' selected'; ?>>6 am</option>
					<option value="07:00"<?php if ($maid['availability_start'] === '07:00:00') echo ' selected'; ?>>7 am</option>
					<option value="08:00"<?php if ($maid['availability_start'] === '08:00:00') echo ' selected'; ?>>8 am</option>
					<option value="09:00"<?php if ($maid['availability_start'] === '09:00:00') echo ' selected'; ?>>9 am</option>
					<option value="10:00"<?php if ($maid['availability_start'] === '10:00:00') echo ' selected'; ?>>10 am</option>
					<option value="11:00"<?php if ($maid['availability_start'] === '11:00:00') echo ' selected'; ?>>11 am</option>
					<option value="12:00"<?php if ($maid['availability_start'] === '12:00:00') echo ' selected'; ?>>12 pm</option>
				  </select>
				</div>

				<div class="input-box-option">
				  <label for="availability">Availability until</label>
				  <select name="availability_end" id="availability_end" type="time" min="14:00" max="20:00">
					<option value="14:00"<?php if ($maid['availability_end'] === '14:00:00') echo ' selected'; ?>>2 pm</option>
					<option value="15:00"<?php if ($maid['availability_end'] === '15:00:00') echo ' selected'; ?>>3 pm</option>
					<option value="16:00"<?php if ($maid['availability_end'] === '16:00:00') echo ' selected'; ?>>4 pm</option>
					<option value="17:00"<?php if ($maid['availability_end'] === '17:00:00') echo ' selected'; ?>>5 pm</option>
					<option value="18:00"<?php if ($maid['availability_end'] === '18:00:00') echo ' selected'; ?>>6 pm</option>
					<option value="19:00"<?php if ($maid['availability_end'] === '19:00:00') echo ' selected'; ?>>7 pm</option>
					<option value="20:00"<?php if ($maid['availability_end'] === '20:00:00') echo ' selected'; ?>>8 pm</option>
				  </select>
				</div>
                
                <div class="input-box">
                    <label for="profile-image">Profile Image:</label>
                    <img src="<?php echo route($member['member_image']); ?>" alt="Current Profile Image" width="100px" height="100px">
                    <input type="file" id="member_image" name="member_image">
                </div>
                
                <button class="button black-button" type="submit">Update Profile</button>
                
            </form>

        </section>
        <a href="<?php echo route('member/edit_profile'); ?>?change_psw=true">Change password</a>
	<?php
		endif;
	?>

	</div>
</div>


	
<script src=<?php echo route("utils/side-bar.js");?>></script>
	