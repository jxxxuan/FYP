<?php
	require_once 'helper.php';
	require_once 'Database.php';

    if(isPostMethod()) {
		$db = new Database();
		$maid = $db -> table('maid') -> where('maid_id',$_POST['id']) -> row();
		$member = $db -> table('member') -> where('member_id',$maid['member_id']) -> row();
        if(isset($_FILES['member_image']) && $_FILES['member_image']['error'] === UPLOAD_ERR_OK) {
            $image_temp = $_FILES['member_image']['tmp_name'];
            $target_path = 'uploads/members/' . $_FILES['member_image']['name'];
            move_uploaded_file($image_temp, $target_path);
    
            $member_image = $target_path;
        } else {
            $member_image = $member['member_image'];
        }

        $result1 = $db->table('member')
            ->where('member_id', $maid['member_id'])
            ->update([
                'member_name' => $_POST['name'],
                'member_email' => $_POST['email'],
                'member_contact' => $_POST['contact'],
                'member_address' => $_POST['address'],
                'member_image' => $member_image
            ]);

        $result2 = $db->table('maid')
                ->where('maid_id', $_POST['id'])
                ->update([
                    'maid_age' => $_POST['age'],
                    'maid_gender' => $_POST['gender'],
                    'maid_experience' => $_POST['experience'],
                    'availability_start' => $_POST['availability_start'],
                    'availability_end' => $_POST['availability_end'],
                    'maid_skill' => $_POST['skill']
                ]);
                
        if($result1 && $result2){
            echo '<script>alert("Edit Successful!")</script>';
            echo '<script>window.location.href="../maid/maid_profile"</script>';
        } 

		
    }
?>