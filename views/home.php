<head>
	<title>Home Page</title>
</head>

<?php
	$database = new Database();
	$services = $database -> table('service') -> rows();
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
		<?php
			for($i = 0;$i <= 3;$i++){
		?>
				<a href=<?php echo route('service/service')?>>
					<div class="inside-service">
						<img src=<?php echo $services[$i]['service_image']?>/>
						<div class='service-text'>
								<h2 class='none-decoration'><?php echo $services[$i]['service_title']?></h2>
								<br>
								<h4><?php echo $services[$i]['service_description']?></h4>
						</div>
					</div>
				</a>
				<div class='seperator'></div>
		<?php
			}
		
		?>
	</section>
	
</section>