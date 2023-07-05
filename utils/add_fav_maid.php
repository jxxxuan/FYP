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

        $isfavourite = $db->table('favourite_list')
                        -> where('member_id',getsession('id'))
                        -> where('maid_id',$id)
                        -> numRows() >0;

        if(!$isfavourite){
            $db->table('favourite_list')->insert([
                'member_id' => getSession('member_id'),
                'maid_id' => $id,
            ]);
            
            echo '<script>alert("added successful!")</script>';
            echo '<script>window.location.href = "../maid/maid_profile?maid_id=' . $id . '";</script>';
        }else {
            echo '<script>alert("You already added!")</script>';
            echo '<script>window.location.href = "../member/maid_explorer";</script>';
        }
    }

?>
