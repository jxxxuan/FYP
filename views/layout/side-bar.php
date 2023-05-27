
<div class="sidebar">
    <?php if ($userRole === ADMIN_ROLE) : ?>
		<div class="head">
            <div class="image-text">
                <span class="image">
                    <img src="<?php echo asset('image\16d57688-523e-4e70-9c5b-be3d10d53b1d.jfif'); ?>" alt="logo">
                </span>

                <div class="text header-text">
                    <p>Title</p>
                </div>
            </div>

        </div>

		<div class="menu-bar">
			<div class="menu">
				<button class='bx bx-chevron-left toggle-btn' onclick='open_sidebar()'></button>

				<li class="search-box">
					<i class='bx bx-search icon'></i>
						<input type="search" placeholder="Search...">					
				</li>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('admin/manage/?table=member'); ?>">
							<i class='bx bx-user icon'></i>
							<span class="text nav-text">Member List</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('admin/manage/?table=maid'); ?>">
							<i class='bx bxs-hand-up icon'></i>
							<span class="text nav-text">Maid List</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('admin/manage/?table=service'); ?>">
							<i class='bx bx-bar-chart icon'></i>
							<span class="text nav-text">Service List</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('admin/manage/?table=booking'); ?>">
							<i class='bx bx-history icon'></i>
							<span class="text nav-text">Booking List</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('admin/manage/?table=maidapplication'); ?>">
							<i class='bx bx-history icon'></i>
							<span class="text nav-text">Maid Application</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="#">
							<i class='bx bxs-edit icon'></i>
							<span class="text nav-text">Edit Profile</span>
						</a>
					</li>
				</ul>
			</div>
		</div>

       
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

        </div>

		<div class="menu-bar">
			<div class="menu">
				<button class='bx bx-chevron-left toggle-btn' onclick='open_sidebar()'></button>

				<li class="search-box">
					<i class='bx bx-search icon'></i>
						<input type="search" placeholder="Search...">					
				</li>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('member/member_profile'); ?>">
							<i class='bx bx-user icon'></i>
							<span class="text nav-text">Profile</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('member/booking'); ?>">
							<i class='bx bxs-hand-up icon'></i>
							<span class="text nav-text">Booking</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('member/member_profile'); ?>">
							<i class='bx bx-bar-chart icon'></i>
							<span class="text nav-text">Booking Status</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('member/member_profile'); ?>">
							<i class='bx bx-history icon'></i>
							<span class="text nav-text">Booking History</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="#">
							<i class='bx bxs-edit icon'></i>
							<span class="text nav-text">Edit Profile</span>
						</a>
					</li>
				</ul>
			</div>
		</div>

		<?php elseif ($userRole === MAID_ROLE) : ?>
        <div class="head">
            <div class="image-text">
                <span class="image">
                    <img src="<?php echo asset('image\16d57688-523e-4e70-9c5b-be3d10d53b1d.jfif'); ?>" alt="logo">
                </span>

                <div class="text header-text">
                    <p>Title</p>
                </div>
            </div>

        </div>

		<div class="menu-bar">
			<div class="menu">
				<button class='bx bx-chevron-left toggle-btn' onclick='open_sidebar()'></button>

				<li class="search-box">
					<i class='bx bx-search icon'></i>
						<input type="search" placeholder="Search...">					
				</li>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('member/member_profile'); ?>">
							<i class='bx bx-user icon'></i>
							<span class="text nav-text">Profile</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('member/booking'); ?>">
							<i class='bx bxs-hand-up icon'></i>
							<span class="text nav-text">Booking</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('member/member_profile'); ?>">
							<i class='bx bx-bar-chart icon'></i>
							<span class="text nav-text">Booking Status</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="<?php echo route('member/member_profile'); ?>">
							<i class='bx bx-history icon'></i>
							<span class="text nav-text">Booking History</span>
						</a>
					</li>
				</ul>
				<ul>
					<li class="menu-link">
						<a href="#">
							<i class='bx bxs-edit icon'></i>
							<span class="text nav-text">Edit Profile</span>
						</a>
					</li>
				</ul>
			</div>
		</div>
	<?php endif; ?>
	
	<div class="bottom-cont">
		<li class="menu-link">
			<a href="<?php echo route('authentication/sign-out'); ?>">
				<i class='bx bx-log-out icon'></i>
				<span class="text nav-text">Logout</span>
			</a>
		</li>
	</div>
</div>
        


<script src=<?php echo route("js/side-bar.js");?>></script>

