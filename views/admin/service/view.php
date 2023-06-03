<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$services = $db->table('service')->rows();
$flash = getFlash('message');
?>
<a href="<?php echo route('admin/service/edit', $service['service_id']); ?>">Add</a>

<h2>SERVICE LIST</h2>
<table class="admin-table box">
	<thead>
		<tr>
			<th>Service ID</th>
			<th>Image</th>
			<th>Title</th>
			<th>Description</th>
			<th>Type</th>
		</tr>
	</thead>

	<tbody>
		<?php 
			foreach ($services as $service) {
		?>
				<tr>
					<td><?php echo $service['service_id']; ?></td>
					<td><img src="<?php echo route($service['service_image']); ?>" alt="Service Image" style="height:100px;width:100px;"></td>
					<td><?php echo $service['service_title']; ?></td>
					
					<td><?php echo $service['service_description']; ?></td>
					<td><?php echo $service['service_type']; ?></td>
					
					<td><a href="<?php echo route('admin/service/edit', $service['service_id']); ?>">Edit</a></td>
					<td><a href="<?php echo route('admin/service/delete', $service['service_id']); ?>" onclick="return confirmation();">Delete</a></td>
				</tr>
		<?php } ?>

	</tbody>
</table>

<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>

    function confirmation() {
        return confirm('Do you want to delete this record?');
    }
</script>
