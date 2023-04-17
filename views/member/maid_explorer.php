
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
				
				echo "<div class='mx-2'>";
					echo "<h2>".$maid['name']."</h2>";
					echo "<div>Age: ".$maid['age']."</div>";
					echo "<div>Gender: ".$maid['gender']."</div>";
					echo "<div>Skill: ".$maid['skill']."</div>";
					echo "<div>Experience: ".$maid['experience'].' year'."</div>";
					
				echo "</div>";
			echo "</div>";
		}
	?>
</body>