<?php
	if (isset($_GET['maid_id'])){
		$maid_id = $_GET['maid_id'];
	}else if (!authenticated(MAID_ROLE)){//Check if user is logged in 
		setFlash('message', 'Please Sign In First!');
		redirect('authentication/sign-in');
	}else{
		$maid_id = $_SESSION['id'];
	}
	
	//Get maid information
	$database = new Database();
	$maid = $database -> table('maid') -> where('maid_id',$maid_id) -> row();
    $bookings = $database -> table('booking') -> where('maid_id',$maid_id) -> rows();
?>


<div class="mx-3 my-3">
	<img class="border border-circle" src=<?php echo asset($maid['image_file_path']); ?> alt='user' width='200px' height='200px'>
	<h1 class="ml-3 mt-3"><?php echo $maid['name']; ?></h1>
</div>
<section class="box">
	<h2>Personal Information</h2>
	<div class="mt-2">
		
		<p>Age: <?php echo $maid['age']; ?></p>
		<p>Gender: <?php echo $maid['gender']; ?></p>
		<p>Contact: <?php echo $maid['contact']; ?></p>
		<p>Address: <?php echo $maid['address']; ?></p>
	</div>
</section>

<section class="box">
	<h2>Skills and Experience</h2>
	<p>Skill: <?php echo $maid['skill']; ?></p>
	<p>Experience: <?php echo $maid['experience']; ?></p>
	
	<h2 class='mt-2'>Availability</h2>
	<p>Available from <?php echo date('H:i', strtotime($maid['availability_start'])); ?> to <?php echo date('H:i', strtotime($maid['availability_end'])); ?></p>
</section>

<section class="box">
	<h2>Time Slots</h2>
	
	<?php 
		$_GET['maid_id'] = $maid_id;
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
	if(!(getSession('user_role') == 1)):
?>
		<div class='booking-section'>
			<a href='<?php echo route("member/booking")."?&maid_id=".$_GET["maid_id"];?>'
			 class='button booking-button'>BOOKING</a>
			<a href='' class='button booking-button'>ADD TO FAVOURITE MAID</a>
		</div>
<?php
endif;
?>