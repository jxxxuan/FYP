<?php
	$db = new Database();
?>
<div class='container'>
	<h2>Service Plan</h2>
	<?php 
		if ($_GET['service_id'] == ''):
	?>
			<a href='<?php echo route("service/service_explorer");?>' class='button booking-button'>choose a service package</a>
	
	<?php 
		else:
			$service = $db->table('service')->where('service_id',$_GET['service_id'])->row();
	?>
			<table class='table-container'>
				<thead>
					<tr>
						<th>Title</th>
						<th>Type</th>
						<th>Description</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>{service_title}</td>
						<td>{service_type}</td>
						<td>{service_description}</td>
					</tr>
				</tbody>
			</table>
	<?php
		endif;
	?>
	
	<h2>Maid</h2>
	<?php 
		if ($_GET['maid_id'] == ''):
	?>
			<a href='<?php echo route("member/maid_explorer");?>' class='button booking-button'>choose a maid</a>
	
	<?php 
		else:
			$maid = $db->table('maid')->where('maid_id',$_GET['maid_id'])->row();
	?>
			<table class='table-container'>
				<thead>
					<tr>
						<th>Name</th>
						<th>Age</th>
						<th>Gender</th>
						<th>Contact</th>
						<th>Skill</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td><?php echo $maid['name'];?></td>
						<td><?php echo $maid['age'];?></td>
						<td><?php echo $maid['gender'];?></td>
						<td><?php echo $maid['contact'];?></td>
						<td><?php echo $maid['skill'];?></td>
					</tr>
				</tbody>
			</table>
	<?php
		endif;
	?>
	<a href="#" class="booking-button button">Confirm Booking</a>
</div>
