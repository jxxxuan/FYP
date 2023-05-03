<?php 

if (!authenticated(ADMIN_ROLE)) {
    redirect('');
}

?>

<div>
    Admin ID: <?php echo getSession('username'); ?>
</div>
<div>
    <a href="<?php echo route('admin/member/view'); ?>">Member</a>
</div>
<div>
    <a href="<?php echo route('admin/booking/view'); ?>">Booking</a>
</div>
<div>
    <a href="<?php echo route('admin/maid/view'); ?>">Maid</a>
</div>