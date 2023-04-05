<?php include("dataconnection.php"); ?>
<!DOCTYPE html>
<html>
<head>
	<title>Explore Maids Info</title>
</head>
<body>
	<header>
	</header>
		<h1>Explore Maids</h1>
		<table>
		<tr>
			<th>Name</th>
			<th>Age</th>
			<th>Gender</th>
			<th>Skill</th>
			<th>Experience</th>
			<th>Availability</th>
			<th>Profile Image</th>
		</tr>

		<?php
			$sql = "SELECT * FROM maid";
			$maid_result = mysqli_query($connect, $sql);

			if (mysqli_num_rows($maid_result) > 0) {
				while($maid = mysqli_fetch_assoc($maid_result)) {
					$app_id = $maid['application_id'];
					$sql = "SELECT * FROM maid_application WHERE application_id = $app_id";
					$maid_app_result = mysqli_query($connect, $sql);
					$maid_info = mysqli_fetch_assoc($maid_app_result);
					echo "<tr>";
					echo "<td>".$maid_info['name']."</td>";
					echo "<td>".$maid_info['age']."</td>";
					echo "<td>".$maid_info['gender']."</td>";
					echo "<td>".$maid_info['skill']."</td>";
					echo "<td>".$maid_info['experience'].' year'."</td>";
					echo "<td>".$maid_info['availability_start']." to ".$maid_info['availability_end']."</td>";
					echo "<td><img src='".$maid_info['image_file_path']."' width='100' height='100'></td>";
					echo "</tr>";
				}
			} else {
				echo "<tr><td colspan='12'>No maid applications found.</td></tr>";
			}
		?>
	</table>
</body>
</html>