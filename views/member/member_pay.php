<?php 
    require_once getView('layout.side-bar');
    if(isset($_GET['booking_id'])){
        $bookingid = $_GET['booking_id'];
    }

    $db = new Database();
    $payment = $db-> table('payment')-> where('booking_id',$bookingid)-> rows();
    $rowcount = count($payment);

    if($rowcount  > 0 ){
        echo '<script>alert("You Already Paid!")</script>';
        redirect('');
    }

    $bookingdetail = $db->table('booking')-> where('booking_id',$bookingid)-> row();
    $member = $db->table('member')-> where('member_id',$bookingdetail['member_id'])-> row();
    $service = $db-> table('service')-> where('service_id',$bookingdetail['service_id'])-> row();
    
    $startTime = new DateTime($bookingdetail['booking_arrive_datetime']);
    $endTime = new DateTime($bookingdetail['booking_leave_datetime']);
    $interval = $startTime->diff($endTime);
    $hours = $interval->h;

    $price = $service['service_price'];

    $finalprice = $hours * $price;
?>

<h2>Payment</h2>

<section class="c1">
    <div class="box pay" style="width:50%">
        <form action="" method="post">
            <div class="payform">
                <label for="username">Username:</label>
                <input type="text" value="<?php echo $member['member_name'];?>" disabled>
            </div>
            <div class="payform">
                <label for="service">Service:</label>
                <input type="text" value="<?php echo $service['service_title']; ?>" disabled>
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
                <button type="submit" value="pay" name="pay">Pay</button>
            </div>
        </form>
    </div>
</section>

<?php

    function update_status($bookingid,$status){
        $db -> table('booking') -> where('booking_id',$bookingid) -> update(['booking_status'=>$status]);
    }

    if(isPostMethod()){
        $result = $db-> table('payment')-> insert([
            'booking_id' => $bookingid,
            'member_id' => $member['member_id'],
            'payment_price' => $service['service_price'],
            'payment_type' => $_POST['type']
        ]);

        update_status($bookingid,'Completed');
       echo '<script>alert("Payment Successful!")</script>';
       redirect('member/member_booking_status?booking_id='.$bookingid);

    }

?>