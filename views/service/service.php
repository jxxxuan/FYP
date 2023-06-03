<?php
	//Get service information
	$database = new Database();
	if(isset($_GET['id'])){
		$service = $database -> table('service') -> where('service_id',$_GET["id"]) -> row();
	}else{
		redirect('service/service_explorer');
	}
	
?>


<div>
	<img src=<?php echo asset($service['service_image']); ?> width='100%' height='800px'>
	
</div>
<section class="box">
	<div class="mt-2">
		<h1><?php echo $service['service_title']; ?></h1>
		<br>
		<h3>Type: <?php echo $service['service_type']; ?></h3>
		<br>
		<h4><?php echo $service['service_description']; ?></h4>
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
			<div class='separator'>
		</div>
<?php
endif;
?>