const circle = document.querySelectorAll('.circle'),
progressbar = document.querySelector('.indicator'),
button = document.querySelectorAll('button');

let currentStep = 1;

	const updateProgress = () => {
		circle.forEach((circle, index) => {
			circle.classList[`${index < currentStep ? 'add' : 'remove'}`]('active');
		});
		
		progressbar.style.width = `${((currentStep - 1) / (circle.length - 1)) * 100}%`;
	};

	if (localStorage.getItem('progress')) {
		currentStep = parseInt(localStorage.getItem('progress'));
		updateProgress();
	}
	
const updateSteps = (e) => {

	currentStep = e.target.id === "next" ? ++currentStep : --currentStep;
	updateProgress();

	localStorage.setItem('progress', currentStep);
};

button.forEach((button) => {
	button.addEventListener("click",updateSteps);
});