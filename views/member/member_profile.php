<?php 
    // Check if user is logged in
    if (!authenticated(MEMBER_ROLE)) {
		setFlash('message', 'Please Sign In First!');
		redirect('authentication/sign-in');
	}
    
    // Get maid information
	$database = new Database();
    $maid_id = getSession('id');
	$member = $database -> table('member') -> row();
    require_once getView('layout.side-bar');
?>
<div class='profile'>
	<div class="box">
		<div class="mx-3 my-3">
			<h4>Profile Picture</h4>
			<img src="<?php echo $member['member_image_file_path']; ?>" width="200" height="200">
			<p>Welcome, <?php echo $member['member_username']; ?>!</p>
		</div>
	</div>


	<div class="box">
	<h2>Personal Information</h2>
	<p>Name: <?php echo $member['member_username']; ?></p>
	<p>Contact: <?php echo $member['member_contact']; ?></p>
	<p>Address: <?php echo $member['member_address']; ?></p>
	<p>Favourite Maid: <?php echo $member['member_address']; ?></p>
	</div>

	<div class="box edit">
		<button><a href="#">Edit Profile</a></button>
		<button><a href="#">Logout</a></button>
	</div>
</div>
