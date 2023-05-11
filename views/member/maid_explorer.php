<?php
	$database = new Database();
	$rows = $database -> table('maid') -> rows();
?>

<div>
<?php
foreach($rows as $maid):
?>
	<a class='d-flex box maid-name-card' href="<?php echo route('maid/maid_profile').'?maid_id='.$maid['maid_id']; ?>">
		<div> <img src="<?php echo asset($maid['image_file_path']);?>" width='100' height='100'> </div>
		
		<div class='mx-2 my-1'>
			<h3>"<?php echo $maid['name']?>"</h3>
			<h4 class='mt-1'>Age: "<?php echo $maid['age']?>"</h4>
			<h4>Gender: "<?php echo $maid['gender']?>"</h4>
		</div>
		
		<div class='mx-2 my-1'>
			<div>Skill: "<?php echo $maid['skill']?>"</div>
			<div class='mt-1'>Experience: "<?php echo $maid['experience']?>"</div>
			<div class='mt-1'>Availability time: "<?php echo date('H:i', strtotime($maid['availability_start']))." to ".date('H:i', strtotime($maid['availability_end']))?>"</div>
		</div>
			
	</a>
<?php
endforeach;
?>
</div>