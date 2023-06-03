<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();

$db->table('booking')->where('service_id', $_GET['id'])->delete();
$db->table('service')->where('service_id', $_GET['id'])->delete();

setFlash('message', 'Service successfully deleted');

redirect('admin/manage?table=service');
?>
