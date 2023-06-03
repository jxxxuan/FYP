<?php
	if (isset($_GET['maid_id'])){
		$maid_id = $_GET['maid_id'];
		$is_self = false;
	}else if (!authenticated(MAID_ROLE)){//Check if user is logged in 
		setFlash('message', 'Please Sign In First!');
		redirect('authentication/sign-in');
	}else{
		$maid_id = getSession('id');
		$is_self = true;
	}
	
	require_once getView('layout.side-bar');
	//Get maid information
	$database = new Database();
	$maid = $database -> table('maid') -> where('maid_id',$maid_id) -> row();
	$member = $database -> table('member') -> where('member_id',$maid['member_id']) -> row();
    $bookings = $database -> table('booking') -> where('maid_id',$maid_id) -> rows();
?>

<div class='page'>
	<div class="mx-3 my-3">
		<img class="border border-circle" src=<?php echo asset($member['member_image']); ?> alt='user' width='200px' height='200px'>
		<h1 class="ml-3 mt-3"><?php echo $member['member_name']; ?></h1>
	</div>
	
	
	<section class="box">
		<h2>Personal Information</h2>
		<div class="mt-2">
			
			<p>Age: <?php echo $maid['maid_age']; ?></p>
			<p>Gender: <?php echo $maid['maid_gender']; ?></p>
			<p>Contact: <?php echo $member['member_contact']; ?></p>
			<p>Address: <?php echo $member['member_address']; ?></p>
		</div>
	</section>


	<section class="box">
		<h2>Skills and Experience</h2>
		<p>Skill: <?php echo $maid['maid_skill']; ?></p>
		<p>Experience: <?php echo $maid['maid_experience']; ?></p>
		
		<h2 class='mt-2'>Availability</h2>
		<p>Available from <?php echo date('H:i', strtotime($maid['availability_start'])); ?> to <?php echo date('H:i', strtotime($maid['availability_end'])); ?></p>
	</section>


	<section class="box">
		<h2>Time Slots</h2>
		
		<?php 
			$_GET['id'] = $maid_id;
			$_GET['mode'] = 'view';
			
			include_once getView('maid.time_slot');
		?>
	</section>


	<div class="box">
		<h2>Comment</h2>
		<table class="table-container">
		<thead>
			<tr>
				<th>Comment</th>
				<th>Rating</th>
			</tr>
		</thead>
			<tbody>
			<?php
				$database = new Database();
				$rows = $database -> table('rating') -> where('maid_id',getSession('id')) -> rows();

				foreach($rows as $row) {
					echo "<tr>";
					echo "<td>".$row['comment']."</td>";
					echo "<td>".$row['rating_score']."</td>";
					echo "</tr>";
				}
			?>
			</tbody>
		</table>
	</div>
	
	
	<?php
		if(!(getSession('user_role') == 1) && !$is_self){
	?>
			<div class='booking-section'>
				<a href='<?php echo route("member/booking")."?&maid_id=".$_GET["maid_id"];?>'
				 class='button booking-button'>BOOKING</a>
				<a href='' class='button booking-button'>ADD TO FAVOURITE MAID</a>
			</div>
	<?php
		}
	?>
</div>
<script src=<?php echo route('utils/side-bar.js')?>></script>
