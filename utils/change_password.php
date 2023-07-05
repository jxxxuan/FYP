<?php
	require_once 'Database.php';
	require_once 'helper.php';
	session_start();
	
	if(isPostMethod()){
		$db = new Database();
		$current_password = $db -> table('member') -> where('member_id',getSession('member_id')) -> row()['member_password'];
		
		$valid = $_POST['newPassword'] === $_POST['confirmPassword'];
		if (!$valid) {
			echo "<script>confirm('New password and confirm password do not match.');
			window.history.back();</script>";
		}
		
		$valid = $valid && $current_password === $_POST['currentPassword'];
		if (!$valid) {
			echo "<script>confirm('Invalid current password.');
			window.history.back();</script>";
		}
		
		if($valid){
			$result = $db -> table('member') -> where('member_id',getSession('member_id')) -> update(['member_password' => $_POST['confirmPassword']]);
			if ($result) {
				echo "<script>confirm('Password changed successfully.');
				window.history.back();</script>";
			} else {
				echo "<script>confirm('Error occurred while changing the password.');
				window.history.back();</script>";
			}
		}
		
		
	}


?>