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
			<div class="inside-intro" id="maidpic">
				<img src='image\maid2.avif' class='h-100 w-100'/>
				<div class="word">
					<h2>Become A Maid</h2>
					<h4>A perfect place for you to join</h4>
					<a href="#">Learn More!</a>
				</div>
			</div>

			<div class="inside-intro">
				<img src='' class='h-100 w-100'/>
				<div class="word">
					<h2>Experince Our Service</h2>
					<h4>We Provide Proffesional And Afforable Price Service</h4>
					<a href="#">Learn More!</a>
				</div>
			</div>
				
			<div class="inside-intro">
				<img src='image/Kuala-Lumpur5.jpg' class='h-100 w-100'/>
				<div class="word"> 
					<h2>Only In Selangor</h2>
					<h4></h4>
				</div>
			</div>
		</section>

		<section class="service">
			<div class="inside-service position-relative">
				<img src='uploads/service/gardening2.jpg' class='h-100 w-100'/>
				<div class='position-absolute white-service-text'>
					<h2>House Gradening Service</h2>
					<h4>Maintenance & Beautification of your plants</h4>
				</div>
			</div>

			<div class="inside-service position-relative">
				<img src='uploads/service/baby-care2.jpg' class='h-100 w-100'/>
				<div class='position-absolute black-service-text'>
					<h2>Baby Caring Service</h2>
					<h4>Proffesional carer with love and passion to take care of baby</h4>
				</div>
			</div>

			<div class="inside-service position-relative">
				<img src='uploads/service/office-clean.jpg' class='h-100 w-100'/>
				<div class='position-absolute black-service-text'>
					<h2>Firm Cleaning Service</h2>
					<h4>A complete cleaning of your desired place</h4>
				</div>
			</div>

			<div class="inside-service position-relative">
				<img src='uploads/service/house-clean1.jpg' class='h-100 w-100'/>
				<div class='position-absolute white-service-text'>
					<h2>House Cleaning</h2>
					<h4>A thorough cleaning of your home from top to bottom</h4>
				</div>
			</div>
		</section>
	</section>
</section>