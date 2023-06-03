function open_sidebar() {
	document.querySelector('.sidebar').classList.toggle('open');
	document.querySelector('.page').classList.toggle('close');
}
/*
const sb = document.querySelector('.sidebar');
const page = document.querySelector('.page');
console.log(page);
      toggle = sb.querySelector(".toggle-btn");

        // Check if the toggle state is stored in local storage
        const toggleState = localStorage.getItem('toggleState');
        if (toggleState === 'true') {
            sb.classList.add('open');
            page.classList.add('close');
        }

        // Toggle button state on click
        toggle.addEventListener('click', function() {
            sb.classList.toggle('open');
            page.classList.toggle('close');

            // Store the toggle state in local storage
            const currentState = sb.classList.contains('open');
            localStorage.setItem('toggleState', currentState.toString());
		});
*/