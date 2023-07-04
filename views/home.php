<head>
	<title>Home Page</title>
</head>

<?php
	$database = new Database();
	$services = $database -> table('service') -> rows();
	$rowcount = count($services);
	
	$role = "";
	if(isset($_SESSION['user_role'])) {
		$role = $_SESSION['user_role'];
	}
	
	$memberrole = ($role == 3);

	
?>

<section class="wrapper container">
	<section class="intro">
		
		<div class="inside-intro">
			<img src='image/p2.jpg' class='intro-image h-100 w-100'/>
			<div class="word">
				<h2 class='fs-2 mb-2'>Experince Our Service</h2>
				<h4>We Provide Proffesional And Afforable Price Service</h4>

				<a href="member/maid_explorer"><button class = 'button black-button'>Book a maid</button></a>

				<?php if($memberrole): ?>
					<a href="application/maid_application"><button class = 'button black-button'>Apply As maid</button></a>
				<?php endif; ?>
			</div>
		</div>
		
	</section>
	
	<section class="box">
		<?php
			for($i = 0;$i < $rowcount;$i++){
		?>
				<a href=<?php echo route('service/service',$services[$i]['service_id'])?> class='none-decoration'>
					<div class="inside-service">
						<img src="<?php echo asset($services[$i]['service_image'])?>"/>
							<div class='service-text'>
								<h2><?php echo $services[$i]['service_title']?></h2>
								<br>
								<h4><?php echo $services[$i]['service_description']?></h4>
							</div>
					<!--
					<?php
						if($i % 2 == 0){
					?>
							<img src=<?php echo $services[$i]['service_image']?>/>
							<div class='service-text'>
								<h2><?php echo $services[$i]['service_title']?></h2>
								<br>
								<h4><?php echo $services[$i]['service_description']?></h4>
							</div>
					<?php
						}else{
					?>
							<div class='service-text'>
								<h2><?php echo $services[$i]['service_title']?></h2>
								<br>
								<h4><?php echo $services[$i]['service_description']?></h4>
							</div>
							<img src=<?php echo $services[$i]['service_image']?>/>
					<?php
						}
					?>
					-->
					</div>
				</a>
				<div class='seperator'></div>
		<?php
			}
		
		?>
	</section>
	
</section>