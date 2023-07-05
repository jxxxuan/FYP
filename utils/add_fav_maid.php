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
            'member_id' => getSession('id'),
            'maid_id' => $id,
        ]);

        redirect('maid/maid_profile?maid_id=' . $id);
    }
?>
