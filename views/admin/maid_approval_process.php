<head>
	<title>Maid Approval Process</title>
</head>

<h1>Maid Approval Process</h1>

<?php
if (!authenticated(ADMIN_ROLE)) {
	redirect('');
}
if (isPostMethod()) {
	$database = new Database();
	$database -> table('maid_application') -> where('application_id',$_POST['application_id']) ->update(['background_check_status' => $_POST['background_check_status']]);
}
?>
<div class='table-container'>
	<table border='1 '>
		<tr>
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
			<th>Status</th>
			<th>Action</th>
		</tr>

		<?php
			$database = new Database();
			$rows = $database -> table('maid_application') -> where('background_check_status','pending') -> rows();

			foreach($rows as $row) {
				echo "<tr>";
				echo "<td class='table-item'>".$row['name']."</td>";
				echo "<td class='table-item'>".$row['age']."</td>";
				echo "<td class='table-item'>".$row['gender']."</td>";
				echo "<td class='table-item'>".$row['contact']."</td>";
				echo "<td class='table-item'>".$row['email']."</td>";
				echo "<td class='table-item'>".$row['address']."</td>";
				echo "<td class='table-item'>".$row['skill']."</td>";
				echo "<td class='table-item'>".$row['experience']." years"."</td>";
				echo "<td class='table-item'>".$row['availability_start']." to ".$row['availability_end']."</td>";
				echo "<td class='table-item'><img src=".asset('' . $row['image_file_path'])." style='width:100px; height:100px;'></td>";
				
				echo "<td class='table-item'>".$row['background_check_status']."</td>";
				
				echo "<td class='table-item'>";
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
		?>
	</table>
</div>
