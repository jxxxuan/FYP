<head>
	<title>Maid Approval Process</title>
</head>

<?php
if (!authenticated(ADMIN_ROLE)) {
	redirect('');
}
if (isPostMethod()) {
	$database = new Database();
	$database -> table('maid_application') -> where('application_id',$_POST['application_id']) ->update(['background_check_status' => $_POST['background_check_status']]);
}
?>
<div class='test'>
	<h2>
		MAID APPLICATION
	</h2>
	<table class='table-container'>
		<thead>
			<tr>
				<th>Profile Image</th>
				<th>Name</th>
				<th>Age</th>
				<th>Gender</th>
				<th>Contact</th>
				<th>Email</th>
				<th>Skill</th>
				<th>Availability</th>
				<th>Action</th>
			</tr>
		</thead>
		<tbody>
			<?php
				$database = new Database();
				$rows = $database -> table('maid_application') -> where('background_check_status','pending') -> rows();

				foreach($rows as $row) {
					echo "<tr>";
					echo "<td><img src=".asset('' . $row['image_file_path'])." style='width:100px; height:100px;'></td>";
					echo "<td>".$row['name']."</td>";
					echo "<td>".$row['age']."</td>";
					echo "<td>".$row['gender']."</td>";
					echo "<td>".$row['contact']."</td>";
					echo "<td>".$row['email']."</td>";
					echo "<td>".$row['skill']."</td>";
					$availability_start = date('H:i', strtotime($row['availability_start']));
					$availability_end = date('H:i', strtotime($row['availability_end']));
					echo "<td>".$availability_start." to ".$availability_end."</td>";
					
					
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
		</tbody>
	</div>
</table>
