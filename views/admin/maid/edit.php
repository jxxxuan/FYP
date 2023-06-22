<?php
$id = $_GET['id'] ?? null;

if ($id === null) {
    redirect('admin/manage?table=maid');
}


$db = new Database();
$maid = $db->table('maid')->where('maid_id', $id)->row();
$member = $db->table('member')->where('member_id', $maid['member_id'])->row();
echo $id;
if (isPostMethod()) {
    $result1 = $db->table('maid')
    ->where('maid_id', $id)
    ->update([
        'maid_age' => $_POST['maid_age'],
        'maid_gender' => $_POST['maid_gender'],
        'maid_experience' => $_POST['maid_experience'],
        'availability_start' => $_POST['availability_start'],
        'availability_end' => $_POST['availability_end'],
        'maid_skill' => $_POST['maid_skill'],
    ]);

	$result2 = $db->table('member')
    ->where('member_id', $maid['member_id'])
    ->update([
        'member_name' => $_POST['member_name'],
        'member_email' => $_POST['member_email'],
        'member_contact' => $_POST['member_contact'],
        'member_address' => $_POST['member_address'],
        //'member_image' => $_POST['member_image'],
    ]);


    if ($result1 && $result2) {
        setFlash('message', 'Member successful edit!');
    }

    redirect('admin/manage?table=maid');
}
require_once getView('layout.side-bar');
?>

<div class='box profile'>

	<section>
		<form method="post">
			<div class="input-box">
				<label for="name">Name:</label>
				<input type="text" id="member_name" name="member_name" value="<?php echo $member['member_name']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="email">Email:</label>
				<input type="email" id="member_email" name="member_email" value="<?php echo $member['member_email']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="contact">Contact:</label>
				<input type="text" id="member_contact" name="member_contact" value="<?php echo $member['member_contact']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="address">Address:</label>
				<input type="text" id="member_address" name="member_address" value="<?php echo $member['member_address']; ?>" required>
			</div>
			
			<!--
			<div class="input-box">
				<label for="image">Image:</label>
				<input type="text" id="member_image" name="member_image" value="<?php echo $member['member_image']; ?>" required>
			</div>
			-->
			
			<div class="input-box">
				<label for="age">Age:</label>
				<input type="text" id="maid_age" name="maid_age" value="<?php echo $maid['maid_age']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="gender">Gender:</label>
				<input type="text" id="maid_gender" name="maid_gender" value="<?php echo $maid['maid_gender']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="experience">Experience:</label>
				<input type="text" id="maid_experience" name="maid_experience" value="<?php echo $maid['maid_experience']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="availability_start">Availability Start:</label>
				<input type="time" id="availability_start" name="availability_start" value="<?php echo $maid['availability_start']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="availability_end">Availability End:</label>
				<input type="time" id="availability_end" name="availability_end" value="<?php echo $maid['availability_end']; ?>" required>
			</div>
			
			<div class="input-box">
				<label for="skill">Skill:</label>
				<input type="text" id="maid_skill" name="maid_skill" value="<?php echo $maid['maid_skill']; ?>" required>
			</div>
			
			<button class="button black-button" type="submit">Update Profile</button>
		</form>
	</section>

	<a href="<?php echo route('member/edit_profile'); ?>?change_psw=true">Change password</a>

</div>
	
	
	
	
