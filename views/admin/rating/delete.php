<?php
    if (!authenticated(ADMIN_ROLE)) {
        redirect('authentication/sign-in');
    }
    $db = new Database();
    $ratingid = $_GET['id'];

    $db-> table('rating')-> where('rating_id',$ratingid)-> delete();

    if ($result) {
        setFlash('message', 'Successfully deleted');
    }
	redirect('admin/manage?table=rating');

?>