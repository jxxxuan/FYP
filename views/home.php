<head>
	<title>Home Page</title>
</head>

<?php
	$database = new Database();
	$rows = $database -> table('maid_application') -> where('background_check_status','pending') -> rows();
?>


<section class="all-home">
	<section class="wrapper">
		<section class="intro">
			<div class="inside-intro">
				
			</div>

			<div class="inside-intro">

			</div>
				
			<div class="inside-intro">
				<img src='image/Kuala-Lumpur5.jpg' class='h-100 w-100'/>
			</div>
		</section>

		<section class="service">
			<div class="inside-service">
				<img src='uploads/service/gardening2.jpg' class='h-100 w-100'/>
			</div>

			<div class="inside-service">
				<img src='uploads/service/baby-care2.jpg' class='h-100 w-100'/>
			</div>

			<div class="inside-service">
				<img src='uploads/service/office-clean.jpg' class='h-100 w-100'/>
			</div>

			<div class="inside-service">
				<img src='uploads/service/house-clean1.jpg' class='h-100 w-100'/>
			</div>
		</section>
	</section>
</section>