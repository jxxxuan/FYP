<?php
$authenticated = authenticated();
$userRole = getSession('user_role');
?>

<header class="header bg-primary">
    <a href="<?php echo route(''); ?>">
        <img src="<?php echo asset('image/header/logo-mmu.png'); ?>" alt="MMU Logo" />
    </a>

    <nav class="d-flex" id="header-nav">
        <a class="nav-link" href="<?php echo route(''); ?>">HOME</a>
        <a class="nav-link" href="<?php echo route('info'); ?>">INFO</a>
        <a class="nav-link" href="<?php echo route('about-us'); ?>">ABOUT US</a>
        <a class="nav-link" href="<?php echo route('contact-us'); ?>">CONTACT US</a>
        <?php if ($authenticated) : ?>
            <?php if ($userRole === ADMIN_ROLE) : ?>
                <a class="nav-link" href="<?php echo route('admin/manage'); ?>">MANAGE SYSTEM</a>
            <?php elseif ($userRole === MEMBER_ROLE) : ?>
                <a class="nav-link" href="<?php echo route('comment-rating'); ?>">RATE US</a>
            <?php endif; ?>
        <?php endif; ?>
    </nav>

    <div class="ml-auto d-flex">
        <?php if ($authenticated) : ?>
            <img class="border border-circle" src="<?php echo asset('image/header/default-avatar.png'); ?>" alt="user" width="36" />
            <a class="nav-link" href="<?php echo route('authentication/sign-out'); ?>" style="align-self: center;">Sign Out</a>
        <?php else : ?>
            <a class="nav-link" href="<?php echo route('authentication/sign-in'); ?>">Sign In</a>
            |
            <a class="nav-link" href="<?php echo route('authentication/sign-up'); ?>">Sign Up</a>
        <?php endif; ?>
    </div>
</header>