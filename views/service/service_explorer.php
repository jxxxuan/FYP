<?php
	$database = new Database();
	$rows = $database -> table('service') -> rows();
?>

<div>
<?php
foreach($rows as $service):
?>
	<a class='d-flex box maid-name-card' href="<?php echo route('service/service').'?id='.$service['service_id']; ?>">
		<div> <img src="<?php echo asset($service['service_image']);?>" width='100' height='100'> </div>
		
		<div class='mx-2 my-1'>
			<h3><?php echo $service['service_title']?></h3>
			<h4 class='mt-1'><?php echo $service['service_description']?></h4>
			<h4>Type: <?php echo $service['service_type']?></h4>
		</div>
	</a>
<?php
endforeach;
?>
</div>