// const container = document.querySelector('.container3');
// const p1Link = document.querySelector('.p1-link');
// const p2Link = document.querySelector('.p2-link');


// p2Link.addEventListener('click', ()=> {
//     container.classList.add('active');
// });

// p1Link.addEventListener('click', ()=> {
//     container.classList.remove('active');
// });

const body = document.querySelector(".all"),
      sidebar = body.querySelector(".sidebar"),
      toggle = body.querySelector(".toggle"),
      searchBtn = body.querySelector(".search-box");

      toggle.addEventListener("click", () =>{
        sidebar.classList.toggle("close");
      });
