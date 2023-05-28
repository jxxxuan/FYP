<?php
/*
	redirect('sfdv');
	if(true){
		echo 'ahahha';
		redirect('sfdv');
	}*/
	echo "<script src='" . route('utils/booking.js') . "'></script>";
	if (isset($_SESSION['maid_id'])){
		echo 'akck';
	}
	/*
	unset($_SESSION['maid_id']);
	unset($_SESSION['service_id']);
	*/
	function booking(){
		return 'adc';
	}
?>
