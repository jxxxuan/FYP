<?php
	if(!isset($_GET['maid_id']) && !authenticated(MAID_ROLE)){
		redirect('404');
	}else if(!authenticated()){//Check if user is logged in 
		setFlash('message', 'Please Sign In First!');
		redirect('authentication/sign-in');
	}else if(authenticated(ADMIN_ROLE) || authenticated(MEMBER_ROLE) || (authenticated(MAID_ROLE) && isset($_GET['maid_id']) && $_GET['maid_id'] != getSession('id'))){
		$id = $_GET['maid_id'];
		$is_self = false;
	}else{
		$id = getSession('id');
		$is_self = true;
	}
	
	require_once getView('layout.side-bar');
	//Get maid information
	$database = new Database();
	$maid = $database -> table('maid') -> where('maid_id',$id) -> row();
	$member = $database -> table('member') -> where('member_id',$maid['member_id']) -> row();
    $bookings = $database -> table('booking') -> where('maid_id',$id) -> rows();
?>

<div class='page'>
	<div class="mx-3 my-3">
		<img class="border border-circle" src=<?php echo route($member['member_image']); ?> alt='user' width='200px' height='200px'>
		<h1 class="ml-3 mt-3"><?php echo $member['member_name']; ?></h1>
	</div>
	
	
	<section class="box">
		<h2>Personal Information</h2>
		<div class="mt-2">
			
			<p>Age: <?php echo $maid['maid_age']; ?></p>
			<p>Gender: <?php echo $maid['maid_gender']; ?></p>
			<p>Contact: <?php echo $member['member_contact']; ?></p>
			<p>Email: <?php echo $member['member_email']; ?></p>
		</div>
	</section>


	<section class="box">
		<h2>Skills and Experience</h2>
		<p>Skill: <?php echo $maid['maid_skill']; ?></p>
		<p>Experience: <?php echo $maid['maid_experience'].' years'; ?></p>
		
		<h2 class='mt-2'>Availability</h2>
		<p>Available from <?php echo date('H:i', strtotime($maid['availability_start'])); ?> to <?php echo date('H:i', strtotime($maid['availability_end'])); ?></p>
	</section>


	<section class="box">
		
		<?php 
			$_GET['id'] = $id;
			$_GET['mode'] = 'view';
			
			include_once getView('maid.time_slot');
		?>
	</section>

	<?php
		if($is_self){
			$num_fav = $db -> table('favourite_list') -> where('member_id',getSession('member_id')) -> numRows();
			if($is_self && $num_fav > 0){
			?>
				<div class="box">
					<h2>Favourite Maid</h2>
					<div class='vertical-list'>
			
					<?php
						$fav_maids = $db -> table('favourite_list') -> where('member_id',getSession('member_id')) -> rows();
						
						foreach($fav_maids as $fav_maid){
							$maid = $db -> table('maid') -> where('maid_id',$fav_maid['maid_id']) -> row();
							$image = $db -> table('member') -> where('member_id',$maid['member_id']) -> row()['member_image'];
							echo "<a href=" . route('maid/maid_profile') . "?maid_id=" . $maid['maid_id'] . "> <img class='profile-image' src=" . asset($image). " width=150px height=150px> </a>";
						}
					?>
				
				
					</div>
				</div>
			<?php
			}
		}
	?>
	
	<?php
	if($is_self){
		$num_booking = $db->table('booking')->where('member_id', getSession('member_id'))->numRows();
		if($num_booking > 0){
?>
			<div class="box">
				<h2>Bookings as a member</h2>
				<?php
					$bookings = $db->table('booking')->where('member_id', getSession('member_id'))->rows();
					$bookings = array_reverse($bookings);
					$bookings = array_slice($bookings, -5);
					foreach($bookings as $booking){
						$service = $db->table('service')->where('service_id', $booking['service_id'])->row();
						if($booking['booking_status'] != 'Rejected'){
				?>
						
							<a class='d-flex maid-name-card' href=<?php echo route('member/booking_status') . "?booking_id=" . $booking['booking_id'];?>>
								<div class='mx-2 my-1' style="min-width:400px;">
									<h3><?php echo $service['service_type'] ?></h3>
									<h4 class='mt-1'>Service Title: <?php echo $service['service_title'] ?></h4>
								</div>
								
								<div class='mx-2 my-1'>
									<div>Booking Time: <?php echo $booking['booking_datetime'] ?></div>
									<div class='mt-1'>Arrive Time: <?php echo $booking['booking_arrive_datetime'] ?></div>
									<div class='mt-1'>Leave Time: <?php echo $booking['booking_leave_datetime'] ?></div>
								</div>

								<div class='mx-2 my-1'>
									<div>Booking Status: <?php echo $booking['booking_status'] ?></div>
								</div>
							</a>
						<?php }else{?>
							<div class='d-flex maid-name-card'>
								<div class='mx-2 my-1' style="min-width:400px;">
									<h3><?php echo $service['service_type'] ?></h3>
									<h4 class='mt-1'>Service Title: <?php echo $service['service_title'] ?></h4>
								</div>
								
								<div class='mx-2 my-1'>
									<div>Booking Time: <?php echo $booking['booking_datetime'] ?></div>
									<div class='mt-1'>Arrive Time: <?php echo $booking['booking_arrive_datetime'] ?></div>
									<div class='mt-1'>Leave Time: <?php echo $booking['booking_leave_datetime'] ?></div>
								</div>

								<div class='mx-2 my-1'>
									<div>Booking Status: <?php echo $booking['booking_status'] ?></div>
								</div>
							</div>
						<?php
						}
					}
				?>
				<a href=<?php echo route('member/view_bookings'); ?>>View all bookings</a>
			</div>
	<?php
		}
	}
