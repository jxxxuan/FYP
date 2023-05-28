<?php 
    require_once getView('layout.side-bar');
?>

<div class="base">
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

                <div class="progress-bar">
                    <span class="indicator"></span>
                </div>
            </div>

            <div class="status_text">
                <span class="circle_name">Pending</span>
                <span class="circle_name">Confirm</span>
                <span class="circle_name">On the Way</span>
                <span class="circle_name">Arrvied</span>
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

<script src="<?php echo route('js/status.js')?>"></script>