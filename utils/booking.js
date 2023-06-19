const scriptUrl = document.currentScript.src;
const path = new URL(scriptUrl).pathname;
const BASEPATH = '/' + path.split('/').slice(1, -1).join('/');

function select(button) {
	if (check_valid(button)) {
		button.classList.toggle('selected');
		button.classList.toggle('available');
	}
}

function check_valid(button) {
	return (button.classList.contains('available') || button.classList.contains('selected'));
}

function get_all_selected_datetime() {
	var selectedButtons = document.querySelectorAll('.button.selected');
	var selectedDates = [];

	// Selects the first table element in the document
	var table = document.querySelector('.time-slot-table'); 
	// Get the date text from the <th> elements
	var dates = [];
	table.querySelectorAll('th:not(:first-child)').forEach(function(thElement, index) {
		dates.push(thElement.innerText.split('\n')[1]);
	});;
	
	selectedButtons.forEach(function(button, index) {
		var column = button.closest('td'); // Find the closest parent <td> element

		// Access the column index using the cellIndex property
		var columnIndex = column.cellIndex;
		selectedDates.push(dates[columnIndex]);
	});
	
	// Get the date text from the first row
	var times = [];
	table.querySelectorAll("tr td:first-child").forEach(function(trElement, index) {
		times.push(trElement.innerText);
	});
	
	selectedButtons.forEach(function(button, index) {
		var row = button.closest('tr'); // Find the closest parent <tr> element
		
		selectedDates[index] = selectedDates[index]+' '+times[row.rowIndex-1];
	});
	return selectedDates;
}


function splitDateTimeList(datetimeList) {
	datetimeList.sort();

	let result = [];
	let temp = [];

	for (let i = 0; i < datetimeList.length; i++) {
		const [date, time] = datetimeList[i].split(' ');

		if (i === 0 || isConsecutive(datetimeList[i - 1], datetimeList[i])) {
			temp.push(datetimeList[i]);
		} else {
			result.push(temp);
			temp = [datetimeList[i]];
		}

		if (i === datetimeList.length - 1) {
			result.push(temp);
		}
	}
	return result;
}

function isConsecutive(datetime1, datetime2) {
	const time1 = getTime(datetime1);
	const time2 = getTime(datetime2);

	return time2.getHours() - time1.getHours() === 1;
}

function getTime(datetime) {
	const [, time] = datetime.split(' ');
	const [hour, minute] = time.split(':');

	const date = new Date();
	date.setHours(hour);
	date.setMinutes(minute);

	return date;
}

function get_begin_end(datetimelist) {
	var begin = new Date(datetimelist[0]);
	if (datetimelist.length === 1) { 
		var end = new Date(datetimelist[0]);
		
	} else {
		var end = new Date(datetimelist[datetimelist.length - 1]);
	}
	end.setHours(end.getHours() + 1);
	end = formatDateTime(end);
	begin = formatDateTime(begin);
	return [begin, end];
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

function cancel_booking(){
	console.log('xas');
}

function confirm_booking() {
	
	var selectedDates = get_all_selected_datetime();
	var addressValue = get_address();
	if (selectedDates.length > 0) {
		selectedDates = splitDateTimeList(selectedDates);
		var booking_time = [];
		selectedDates.forEach(function (datetime) {
			booking_time.push(get_begin_end(datetime));
		});
	} else {
		console.log('unvalid booking');
	}
	console.log(booking_time);
	sendDataToPhp({'booking_datetime':booking_time,'address':addressValue}, 'fyp/utils/booking_process.php');
}

function get_address(){
	var addressTextarea = document.querySelector('textarea[name="address"]');
	var addressValue = addressTextarea.value;
	return addressValue;
}

function valid_booking(){
	return true;
}

function sendDataToPhp(data, url) {
    var xhr = new XMLHttpRequest();
    var url = window.location.origin + '/' + url; // Construct the complete URL
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Response from PHP
            var response = xhr.responseText;
            console.log(response);
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

function previous_week(currentDate) {
    var previousWeekStartDate = new Date(currentDate);
    previousWeekStartDate.setDate(previousWeekStartDate.getDate() - 7);
    var date = formatDate(previousWeekStartDate);
    window.location.replace('time_slot.php?current_date=' + date);
}

function next_week(currentDate) {
    var nextWeekStartDate = new Date(currentDate);
    nextWeekStartDate.setDate(nextWeekStartDate.getDate() + 7);
    var date = formatDate(nextWeekStartDate);
    window.location.replace('time_slot.php?current_date=' + date);
	console.log('hahaha');
}


/*
function previous_week(currentDate) {
	// Calculate the previous week's start and end date
	var previousWeekStartDate = new Date(currentDate);
	previousWeekStartDate.setDate(previousWeekStartDate.getDate() - 7);
	var previousWeekEndDate = new Date(previousWeekStartDate);
	previousWeekEndDate.setDate(previousWeekEndDate.getDate() + 6);

	// Update the table content with the new week's data
	updateTableContent(previousWeekStartDate, previousWeekEndDate);
}

function next_week(currentDate) {
	// Calculate the next week's start and end date
	var nextWeekStartDate = new Date(currentDate);
	nextWeekStartDate.setDate(nextWeekStartDate.getDate() + 7);
	var nextWeekEndDate = new Date(nextWeekStartDate);
	nextWeekEndDate.setDate(nextWeekEndDate.getDate() + 6);

	// Update the table content with the new week's data
	updateTableContent(nextWeekStartDate, nextWeekEndDate);
}

function updateTableContent(startDate, endDate) {
	// Construct the new table content for the given week
	var tableContent = '';

	// Generate the table rows and cells for each day in the week
	for (var i = 0; i < 7; i++) {
		var currentDate = new Date(startDate);
		currentDate.setDate(currentDate.getDate() + i);

		var currentDay = currentDate.getDate();
		var currentFormattedDate = currentDate.toISOString().split('T')[0];

		// Append the table cell for the current day
		tableContent += '<th>' + currentDay + ' ' + currentFormattedDate + '</th>';
	}

	// Update the table's tbody with the new content
	$('.time-slot-table tbody').html(tableContent);
}
*/