?>

	
	<?php
	if($is_self){
		$num_booking = $db -> table('booking') -> where('maid_id',getSession('id')) -> numRows();
		if($num_booking > 0){
	?>
			<div class="box">
				<h2>Bookings as a maid</h2>
				<?php
					$bookings = $db -> table('booking') -> where('maid_id',getSession('id')) -> rows();
					$bookings = array_reverse($bookings);
					$bookings = array_slice($bookings,-5);
					foreach($bookings as $booking){
						$service = $db->table('service')->where('service_id', $booking['service_id'])->row();
				?>
						<a class='d-flex maid-name-card' href=<?php echo route('maid/booking_status') . "?booking_id=" . $booking['booking_id'];?>>
							<div class='mx-2 my-1' style="min-width:400px;">
								<h3><?php echo $service['service_type']?></h3>
								<h4 class='mt-1'>Service Title: <?php echo $service['service_title'] ?></h4>
							</div>
							
							<div class='mx-2 my-1'>
								<div>Booking Time: <?php echo $booking['booking_datetime'] ?></div>
								<div class='mt-1'>Arrive Time: <?php echo $booking['booking_arrive_datetime']?></div>
								<div class='mt-1'>Leave Time: <?php echo $booking['booking_leave_datetime'] ?></div>
							</div>

							<div class='mx-2 my-1'>
								<div>Booking Status: <?php echo $booking['booking_status'] ?></div>
							</div>
						</a>
				<?php
					}
				?>
				<a href=<?php echo route('maid/view_bookings');?>>View all bookings</a>
			
			</div>
	<?php
		}
	}
	?>
	
	<div class="box">
		<h2>Comment</h2>
		<table class='comment-table text-center'>
		<thead>
			<tr>
				<th>Comment</th>
				<th>Rating</th>
			</tr>
		</thead>
			<tbody>
			<?php
				$database = new Database();
				$rows = $database -> table('rating') -> where('maid_id',$id) -> rows();

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
				<form method='post' action=<?php echo route('member/booking')?>>
					<input type='hidden' name='booked_maid_id' value=<?php echo $id;?>>
					<button class='button booking-button'>BOOKING</button>
				</form>
			<?php	
			$added = $db -> table('favourite_list') -> where('member_id',getSession('member_id')) -> where('maid_id',$id) -> numRows();
			if(!$added){
			?>
				<form class='booking-section' method='post' action='../utils/add_fav_maid.php'>
					<input type='hidden' name='fav_maid_id' value=<?php echo $id;?>>
					<button class='button booking-button'>ADD TO FAVOURITE LIST</button>
				</form>
			</div>
			<?php
			}else{
			?>
				<form class='booking-section' method='post' action='../utils/remove_fav_maid.php'>
					<input type='hidden' name='fav_maid_id' value=<?php echo $id;?>>
					<button class='button booking-button'>REMOVE FROM FAVOURITE LIST</button>
				</form>
			<?php
			}
			?>
	<?php
		}
	?>
</div>
<script src=<?php echo route('utils/side-bar.js')?>></script>
