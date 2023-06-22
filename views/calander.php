<!DOCTYPE html>
<html>
<head>
  <title>Weekly Calendar Example</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/fullcalendar/3.10.2/fullcalendar.min.css" />
  <style>
    .calendar {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
    }
    .calendar .day {
      background-color: #fff;
      border: 1px solid #ccc;
      padding: 5px;
      text-align: center;
    }
    .calendar .day.booked {
      background-color: red;
      color: #fff;
    }
  </style>
  
</head>
<body>
  <div id="calendar"></div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/fullcalendar/3.10.2/fullcalendar.min.js"></script>
  <script>
	$(document).ready(function() {
	  var selectedRanges = []; // Array to store selected ranges

	  $('#calendar').fullCalendar({
		header: {
		  left: 'prev,next today',
		  center: 'title',
		  right: ''
		},
		defaultView: 'agendaWeek',
		minTime: '06:00:00',
		maxTime: '20:00:00',
		slotDuration: '01:00:00',
		allDaySlot: false,
		weekends: true,
		contentHeight: 'auto',
		selectable: true,
		
		select: function(start, end) {
		  var startTime = start.format('HH:mm');
		  var endTime = end.format('HH:mm');
		  var selectedRange = {
			start: startTime,
			end: endTime
		  };
		  selectedRanges.push(selectedRange); // Store the selected range in the array
		  console.log('Selected time:', startTime, 'to', endTime);

		  // Highlight the selected range by rendering a new event with a green background color
		  $('#calendar').fullCalendar('renderEvent', {
			start: start,
			end: end,
			backgroundColor: 'green',
			rendering: 'background',
			selectable: false // Disable selection for the rendered event
		  }, true);

		  // Clear the current selection
		  $('#calendar').fullCalendar('unselect');
		},
		
		events: [
		  // Define your events here
		  // Example:
		  // {
		  //   title: 'Event 1',
		  //   start: '2023-05-25T10:00:00',
		  //   end: '2023-05-25T12:00:00'
		  // }
		]
	  });

	  // Example: Logging all selected ranges
	  $('#showSelected').click(function() {
		console.log('Selected Ranges:', selectedRanges);
	  });
	});

  </script>
</body>
</html>
