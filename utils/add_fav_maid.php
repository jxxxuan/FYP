<?php
	require_once 'helper.php';
	if(getSession('user_role') == ADMIN_ROLE){
		redirect('authentication/sign-in');
	}
   
    if (isset($_POST['fav_maid_id'])) {
        require_once 'Database.php';
        session_start();
        $id = $_POST['fav_maid_id'];
        $db = new Database();


		$db->table('favourite_list')->insert([
			'member_id' => getSession('member_id'),
			'maid_id' => $id,
		]);
		
		echo '<script>alert("added successful!")</script>';
		echo '<script>window.location.href = "../maid/maid_profile?maid_id=' . $id . '";</script>';
        
    }

?>
