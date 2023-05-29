<?php 
    require_once getView('layout.side-bar');
    $database = new database();
    
    $circles = [
        ['circle' => 'circle1', 'name' => 'Pending', 'icon' => 'bx bx-check'],
        ['circle' => 'circle2', 'name' => 'Confirm', 'icon' => 'bx bx-receipt'],
        ['circle' => 'circle3', 'name' => 'On the Way', 'icon' => 'bx bx-car'],
        ['circle' => 'circle4', 'name' => 'Arrived', 'icon' => 'bx bx-home'],
        ['circle' => 'circle5', 'name' => 'In Progress', 'icon' => 'bx bxs-hand'],
        ['circle' => 'circle6', 'name' => 'Payment', 'icon' => 'bx bx-dollar'],
        ['circle' => 'circle7', 'name' => 'Rating', 'icon' => 'bx bx-star']
    ]; // Update with your circle classes

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
            $progressHTML .= "<span class='circle $circle[circle] $activeClass'><i class='$iconClass'></i></span>";
        }

        return $progressHTML;
    }
?>

<div class="base">
    <div class="title">
        <span class="text">Booking Status</span>
    </div>

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
        <form method="post">
        
            <div class="buttons">
                <button type="submit" name="prev" <?php if ($currentStep === 1) echo 'disabled'; ?>>Previous</button>
                <button type="submit" name="next" <?php if ($currentStep === count($circles)) echo 'disabled'; ?>>Next</button>
            </div>
        </form>
    </div>
</div>


    <?php
    // Update the progress bar width based on current step
    $progressWidth = (($currentStep - 1) / (count($circles) - 1)) * 100;
    echo "<style>.step .progress-bar .indicator { width: $progressWidth%; }</style>";
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