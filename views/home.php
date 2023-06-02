<head>
	<title>Home Page</title>
</head>

<?php
	$database = new Database();
	$rows = $database -> table('service') -> rows();
?>

<section class="wrapper container">
	<section class="intro">
		<!--
		<div class="inside-intro">
			<img src='image\20Land-jumbo.webp' class='intro-image h-100 w-100'/>
			<div class="word">
				<h2 class='fs-2 mb-2'>Become A Maid</h2>
				<h4>A perfect place for you to join</h4>
				<a href="maid_application">Learn More!</a>
			</div>
		</div>
		-->

		<div class="inside-intro">
			<img src='image/p2.jpg' class='intro-image h-100 w-100'/>
			<div class="word">
				<h2 class='fs-2 mb-2'>Experince Our Service</h2>
				<h4>We Provide Proffesional And Afforable Price Service</h4>
				<button class = 'button black-button'>Book a maid</button>
			</div>
		</div>
			
		<!--
		<div class="inside-intro">
			<img src='image/Kuala-Lumpur5.jpg' class='intro-image h-100 w-100'/>
			<div class="word"> 
				<h2 class='fs-2 mb-2'>Only In Selangor</h2>
				<h4></h4>
			</div>
		</div>
		-->
	</section>
	
	<section class="box">
		<div class="inside-service">
			<img src='uploads/service/gardening2.jpg'/>
			<div class='black-service-text'>
				<h2>House Gradening Service</h2>
				<h4>Maintenance & Beautification of your plants</h4>
			</div>
		</div>

		<div class="inside-service">
			<img src='uploads/service/baby-care2.jpg'/>
			<div class='black-service-text'>
				<h2>Baby Caring Service</h2>
				<h4>Proffesional carer with love and passion to take care of baby</h4>
			</div>
		</div>

		<div class="inside-service">
			<img src='uploads/service/office-clean.jpg'/>
			<div class='black-service-text'>
				<h2>Firm Cleaning Service</h2>
				<h4>A complete cleaning of your desired place</h4>
			</div>
		</div>

		<div class="inside-service">
			<img src='uploads/service/house-clean1.jpg'/>
			<div class='black-service-text'>
				<h2>House Cleaning</h2>
				<h4>A thorough cleaning of your home from top to bottom</h4>
			</div>
		</div>
	</section>
	
</section>