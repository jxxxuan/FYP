const scriptUrl = document.currentScript.src;
const path = new URL(scriptUrl).pathname;
const BASEPATH = '/' + path.split('/').slice(1, -1).join('/');

var total_selected_hour = 0;
var selectedDates = [];

function select(button) {
	if(check_valid(button)){
		if (button.classList.contains('selected')){
			button.classList.toggle('selected');
			button.classList.toggle('available');
			button.classList.toggle('cancel');
			total_selected_hour -= 1;
			
		}else if(button.classList.contains('cancel')){
			button.classList.toggle('selected');
			button.classList.toggle('available');
			button.classList.toggle('cancel');
			total_selected_hour -= 1;
		}else{
			button.classList.toggle('selected');
			button.classList.toggle('available');
		}
	}
	
}

function showAlert() {
  var message = 'This is an alert message.';
  alert(message);
}

function check_valid(button) {
	return (button.classList.contains('available') || button.classList.contains('selected'));
}

function getAllDatetimebyClass(class_) {
	var Buttons = document.querySelectorAll('.button.'+class_);
	var Dates = [];
	// Selects the first table element in the document
	var table = document.querySelector('.time-slot-table'); 
	// Get the date text from the <th> elements
	var dates = [];
	table.querySelectorAll('th:not(:first-child)').forEach(function(thElement, index) {
		dates.push(thElement.innerText.split('\n')[1]);
	});;
	
	Buttons.forEach(function(button, index) {
		var column = button.closest('td'); // Find the closest parent <td> element

		// Access the column index using the cellIndex property
		var columnIndex = column.cellIndex-1;
		Dates.push(dates[columnIndex]);
	});
	
	// Get the date text from the first row
	var times = [];
	table.querySelectorAll("tr td:first-child").forEach(function(trElement, index) {
		times.push(trElement.innerText);
	});
	
	Buttons.forEach(function(button, index) {
		var row = button.closest('tr'); // Find the closest parent <tr> element
		
		Dates[index] = Dates[index]+' '+times[row.rowIndex-1];
	})
	
	return Dates;
}


function formatDateTime(date) {
	var year = date.getFullYear();
	var month = String(date.getMonth() + 1).padStart(2, '0'); // Month is zero-based, so we add 1
	var day = String(date.getDate()).padStart(2, '0');
	var hours = String(date.getHours()).padStart(2, '0');
	var minutes = String(date.getMinutes()).padStart(2, '0');
	var seconds = String(date.getSeconds()).padStart(2, '0');

	return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

function confirm_booking() {
	storeOperatedDt();
	var addressValue = get_address();
	sendDataToPhp({'func':'book','address':addressValue}, 'fyp/utils/booking_process.php', function(response) {
		console.log(response);
		if (response.hasOwnProperty('func') && response.func == 'alert'){
			confirm(response.content);
		}
	});
	
	//window.location.href = 'view_bookings';
}

function get_address(){
	var addressInput = document.querySelector('input[name="address"]');
	return addressInput.value;
}

function valid_booking(){
	return true;
}

function sendDataToPhp(data, url, callback) {
	
    var xhr = new XMLHttpRequest();
    var url = window.location.origin + '/' + url; // Construct the complete URL
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Response from PHP
			var response = {};
			if(xhr.responseText.length > 0){
				response = JSON.parse(xhr.responseText);
				//console.log(response);
				
				/*
				if (response.hasOwnProperty('func') && response.func == 'alert'){
					confirm(response.content);
				}
				*/
			}
			callback(response);
        }
    };
    xhr.send(JSON.stringify(data));
}

function formatDate(date) {
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    return year + '-' + month + '-' + day;
}

function storeOperatedDt(){
	var selected = getAllDatetimebyClass('selected');
	var canceled = getAllDatetimebyClass('cancel');
	console.log(selected);
	sendDataToPhp({'func':'select','selected_dt':selected}, 'fyp/utils/booking_process.php', function(response) {
		console.log(response);
	});
	sendDataToPhp({'func':'cancel','cancel_dt':canceled}, 'fyp/utils/booking_process.php', function(response) {
		console.log(response);
	});
}

function previous_week(viewDate) {
	event.preventDefault();
	storeOperatedDt();
	var previousWeekStartDate = new Date(viewDate);
	previousWeekStartDate.setDate(previousWeekStartDate.getDate() - 7);
	var date = formatDate(previousWeekStartDate);
	var url = window.location.href;
	var updatedUrl;

	if (url.includes('view_date=')) {
	  updatedUrl = url.replace(/(view_date=)[^&]+/, '$1' + date);
	} else {
	  updatedUrl = url + (url.includes('?') ? '&' : '?') + 'view_date=' + date;
	}

	window.location.href = updatedUrl;
}

function next_week(viewDate) {
	event.preventDefault();
	storeOperatedDt();
	var nextWeekStartDate = new Date(viewDate);
	nextWeekStartDate.setDate(nextWeekStartDate.getDate() + 7);
	var date = formatDate(nextWeekStartDate);
	var url = window.location.href;
	var updatedUrl;

	if (url.includes('view_date=')) {
	  updatedUrl = url.replace(/(view_date=)[^&]+/, '$1' + date);
	} else {
	  updatedUrl = url + (url.includes('?') ? '&' : '?') + 'view_date=' + date;
	}

	window.location.href = updatedUrl;
}

