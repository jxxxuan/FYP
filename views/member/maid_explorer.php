<?php
	$database = new Database();
	$maids = $database -> table('maid') -> where('maid_background_check_status','Approved') -> rows();
?>

<div>
<?php
foreach($maids as $maid):
	$member = $database -> table('member') -> where('member_id',$maid['member_id']) -> row();
?>
	<a class='d-flex box maid-name-card' href="<?php echo route('maid/maid_profile').'?maid_id='.$maid['maid_id']; ?>">
		<div> <img src="<?php echo asset($member['member_image']);?>" width='100' height='100' > </div>
		
		<div class='maid-info mx-2 my-1'>
			<h3><?php echo $member['member_name']?></h3>
			<h4 class='mt-1'>Age: <?php echo $maid['maid_age']?></h4>
			<h4>Gender: <?php echo $maid['maid_gender']?></h4>
		</div>
		
		<div class='mx-2 my-1'>
			<div>Skill: <?php echo $maid['maid_skill']?></div>
			<div class='mt-1'>Experience: <?php echo $maid['maid_experience']?></div>
			<div class='mt-1'>Availability time: <?php echo date('H:i', strtotime($maid['availability_start']))." to ".date('H:i', strtotime($maid['availability_end']))?></div>
		</div>
			
	</a>
<?php
endforeach;
?>
</div>