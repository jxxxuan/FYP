


<div class="sidebar">
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
		<a class="sb-link" href="<?php echo route('comment-rating'); ?>">RATE US</a>

	<?php endif; ?>

	<a class="sb-link" href="<?php echo route('authentication/sign-out'); ?>" style="align-self: center;">Sign Out</a>
  
</div>

<script>
document.querySelector('.toggle-btn').addEventListener('click', function() {
	console.log("Hello, world!");
	document.querySelector('.sidebar').classList.toggle('open');
	//document.querySelector('.main-content').classList.toggle('open');
});
</script>