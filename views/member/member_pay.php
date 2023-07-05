<?php 
    require_once getView('layout.side-bar');
    if(isset($_POST['booking_id'])){
        $bookingid = $_POST['booking_id'];
    }

    $db = new Database();
    $num_payment = $db-> table('payment')-> where('booking_id',$bookingid) -> numRows();

    if($num_payment  > 0){
        echo '<script>alert("You Already Paid!");
		window.history.back()</script>';
    }

    $bookingdetail = $db->table('booking')-> where('booking_id',$bookingid)-> row();
    $member = $db->table('member')-> where('member_id',getSession('member_id'))-> row();
    $service = $db-> table('service')-> where('service_id',$bookingdetail['service_id'])-> row();
    
    $startTime = new DateTime($bookingdetail['booking_arrive_datetime']);
    $endTime = new DateTime($bookingdetail['booking_leave_datetime']);
    $interval = $startTime->diff($endTime);
    $hours = $interval->h;

    $price = $service['service_price'];

    $finalprice = $hours * $price;
?>


<div class='page'>
	<div class="box pay">
		<h2 class='my-2'>Payment</h2>
		<form action="../utils/status_process.php" method="post">
			<div class="payform">
				<label for="username">Username:</label>
				<input type="text" value="<?php echo $member['member_name'];?>" disabled>
			</div>
			<div class="payform">
				<label for="service">Service:</label>
				<input type="text" value="<?php echo $service['service_title']; ?>" disabled>
			</div>
			<div class="payform">
				<label for="service">Service Price Per Hour:</label>
				<input type="text" value="RM <?php echo $service['service_price']; ?>" disabled>
			</div>
			<div class="payform">
				<label for="service">Selected Hours:</label>
				<input type="text" value="<?php echo $hours; ?>" disabled>
			</div>
			<div class="payform">
				<label for="price">Total Price: </label>
				<input type="text" value="RM <?php echo $finalprice; ?>" disabled>
			</div>
			<div class="payform">
				<label for="paytype">Payment Type:</label>
				<select name="type" id="type">
					<option value="cc">Credit Card</option>
					<option value="dc">Debit Card</option>
					<option value="ewallet">Ewallet</option>
				</select>
			</div>

			<div class="payform">
				<input type='hidden' name='func' value='payment'>
				<input type='hidden' name='booking_id' value=<?php echo $bookingid;?>>
				<input type='hidden' name='price' value=<?php echo $finalprice;?>>
				<input type='hidden' name='member_id' value=<?php echo getSession('member_id');?>>
				<button class='button action-button' type="submit" value="pay" name="pay">Pay</button>
			</div>
		</form>
	</div>
</div>
