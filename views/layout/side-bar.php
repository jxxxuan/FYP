<div class="all">
<div class="sidebar close">
	<?php if ($userRole === ADMIN_ROLE) : ?>
		<div class='sb-item'>
			<a class="sb-link" href="<?php echo route('admin/manage/?table=member'); ?>">MEMBERS</a>
		</div>
		<div class='sb-item'>
			<a class="sb-link" href="<?php echo route('admin/manage/?table=maid'); ?>">MAIDS</a>
		</div>
		<div class='sb-item'>
			<a class="sb-link" href="<?php echo route('admin/manage/?table=service'); ?>">SERVICE</a>
		</div>
		<div class='menu-separator'></div>
		<div class='sb-item'>
			<a class="sb-link" href="<?php echo route('admin/manage/?table=member'); ?>">MEMBERS</a>
		</div>
		<div class='sb-item'>
			<a class="sb-link" href="<?php echo route('admin/manage/?table=maid'); ?>">MAIDS</a>
		</div>
		<div class='sb-item'>
			<a class="sb-link" href="<?php echo route('admin/manage/?table=service'); ?>">SERVICE</a>
		</div>
		
		<div class='menu-separator'></div>

	<?php elseif ($userRole === MEMBER_ROLE) : ?>
		<div class="head">
			<div class="image-text">
				<span class="image">
					<img src="<?php echo asset('image\16d57688-523e-4e70-9c5b-be3d10d53b1d.jfif'); ?>" alt="logo">
				</span>

				<div class="text header-text">
					<p>Title</p>
				</div>				
			</div>

			<i class='bx bx-chevron-left toggle'></i>
		</div>

		<div class="menu-bar">
			<div class="menu">
				<li class="search-box">
					<i class='bx bx-search icon'></i>
						<input type="search" placeholder="Search...">					
				</li>
				<ul class="menu-link">
					<li class="nav-link">
						<a href="#">
							<i class='bx bx-user icon'></i>
							<span class="text nav-text">Profile</span>
						</a>
					</li>
				</ul>
				<ul class="menu-link">
					<li class="nav-link">
						<a href="#">
							<i class='bx bxs-hand-up icon'></i>
							<span class="text nav-text">Booking</span>
						</a>
					</li>
				</ul>
				<ul class="menu-link">
					<li class="nav-link">
						<a href="#">
							<i class='bx bx-bar-chart icon'></i>
							<span class="text nav-text">Booking Status</span>
						</a>
					</li>
				</ul>
				<ul class="menu-link">
					<li class="nav-link">
						<a href="#">
							<i class='bx bx-history icon'></i>
							<span class="text nav-text">Booking History</span>
						</a>
					</li>
				</ul>
				<ul class="menu-link">
					<li class="nav-link">
						<a href="#">
							<i class='bx bxs-edit icon'></i>
							<span class="text nav-text">Edit Profile</span>
						</a>
					</li>
				</ul>
			</div>
		</div>

		<div class="bottom-cont">
			<li class="nav-link">
				<a href="<?php echo route('authentication/sign-out'); ?>">
					<i class='bx bx-log-out icon'></i>
					<span class="text nav-text">Logout</span>
				</a>
			</li>
		</div>


			<!-- <div class='sb-item'>
				<a class="sb-link" href="<?php echo route('member/booking_list'); ?>">Edit profile</a>
			</div>
			<div class='menu-separator'></div>
		
			<div class='sb-item'>
				<a class="sb-link" href="<?php echo route('member/booking_list'); ?>">Bookings</a>
			</div>
			<div class='menu-separator'></div> -->

	<?php endif; ?>
	<!-- <div class='authentication-block'>
		<a class="sb-link" href="<?php echo route('authentication/sign-out'); ?>" style="align-self: center;">Sign Out</a>
	</div> -->
</div>
</div>

<!-- <script>
	
	document.querySelector('.toggle-btn').addEventListener('click', function() {
	console.log("Hello, world!");
	document.querySelector('.sidebar').classList.toggle('open');
	//document.querySelector('.main-content').classList.toggle('open');
});
</script> -->