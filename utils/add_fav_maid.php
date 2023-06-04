<?php
	require_once 'helper.php';
	if(isset($_GET['id'])){
		session_start();
		require_once 'Database.php';
		$id = $_GET['id'];
		$db = new Database();
		echo $id;
		$db -> table('favourite_maid') -> insert(['member_id'=>getSession('id'),'maid_id'=>$id]);
		redirect('maid/maid_profile',$id);
	}

	//redirect('member/maid_explorer');
?>