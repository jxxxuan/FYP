
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
			$database = new Database();
			$rows = $database -> table('maid') -> rows();
			
			foreach($rows as $maid) {
				echo "<tr>";
				echo "<td>".$maid['name']."</td>";
				echo "<td>".$maid['age']."</td>";
				echo "<td>".$maid['gender']."</td>";
				echo "<td>".$maid['skill']."</td>";
				echo "<td>".$maid['experience'].' year'."</td>";
				echo "<td>".$maid['availability_start']." to ".$maid['availability_end']."</td>";
				echo "<td><img src='".$maid['image_file_path']."' width='100' height='100'></td>";
				echo "</tr>";
			}
		?>
	</table>
</body>