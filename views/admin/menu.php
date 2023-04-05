<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('');
}
?>

<div>
    Admin ID: <?php echo getSession('username'); ?>
</div>
<div>
    <a href="<?php echo route('member/view'); ?>">Member</a>
    |
    <a href="<?php echo route('member/add'); ?>">Add</a>
</div>
<div>
    <a href="<?php echo route('staff/view'); ?>">Staff</a>
    |
    <a href="<?php echo route('staff/add'); ?>">Add</a>
</div>
<div>
    <a href="<?php echo route('order/view'); ?>">Order</a>
    |
    <a href="<?php echo route('order/add'); ?>">Add</a>
</div>
<div>
    <a href="<?php echo route('rating/view'); ?>">Rating</a>
</div>
<div>
    <a href="<?php echo route('contact-us/view'); ?>">Contact Us</a>
</div>