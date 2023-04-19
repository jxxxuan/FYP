
<head>
	<title>Explore Maids Info</title>
</head>
<body>
	
	<h1>Explore Maids</h1>
	

	<?php
		$database = new Database();
		$rows = $database -> table('maid') -> rows();
		
		echo "<div>";
		foreach($rows as $maid) {
			echo "<div class='d-flex box'>";
				echo "<div> <img src=".asset($maid['image_file_path'])." width='100' height='100'> </div>";
				
				echo "<div class='mx-2 my-1'>";
					echo "<h3>".$maid['name']."</h3>";
					echo "<h4 class='mt-1'>Age: ".$maid['age']."</h4>";
					echo "<h4>Gender: ".$maid['gender']."</h4>";
				echo "</div>";
				
				echo "<div class='mx-2 my-1'>";
					echo "<div>Skill: ".$maid['skill']."</div>";
					echo "<div class='mt-1'>Experience: ".$maid['experience']."</div>";
					echo "<div class='mt-1'>Availability time: ".date('H:i', strtotime($maid['availability_start']))." to ".date('H:i', strtotime($maid['availability_end']))."</div>";
				echo "</div>";
				
			echo "</div>";
		}
		echo "</div>";
	?>
</body>