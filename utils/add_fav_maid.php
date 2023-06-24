<?php
    require_once 'helper.php';

    if (isset($_POST['id'])) {
        require_once 'Database.php';
		session_start();
        $id = $_POST['id'];
        $db = new Database();
        $db->table('favourite_list')->insert([
            'member_id' => getSession('id'),
            'maid_id' => $id,
        ]);

        // Redirect to the appropriate page
        redirect('maid/maid_profile?maid_id=' . $id);
    }
?>
