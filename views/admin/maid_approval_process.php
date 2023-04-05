<!DOCTYPE html>
<html>
<head>
	<title>Maid Approval Process</title>
</head>
<body>

<h1>Maid Approval Process</h1>

<?php
if (!authenticated(ADMIN_ROLE)) {
	redirect('');
}
if ($_SERVER["REQUEST_METHOD"] == "POST") {

	$id = mysqli_real_escape_string($connect, $_POST['application_id']);
	$status = mysqli_real_escape_string($connect, $_POST['background_check_status']);
	
	$sql = "UPDATE maid_application SET background_check_status='$status' WHERE application_id='$id'";

	if (mysqli_query($connect, $sql)) {
	    echo "Application status updated successfully!";
	} else {
	    echo "Error: " . $sql . "<br>" . mysqli_error($connect);
	}
	
	$sql = "INSERT INTO maid (application_id,name,age,gender,contact,email,address,experience,skill,availability_start,availability_end,image_file_path) 
			VALUES ('$id','$name', '$age', '$gender', '$contact', '$email','$address','$experience','$skill','$availability_start','$availability_end','$image_file_path')";
			
	if (mysqli_query($connect, $sql)) {
	    echo "Maid table updated successfully!";
	} else {
	    echo "Error: " . $sql . "<br>" . mysqli_error($connect);
	}
}
?>

<table>
	<tr>
		<th>Application_ID</th>
		<th>Name</th>
		<th>Age</th>
		<th>Gender</th>
		<th>Contact</th>
		<th>Email</th>
		<th>Address</th>
		<th>Skill</th>
		<th>Experience</th>
		<th>Availability</th>
		<th>Profile Image</th>
		<th>Background Check Status</th>
		<th>Action</th>
	</tr>

	<?php
		$sql = "SELECT * FROM maid_application";
		$result = mysqli_query($connect, $sql);

		if (mysqli_num_rows($result) > 0) {
			while($row = mysqli_fetch_assoc($result)) {
				echo "<tr>";
				echo "<td>".$row['application_id']."</td>";
				echo "<td>".$row['name']."</td>";
				echo "<td>".$row['age']."</td>";
				echo "<td>".$row['gender']."</td>";
				echo "<td>".$row['contact']."</td>";
				echo "<td>".$row['email']."</td>";
				echo "<td>".$row['address']."</td>";
				echo "<td>".$row['skill']."</td>";
				echo "<td>".$row['experience']."</td>";
				echo "<td>".$row['availability_start']." to ".$row['availability_end']."</td>";
				echo "<td><img src='".$row['image_file_path']."' width='100' height='100'></td>";
				
				echo "<td>".$row['background_check_status']."</td>";
				
				echo "<td>";
				echo "<form method='POST'>";
				echo "<input type='hidden' name='application_id' value='".$row['application_id']."'>";
				echo "<select name='background_check_status'>";
				echo "<option value='Pending' ".($row['background_check_status'] == 'Pending' ? 'selected' : '').">Pending</option>";
				echo "<option value='Approved' ".($row['background_check_status'] == 'Approved' ? 'selected' : '').">Approved</option>";
				echo "<option value='Declined' ".($row['background_check_status'] == 'Declined' ? 'selected' : '').">Declined</option>";
				echo "</select>";
				echo "<input type='submit' value='Update'>";
				echo "</form>";
				echo "</td>";
				echo "</tr>";
			}
		} else {
			echo "<tr><td colspan='12'>No maid applications found.</td></tr>";
		}
	?>
</table>

</body>
</html>
