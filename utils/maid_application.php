<?php
require_once 'helper.php';
require_once 'Database.php';
session_start();

if (isPostMethod()) {
	$background_check_status = "pending";
	
	$database = new Database();
	$memberid = getsession('id');
	$id = $database -> table('maid') -> insert([             
                'maid_age' => $_POST['age'],
				'maid_gender' => $_POST['gender'],
				'maid_experience' => $_POST['experience'].'years',
                'maid_skill' => $_POST['skill'],
				'member_id' => $memberid,
				'availability_start' => $_POST['availability_start'],
                'availability_end' => $_POST['availability_end'],
				'maid_background_check_status' => $background_check_status
            ]);
	
	echo "<script>alert('Application submitted successfully.');
			window.history.back();</script>";
}
?>