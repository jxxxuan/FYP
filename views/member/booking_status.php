<?php 
	$database = new Database();
	if(!isset($_GET['booking_id'])){
		redirect('');
	}else{
		$booking_id = $_GET['booking_id'];
		
		$num_booking = $database -> table('booking') -> where('booking_id',$booking_id) -> where('member_id',getSession('member_id')) -> numRows();
		
		if($num_booking > 0){
			$booking = $database -> table('booking') -> where('booking_id',$booking_id) -> row();
			$service = $database -> table('service') -> where('service_id',$booking['service_id']) -> row();
			$maid = $database -> table('maid') -> where('maid_id',$booking['maid_id']) -> row();
			$maidinfo = $database->table('member')->where('member_id', $maid['member_id'])->row();
		}else{
			redirect('404');
		}
	}
	
    require_once getView('layout.side-bar');
    
    $circles = [
        ['circle' => 'circle1', 'name' => 'Pending', 'icon' => 'bx bx-check', 'status' => 'Pending'],
        ['circle' => 'circle2', 'name' => 'Confirm', 'icon' => 'bx bx-receipt', 'status' => 'Confirm'],
        ['circle' => 'circle3', 'name' => 'Working', 'icon' => 'bx bx-home', 'status' => 'Working'],
        ['circle' => 'circle4', 'name' => 'Payment', 'icon' => 'bx bx-dollar', 'status' => 'Complete'],
        ['circle' => 'circle5', 'name' => 'Rating', 'icon' => 'bx bx-star', 'status' => 'Rating']
    ]; // Update with circle classes

	$currentStep = null;
	for($i = 0;$i < count($circles);$i++){
		if($circles[$i]['status'] == $booking['booking_status']){
			$currentStep = $i;
		}
	}
	
	$currentStep = $currentStep === null ? 4 :$currentStep;

    // Function to generate the progress bar HTML
    function generateProgressHTML($currentStep, $circles)
    {
        $progressHTML = '';

        foreach ($circles as $index => $circle) {
			if($index <= $currentStep){
				$activeClass = 'success';
				$iconClass = 'bx bx-check';
			}else{
				$activeClass = '';
				$iconClass = $circle['icon'];
			}
			
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
							if ($currentStep == 2 && $i == 3) {
						?>
								<form method='POST' action=<?php echo route('member/member_pay')?>>
									<input type='hidden' name='booking_id' value=<?php echo $booking_id;?>>
									<button class='button action-button' type='submit'>Pay</button>
								</form>
						<?php
							} else if ($currentStep == 4 && $i == 4) {
								$num_rating = $database -> table('rating') -> where('booking_id',$booking_id) -> numRows();
								if($num_rating == 0){
						?>
									<form method='POST' action=<?php echo route('member/member_rating')?>>
										<input type='hidden' name='booking_id' value=<?php echo $booking_id;?>>
										<button class='button action-button' type='submit'>Rating</button>
									</form>
						<?php
								}
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
	<div class="box">
		<h2>Service</h2>
		<table>
			<tbody>
				<tr>
					<td>Service Title:</td>
					<td><?php echo $service['service_title']; ?></td>
				</tr>
				<tr>
					<td>Type:</td>
					<td><?php echo $service['service_type']; ?></td>
				</tr>
				<tr>
					<td>Description:</td>
					<td><?php echo $service['service_description']; ?></td>
				</tr>
				<tr>
					<td>Price per hour:</td>
					<td><?php echo $service['service_price']; ?></td>
				</tr>
			</tbody>
		</table>
	</div>
	
	<div class="box">
		<h2>Maid</h2>
		<table>
			<tbody>
				<tr>
					<td>Member Name:</td>
					<td><?php echo $maidinfo['member_name']; ?></td>
				</tr>
				<tr>
					<td>Maid Age:</td>
					<td><?php echo $maid['maid_age']; ?></td>
				</tr>
				<tr>
					<td>Maid Gender:</td>
					<td><?php echo $maid['maid_gender']; ?></td>
				</tr>
				<tr>
					<td>Member Contact:</td>
					<td><?php echo $maidinfo['member_contact']; ?></td>
				</tr>
				<tr>
					<td>Maid Skill:</td>
					<td><?php echo $maid['maid_skill']; ?></td>
				</tr>
			</tbody>
		</table>
	</div>
	
	<div class="box">
		<h2>Time</h2>
		<table>
			<tbody>
				<tr>
					<td>Booking Time:</td>
					<td><?php echo $booking['booking_datetime']; ?></td>
				</tr>
				<tr>
					<td>Arrive Time:</td>
					<td><?php echo $booking['booking_arrive_datetime']; ?></td>
				</tr>
				<tr>
					<td>Leave Time:</td>
					<td><?php echo $booking['booking_leave_datetime']; ?></td>
				</tr>
			</tbody>
		</table>
	</div>
	
</div>

<?php 
    // Update the progress bar width based on current step
    $progressWidth = (($currentStep ) / (count($circles) - 1)) * 100;
    echo "<style>.step .progress-bar .indicator { width: $progressWidth%; }</style>";
	
    // Update the vertical-bar .indicator height based on current step
    $progressheight = (($currentStep  ) / (count($dots) )) * 95;
    $progressheight = min($progressheight, 75); // Set the maximum height to 80%
    echo "<style>.vertical-bar .indicator { height: $progressheight%; }</style>";
?>
