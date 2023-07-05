<?php
    require_once getView('layout.side-bar');
    if(isset($_POST['booking_id'])){
        $bookingid = $_POST['booking_id'];
    }

    $db = new Database();
    $memberid = getsession('id');
    $maid = $db-> table('booking')-> where('booking_id',$bookingid)-> row();
    $maidid = $maid['maid_id'];
    
?>

<section class="page">
    <h2>Rating and Comment</h2>
    <div class="box">
        <form action="../utils/status_process.php" method="POST">
            <div class="rating">
                <input type="radio" name="rating" value="5" id="5"><label for="5">☆</label>
				<input type="radio" name="rating" value="4" id="4"><label for="4">☆</label>
				<input type="radio" name="rating" value="3" id="3"><label for="3">☆</label>
				<input type="radio" name="rating" value="2" id="2"><label for="2">☆</label>
				<input type="radio" name="rating" value="1" id="1"><label for="1">☆</label>
            </div>

            <div class="comment">
                <label for="comment">Write Your Comment: </label>
                <br>
                <textarea name="comment" id="comment" cols="30" rows="10" placeholder="Write Somethings...."></textarea>
            </div>

            <div class="comment right-align">
                <input type='hidden' name='func' value='rating'>
                <input type='hidden' name='member_id' value=<?php echo $memberid;?>>
                <input type='hidden' name='booking_id' value=<?php echo $bookingid;?>>
                <input type='hidden' name='maid_id' value=<?php echo $maidid;?>>
                <button class='button action-button' type="submit" value="submit" name="submit">Submit</button>
            </div>
        </form>
    </div>
</section>

