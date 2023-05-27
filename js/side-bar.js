// function open_sidebar() {
// 	document.querySelector('.sidebar').classList.toggle('open');
	
// }

const body = document.querySelector('.sidebar');
      toggle = body.querySelector(".toggle-btn");

        // Check if the toggle state is stored in local storage
        const toggleState = localStorage.getItem('toggleState');
        if (toggleState === 'true') {
            body.classList.add('open');
        }

        // Toggle button state on click
        toggle.addEventListener('click', function() {
            body.classList.toggle('open');

            // Store the toggle state in local storage
            const currentState = body.classList.contains('open');
            localStorage.setItem('toggleState', currentState.toString());
		});
