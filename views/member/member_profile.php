<?php 
    /*// Check if user is logged in
    if (!authenticated(MEMBER_ROLE)) {
		setFlash('message', 'Please Sign In First!');
		redirect('authentication/sign-in');
	}
    
    // Get maid information
	$database = new Database();
    $maid_id = getSession('id');
	$member = $database -> table('member') -> row();
    */
?>
<!DOCTYPE html>
<html>
<head>
    <title>Member Profile</title>
</head>
<body>
    <h1>Member Profile</h1>
    <p>Welcome, <?php echo $member['member_username']; ?>!</p>
    
    <h2>Personal Information</h2>
    <p>Name: <?php echo $member['member_username']; ?></p>
    <p>Contact: <?php echo $member['member_contact']; ?></p>
    <p>Address: <?php echo $member['member_address']; ?></p>
    
    <h2>Profile Picture</h2>
    <img src="<?php echo $member['member_image_file_path']; ?>" width="300" height="300">
    
    <a href="edit_profile.php">Edit Profile</a>
    <br>
    <a href="logout.php">Logout</a>
</body>
</html>
