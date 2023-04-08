<?php
if (authenticated()) {
    redirect('');
}

function successSignIn($id, $email, $userRole)
{
    $redirects = [
        ADMIN_ROLE => 'admin/manage',
        MEMBER_ROLE => 'user/dashboard',
		MAID_ROLE => 'maid/maid_profile'
    ];

    setSession([
        'loggedin' => true,
        'id' => $id,
        'email' => $email,
        'user_role' => $userRole
    ]);

    redirect($redirects[$userRole]);
}

$showMessage = false;

if (isPostMethod()) {
    $database = new Database();
    $email = $_POST['email'];
    $password = $_POST['password'];

    $user = $database->table('admin')
        ->where('admin_email', $email)
        ->where('admin_password', $password)
        ->row();

    if ($user !== null) {
        successSignIn($user['id'], $email, ADMIN_ROLE);
    }

    $user = $database->table('maid')
        ->where('maid_email', $email)
        ->where('maid_password', $password)
        ->row();
	
	if ($user !== null) {
        successSignIn($user['maid_id'], $email, MAID_ROLE);
    }

    $user = $database->table('member')
        ->where('member_email', $email)
        ->where('member_password', $password)
        ->row();
	
    if ($user !== null) {
        successSignIn($user['member_id'], $email, MEMBER_ROLE);
    }

    $showMessage = true;
}

$flash = getFlash('message');

?>

<div class="container">
    <div class="form-box-login">
        <h2 style="text-align: center">—————————— SIGN IN ——————————</h2>
        <form id="sign-in-form" method="POST">

            <?php if ($showMessage) : ?>
                <p>email or password is incorrect.</p>
            <?php endif; ?>

            <div>
                <span class="icon"><ion-icon name="mail-outline"></ion-icon></span>
                <label>Email: </label>
                <input type="text" placeholder="Enter Email" id="email" name="email" required />
            </div>

            <div>
                <span class="icon"><ion-icon name="lock-closed-outline"></ion-icon></span>
                <label>Password: </label>
                <input type="password" placeholder="Enter Password" id="password" name="password" required />
            </div>

            <div>
                <i>Not yet Registered? <a href="<?php echo route('authentication/sign-up'); ?>">Click Here!</a></i>
            </div>

            <div>
                <button type="submit" class="button">SIGN IN</button>
            </div>
        </form>
    </div>
</div>

<script type="module" src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js"></script>
<script nomodule src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.js"></script>

<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>

    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    const form = document.getElementById('sign-in-form');

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        if (emailInput.value.trim() === '') {
            alert('Email is empty!');

            return;
        }

        if (passwordInput.value.trim() === '') {
            alert('Password is empty!');

            return;
        }

        form.submit();
    })
</script>