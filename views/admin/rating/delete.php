<?php
    if (!authenticated(ADMIN_ROLE)) {
        redirect('authentication/sign-in');
    }
    $db = new Database();
    $ratingid = $_GET['id'];

    $result = $db-> table('rating')-> where('rating_id',$ratingid)-> delete();

    if ($result) {
        echo '<script>alert("Delete Successfully!")</script>';
        echo '<script>window.location.href="../manage?table=rating"</script>';   
    }else
    {
        echo '<script>alert("Delete Fail!")</script>';
        echo '<script>window.location.href="../manage?table=rating"</script>';   
    }
   

?>