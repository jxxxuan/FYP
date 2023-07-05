<?php
	require_once 'helper.php';
	require_once 'Database.php';
    $db = new Database();
    
	if (isPostMethod()) {
		$member = $db -> table('member') -> where('member_id',$_POST['id']) -> row();
		if(isset($_FILES['member_image']) && $_FILES['member_image']['error'] === UPLOAD_ERR_OK) {
			$image_temp = $_FILES['member_image']['tmp_name'];
			$target_path = 'uploads/members/' . $_FILES['member_image']['name'];
			move_uploaded_file($image_temp, $target_path);
			$member_image = $target_path;
		} else {
			$member_image = $member['member_image'];
		}
		$result = $db->table('member')
			->where('member_id', $_POST['id'])
			->update([
				'member_name' => $_POST['name'],
				'member_email' => $_POST['email'],
				'member_contact' => $_POST['contact'],
				'member_address' => $_POST['address'],
				'member_image' => $member_image
			]);

		if ($result) {
			setFlash('message', 'Member Profile Successfully Edit!');
		}

		redirect('member/member_profile');
	}
?>