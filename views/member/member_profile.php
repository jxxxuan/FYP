<?php 
    // Check if user is logged in
    if (!authenticated(MEMBER_ROLE)) {
		setFlash('message', 'Please Sign In First!');
		redirect('authentication/sign-in');
	}
    
    // Get maid information
	$db = new Database();
    $maid_id = getSession('id');
	$member = $db -> table('member') -> where('member_id',getSession('id')) -> row();
    require_once getView('layout.side-bar');
?>
<div class='page'>
	<div class="box">
		<div class="mx-3 my-3">
			<h4>Profile Picture</h4>
			<img src="<?php echo $member['member_image']; ?>" width="200" height="200">
			<p>Welcome, <?php echo $member['member_name']; ?>!</p>
		</div>
	</div>

	<div class="box">
	<h2>Personal Information</h2>
	<p>Name: <?php echo $member['member_name']; ?></p>
	<p>Contact: <?php echo $member['member_contact']; ?></p>
	<p>Address: <?php echo $member['member_address']; ?></p>
	</div>

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

</div>
<script src=<?php echo route("utils/side-bar.js");?>></script>