<?php
	//Get service information
	$database = new Database();
	if(isset($_GET['id'])){
		$id = $_GET['id'];
		$service = $database -> table('service') -> where('service_id',$id) -> row();
	}else{
		redirect('service/service_explorer');
	}
	
?>

<div class='container'>
	<div>
		<img src=<?php echo asset($service['service_image']); ?> width='100%' height='800px'>
		
	</div>
	<section class="box">
		<div class="mt-2">
			<h1><?php echo $service['service_title']; ?></h1>
			<br>
			<h3>Type: <?php echo $service['service_type']; ?></h3>
			<br>
			<h4><?php echo $service['service_description']; ?></h4>
		</div>
	</section>

</div>

<?php
	if(!(getSession('user_role') == 1)):
?>
		<form class='booking-section' method='post' action=<?php echo route('member/booking')?>>
			<input type='hidden' name='booked_service_id' value=<?php echo $id;?>>
			<button class='button booking-button'>BOOKING</button>
		</form>
			
<?php
endif;
?>