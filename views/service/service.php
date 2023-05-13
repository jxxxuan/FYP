<?php
	//Get service information
	$database = new Database();
	$service = $database -> table('service') -> where('service_id',$_GET["service_id"]) -> row();
?>


<div class="mx-3 my-3">
	<img src=<?php echo asset($service['image_file_path']); ?> width='100%' height='200px'>
	<h1 class="ml-3 mt-3"><?php echo $service['service_title']; ?></h1>
</div>
<section class="box">
	<h2>Personal Information</h2>
	<div class="mt-2">
		
		<p>Age: <?php echo $service['service_type']; ?></p>
		<p>Gender: <?php echo $service['service_description']; ?></p>
	</div>
</section>

<!--
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
-->

<?php
	if(!(getSession('user_role') == 1)):
?>
		<div class='booking-section'>
			<a href='<?php echo route("member/booking")."?service_id=".$_GET["service_id"];?>'
			 class='button booking-button'>BOOKING</a>
			<a href='' class='button booking-button'>ADD TO FAVOURITE MAID</a>
		</div>
<?php
endif;
?>