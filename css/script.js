const container = document.querySelector('.container3');
const p1Link = document.querySelector('.p1-link');
const p2Link = document.querySelector('.p2-link');


p2Link.addEventListener('click', ()=> {
    container.classList.add('active');
});

p1Link.addEventListener('click', ()=> {
    container.classList.remove('active');
});