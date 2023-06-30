<?php
if (authenticated()) {
    redirect('');
}

function successSignIn($id, $email, $userRole, $name)
{
    $redirects = [
        ADMIN_ROLE => 'admin/manage?table=member',
        MEMBER_ROLE => 'member/member_profile',
		MAID_ROLE => 'maid/maid_profile'
    ];
	
	if($userRole != ADMIN_ROLE){
		$database = new Database();
		$member_id = $database -> table('maid') -> where('maid_id',$id) -> row()['member_id'];
		setSession([
			'member_id' => $member_id
		]);
	}
	
    setSession([
        'loggedin' => true,
        'id' => $id,
        'email' => $email,
        'user_role' => $userRole,
		'name' => $name,
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
        successSignIn($user['admin_id'], $email, ADMIN_ROLE,$user['name']);
    }

    $user = $database->table('member')
        ->where('member_email', $email)
        ->where('member_password', $password)
        ->row();
	
	if ($user !== null) {
		$name = $user['member_name'];
		$maid=$database->table('maid')
		->where('member_id',$user['member_id'])
		->row();
		
		if($maid !== null){
			successSignIn($maid['maid_id'], $email, MAID_ROLE,$name);
		}else{
			successSignIn($user['member_id'], $email, MEMBER_ROLE,$name);
		}
        
    }

    $showMessage = true;
}

$flash = getFlash('message');

?>
<div class="s">
	<div class="container1">
		<div class="form-box login">
			<h2>SIGN IN</h2>
			<form id="sign-in-form" method="POST">
				<?php if ($showMessage) : ?>
					<p>email or password is incorrect.</p>
				<?php endif; ?>

				<div class="input-box1">
					<span class="icon"><ion-icon name="mail-outline"></ion-icon></span>
					<input type="text" placeholder="" id="email" name="email" required />
					<label>Email: </label>
				</div>

				<div class="input-box1">
					<span class="icon"><ion-icon name="lock-closed-outline"></ion-icon></span>
					<input type="password" placeholder="" id="password" name="password" required />
					<label>Password: </label>
				</div>
				
				<div class="rmb-forgot">
					<label><input type="checkbox">Remember Me</label>
					<i><a href="#">Forget Password?</a></i>
				</div>

				<div>
					<button type="submit" class="button black-button">SIGN IN</button>
				</div>

				<div class="register">
					<i>Not Yet Registered? <a href="<?php echo route('authentication/sign-up'); ?>">Click Here!</a></i>
					<br>
					<i>Wanna Become a Maid? <a href="<?php echo route('views\maid_application.php'); ?>">Apply Here!</a></i>
				</div>
			</form>
		</div>
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