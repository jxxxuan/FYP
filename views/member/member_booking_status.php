<?php 
    require_once getView('layout.side-bar');
    $database = new database();
    
    $circles = [
        ['circle' => 'circle1', 'name' => 'Pending', 'icon' => 'bx bx-check'],
        ['circle' => 'circle2', 'name' => 'Confirm', 'icon' => 'bx bx-receipt'],
        ['circle' => 'circle3', 'name' => 'On the Way', 'icon' => 'bx bx-car'],
        ['circle' => 'circle4', 'name' => 'Arrived', 'icon' => 'bx bx-home'],
        ['circle' => 'circle5', 'name' => 'Payment', 'icon' => 'bx bx-dollar'],
        ['circle' => 'circle6', 'name' => 'Rating', 'icon' => 'bx bx-star']
    ]; // Update with circle classes

    // Initialize current step
    $currentStep = 1;

    // Update current step based on session data
    if (isset($_SESSION['progress'])) {
        $currentStep = (int)$_SESSION['progress'];
    }

    // Handle form submission
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        if (isset($_POST['next'])) {
            $currentStep++;
        } elseif (isset($_POST['prev'])) {
            $currentStep--;
        }

        // Update session data
        $_SESSION['progress'] = $currentStep;
    }

    // Function to generate the progress bar HTML
    function generateProgressHTML($currentStep, $circles)
    {
        $progressHTML = '';

        foreach ($circles as $index => $circle) {
            $activeClass = ($index < $currentStep) ? 'active' : '';
            $iconClass = ($index < $currentStep) ? 'bx bx-check' : $circle['icon'];
            $progressHTML .= "<span class='circle $circle[circle] $activeClass'><i class='$iconClass'></i>$index</span>";
        }

        return $progressHTML;
    }

    // === vertical bar === 

    $dots = [
        ['dot'=> 'dot1', 'date' =>'2023-05-28 11:00:00', 'status' => 'no'],
        ['dot'=> 'dot2', 'date' =>'2023-05-28 12:00:00', 'status' => 'no'],
        ['dot'=> 'dot3', 'date' =>'2023-05-28 13:00:00', 'status' => 'no'],
        ['dot'=> 'dot4', 'date' =>'2023-05-28 14:00:00', 'status' => 'no'],
        ['dot'=> 'dot5', 'date' =>'2023-05-28 15:00:00', 'status' => 'no'],
        ['dot'=> 'dot6', 'date' =>'2023-05-28 16:00:00', 'status' => 'no']
        
    ];

    function generateBody($currentStep, $dots)
    {
        $body = '';

        // foreach ($dots as $index =>$dot){
        //     $activeClass = ($index < $currentStep) ? 'active' : '';
        //     $body .="<span class='dot $dot[dot] $activeClass'></span>";
        // }

        for ($i = 0; $i < $currentStep - 1; $i++) {
            $dot = $dots[$i];
            $activeClass = ($i < $currentStep) ? 'active' : '';
            $body .= "<span class='dot $dot[dot] $activeClass'></span>";
        }

        return $body;
    }

    // === brief === 

    $texts = [
        ['text'=> 'text1', 'name' =>'Maid is comfirm your order.'],
        ['text'=> 'text2', 'name' =>'Maid is on the way to your desire location.'],
        ['text'=> 'text3', 'name' =>'Maid is arrive at your desire location.'],
        ['text'=> 'text4', 'name' =>'Maid service is completed.'],
        ['text'=> 'text5', 'name' =>'Payment made.'],
        ['text'=> 'text6', 'name' =>'Rating made.']
    ];

    function generateBrief($currentStep, $texts)
    {
        $text = '';

        // foreach ($texts as $index =>$dot){
        //     $openClass = ($index < $currentStep) ? 'active' : '';
        //     $body .="<span class='text $dot[text] $openClass'></span>";
        // }

        for ($i = 0; $i < $currentStep - 1; $i++) {
            $textItem = $texts[$i];
            $openClass = ($i === 0) ? 'active' : '';
            $text .= "<span class='text $textItem[text] $openClass'></span>";
        }

        return $text;
    }
?>

<div class="base">
    <div class="title">
        <span class="text">Booking Status</span>
    </div>

    <div class="box" style='max-width:75%; margin-left:10%;'>
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
                    <class class="indicator"></class>

                    <?php echo generateBody($currentStep, $dots) ?>
                </div>

                <div class="vertical-text">
                    <?php for ($i = $currentStep - 1; $i > 0 ;$i--) : ;?>
                        <span class="dot_name <?php if ($i === $currentStep - 1) echo 'active'; ?>"><?php echo $dots[$i]['date']; ?></span>
                    <?php endfor; ?>

                </div>
            </div>
            
            <div class="right">
                <?php for ($i = $currentStep - 1; $i > 0 ;$i--) : ;?>
                    <span class="text_name <?php if ($i === $currentStep - 1) echo 'active'; ?>"><?php echo $texts[$i]['name']; ?></span>
                <?php endfor; ?>
            </div>
        </div>
    </div>
    </div>
            
    <form method="post">        
        <div class="buttons">
            <button type="submit" name="prev" <?php if ($currentStep === 1) echo 'disabled'; ?>>Previous</button>
            <button type="submit" name="next" <?php if ($currentStep === count($circles)) echo 'disabled'; ?>>Next</button>
        </div>
    </form>
</div>



    <?php
    // Update the progress bar width based on current step
    $progressWidth = (($currentStep - 1) / (count($circles) - 1)) * 100;
    echo "<style>.step .progress-bar .indicator { width: $progressWidth%; }</style>";
    echo $index;
    echo $currentStep;
    ?>

    <?php
    // Update the vertical-bar .indicator height based on current step
    $progressheight = (($currentStep - 2) / (count($dots) - 1)) * 100;
    $progressheight = min($progressheight, 100); // Set the maximum height to 80%
    echo "<style>.vertical-bar .indicator { height: $progressheight%; }</style>";
    ?>

<!-- <div class="base">
    <div class="title">
        <span class="text">Booking Status</span>
    </div>

    <div class="control-s-container">
        <div class="status_container">
            <div class="step">
                <span class="circle">1</span>
                <span class="circle">2</span>
                <span class="circle">3</span>
                <span class="circle">4</span>
                <span class="circle">5</span>
                <span class="circle">6</span>
                <span class="circle">7</span>

                <div class="progress-bar">
                    <span class="indicator"></span>
                </div>
            </div>

            <div class="status_text">
                <span class="circle_name">Pending</span>
                <span class="circle_name">Confirm</span>
                <span class="circle_name">On the Way</span>
                <span class="circle_name">Arrvied</span>
                <span class="circle_name">In Progess</span>
                <span class="circle_name">Payment</span>
                <span class="circle_name">Rating</span>
            </div>

            <div class="press">
                <button id="prev">prev</button>
                <button id="next">next</button>
            </div>
        </div>
        

        <div class="line"></div>

        <div class="bar">

        </div>

        <div class="brief">
            
        </div>
    </div>
</div>

<script src="<?php echo route('js/status.js')?>"></script> -->

