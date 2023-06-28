<?php 
	$database = new Database();
	if(!isset($_GET['booking_id'])){
		redirect('');
	}else{
		$booking_id = $_GET['booking_id'];
        if(getsession('user_role') == 3)
		    $num_booking = $database -> table('booking') -> where('member_id',getSession('id')) -> where('booking_id',$booking_id) -> numRows();
        else
            $num_booking = $database -> table('booking') -> where('maid_id',getSession('id')) -> where('booking_id',$booking_id) -> numRows();
     
		if($num_booking > 0){
			$booking = $database -> table('booking') -> where('booking_id',$booking_id) -> row();
		}else{
			redirect('404');
		}
	}
	
    require_once getView('layout.side-bar');
    
    $circles = [
        ['circle' => 'circle1', 'name' => 'Pending', 'icon' => 'bx bx-check'],
        ['circle' => 'circle2', 'name' => 'Confirm', 'icon' => 'bx bx-receipt'],
        ['circle' => 'circle3', 'name' => 'Working', 'icon' => 'bx bx-home'],
        ['circle' => 'circle4', 'name' => 'Payment', 'icon' => 'bx bx-dollar'],
        ['circle' => 'circle5', 'name' => 'Rating', 'icon' => 'bx bx-star']
    ]; // Update with circle classes

	$currentStep = 0;
	for($i = 0;$i < count($circles);$i++){
		if($circles[$i]['name'] == $booking['booking_status']){
			$currentStep = $i;
		}
	}

    // Function to generate the progress bar HTML
    function generateProgressHTML($currentStep, $circles)
    {
        $progressHTML = '';

        foreach ($circles as $index => $circle) {
            $activeClass = ($index <= $currentStep) ? 'active' : '';
            $iconClass = ($index <= $currentStep) ? 'bx bx-check' : $circle['icon'];
            $progressHTML .= "<span class='circle $circle[circle] $activeClass'><i class='$iconClass'></i></span>";
        }

        return $progressHTML;
    }

    // === vertical bar === 

    $dots = [
        ['dot'=> 'dot1'],
        ['dot'=> 'dot2'],
        ['dot'=> 'dot3'],
        ['dot'=> 'dot4'],
        ['dot'=> 'dot5']
    ];

    function generateBody($currentStep, $dots)
    {
        $body = '';

        for ($i = 0; $i <= count($dots)-1; $i++) {
			
            $dot = $dots[$i];
            $activeClass = ($currentStep >= $i) ? 'active' : '';
            $body .= "<span class='dot $dot[dot] $activeClass'></span>";
        }

        return $body;
    }

    // === brief === 

    $texts = [
        ['text'=> 'text1', 'name' =>'Your booking is pending.'],
        ['text'=> 'text2', 'name' =>'Maid is comfirm your order.'],
        ['text'=> 'text3', 'name' =>'Maid is working'],
        ['text'=> 'text4', 'name' =>'Payment made.'],
        ['text'=> 'text5', 'name' =>'Rating made.']
    ];

    function generateBrief($currentStep, $texts)
    {
        $text = '';

        for ($i = 0; $i < $currentStep; $i++) {
            $textItem = $texts[$i];
            $openClass = ($i === 0) ? 'active' : '';
            $text .= "<span class='text $textItem[text] $openClass'></span>";
        }
        return $text;
    }
?>

<div class="page">
    <div class="title">
        <span class="text">Booking Status</span>
    </div>

    <div class="box">
    <div class="control-s-container">
        <div class="status_container">
            <div class="step">
                <?php echo generateProgressHTML($currentStep, $circles) ?>
                <div class="progress-bar">
                    <span class="indicator"></span>
                </div>
            </div>

            <div class="status_text">
                <?php foreach ($circles as $index => $circle) : ;?>
                    <span class="circle_name <?php if ($index === $currentStep - 1) echo 'active'; ?>"><?php echo $circle['name']; ?></span>
                <?php endforeach; ?>
            </div>
        </div>

        <div class="line"></div>

        <div class="second_container">
            <div class="left">
                <div class="step vertical-bar">
                    <div class="indicator"></div>

                    <?php echo generateBody($currentStep, $dots) ?>
                </div>
            </div>
            
            <div class="right">
                <?php for ($i = 0; $i <= 4 ;$i++){?>
					
                    <span class="row <?php if ($i <= $currentStep) echo 'active'; ?>"><?php echo $texts[$i]['name']; ?></span>
                <?php }?>
            </div>
			
			<div class="right">
				<?php for ($i = 0; $i <= 4 ;$i++){?>
					<span class='row'>
					<?php
						if (getSession('user_role') == MEMBER_ROLE && $currentStep == 1 && $i == 2) {
							echo "
								<form method='POST' action='../utils/status_process.php'>
									<input type='hidden' name='func' value='working'>
									<input type='hidden' name='booking_id' value=".$booking_id.">
									<button class='button action-button' type='submit'>Start working</button>
								</form>
							";
						} else if (getSession('user_role') == MEMBER_ROLE && $currentStep == 2 && $i == 3) {
							echo "
								<form method='POST' action='../utils/status_process.php'>
									<input type='hidden' name='func' value='payment'>
									<input type='hidden' name='booking_id' value=".$booking_id.">
									<button class='button action-button' type='submit'>Pay</button>
								</form>
							";
						} else if (getSession('user_role') == MEMBER_ROLE && $currentStep == 3 && $i == 4) {
							echo "
								<form method='POST' action='../utils/status_process.php'>
									<input type='hidden' name='func' value='rate'>
									<input type='hidden' name='booking_id' value=".$booking_id.">
									<button class='button action-button' type='submit'>Rating</button>
								</form>
							";
						}
					?>

					</span>
					<?php
					}
				?>
            </div>
        </div>
    </div>
    </div>
</div>

<?php
    // Update the progress bar width based on current step
    $progressWidth = (($currentStep ) / (count($circles) - 1)) * 100;
    echo "<style>.step .progress-bar .indicator { width: $progressWidth%; }</style>";
    ?>

    <?php
    // Update the vertical-bar .indicator height based on current step
    $progressheight = (($currentStep ) / (count($dots) )) * 110;
    $progressheight = min($progressheight, 80); // Set the maximum height to 80%
    echo "<style>.vertical-bar .indicator { height: $progressheight%; }</style>";
?>

