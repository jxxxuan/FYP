<?php 
    // Check if user is logged in
    if (!authenticated(MAID_ROLE)) {
		setFlash('message', 'Please Sign In First!');
		redirect('authentication/sign-in');
	}
    
    // Get maid information
	$database = new Database();
    $maid_id = $_SESSION['id'];
	$maid = $database -> table('maid') -> row();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Maid Profile</title>
</head>
<body>
    <h1>Maid Profile</h1>
    <p>Welcome, <?php echo $maid['name']; ?>!</p>
    
    <h2>Personal Information</h2>
    <p>Name: <?php echo $maid['name']; ?></p>
    <p>Age: <?php echo $maid['age']; ?></p>
    <p>Gender: <?php echo $maid['gender']; ?></p>
    <p>Contact: <?php echo $maid['contact']; ?></p>
    <p>Address: <?php echo $maid['address']; ?></p>
    
    <h2>Skills and Experience</h2>
    <p>Skill: <?php echo $maid['skill']; ?></p>
    <p>Experience: <?php echo $maid['experience']; ?></p>
    
    <h2>Availability</h2>
    <p>Available from <?php echo $maid['availability_start']; ?> to <?php echo $maid['availability_end']; ?></p>
    
    <h2>Profile Picture</h2>
    <img src="<?php echo $maid['image_file_path']; ?>" width="300" height="300">
    
    <a href="edit_profile.php">Edit Profile</a>
    <br>
    <a href="logout.php">Logout</a>
</body>
</html>
