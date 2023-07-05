<?php 
	require_once getView('layout.side-bar');
    // Check if user is logged in
    if (!authenticated(MEMBER_ROLE)) {
		setFlash('message', 'Please Sign In First!');
		redirect('authentication/sign-in');
	}
    
    // Get maid information
	$db = new Database();
    $maid_id = getSession('id');
	$member = $db -> table('member') -> where('member_id',getSession('id')) -> row();
?>
<div class='page'>
	<div class="box">
		<div class="mx-3 my-3">
			<img src="<?php echo route($member['member_image']); ?> " alt="member profile" width="200" height="200">
			<p>Welcome, <?php echo $member['member_name']; ?>!</p>
		</div>
	</div>

	<div class="box">
	<h2>Personal Information</h2>
	<p>Name: <?php echo $member['member_name']; ?></p>
	<p>Contact: <?php echo $member['member_contact']; ?></p>
	<p>Address: <?php echo $member['member_address']; ?></p>
	</div>


	<?php
	$num_fav = $db -> table('favourite_list') -> where('member_id',getSession('member_id')) -> numRows();
	if($num_fav > 0){
	?>
		<div class="box">
			<h2>Favourite Maid</h2>
			<div class='vertical-list'>
	
			<?php
				$fav_maids = $db -> table('favourite_list') -> where('member_id',getSession('id')) -> rows();
				
				foreach($fav_maids as $maid){
					$image = $db -> table('member') -> where('member_id',$maid['member_id']) -> row()['member_image'];
					echo "<a href=" . route('maid/maid_profile') . "?maid_id=" . $maid['maid_id'] . "> <img class='profile-image' src=" . asset($image). " width=150px height=150px> </a>";
				}
			?>
		
		
			</div>
		</div>
	<?php
	}
	?>
	
	<?php
	$num_fav = $db -> table('booking') -> where('member_id',getSession('member_id')) -> numRows();
	if($num_fav > 0){
	?>
		<div class="box">
			<h2>Bookings</h2>
			<?php
				$bookings = $db -> table('booking') -> where('member_id',getSession('member_id')) -> rows();
				$bookings = array_reverse($bookings);
				$bookings = array_slice($bookings,-5);
				foreach($bookings as $booking){
					$service = $db->table('service')->where('service_id', $booking['service_id'])->row();
			?>
					<a class='d-flex maid-name-card' href=<?php echo route('member/booing_status') . "?booking_id=" . $booking['booking_id'];?>>
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
			<a href=<?php echo route('member/view_bookings');?>>View all bookings</a>
		
		</div>
	<?php
	}
	?>
	

</div>
<script src=<?php echo route("utils/side-bar.js");?>></script>