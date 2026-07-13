// Welcome Message
console.log("Smart Crop Recommendation System Loaded");

// Navbar Shadow Effect

window.addEventListener("scroll",function(){

const navbar=document.querySelector(".navbar");

if(window.scrollY>50){

navbar.classList.add("shadow-lg");

}
else{

navbar.classList.remove("shadow-lg");

}

});

// Button Animation

const buttons=document.querySelectorAll(".btn");

buttons.forEach(btn=>{

btn.addEventListener("mouseenter",()=>{

btn.style.transform="scale(1.05)";

});

btn.addEventListener("mouseleave",()=>{

btn.style.transform="scale(1)";

});

});

// Welcome Message
console.log("Smart Crop Recommendation System Loaded");

// Navbar Shadow on Scroll
window.addEventListener("scroll", function () {

    const navbar = document.querySelector(".navbar");

    if (window.scrollY > 50) {
        navbar.classList.add("shadow-lg");
    } else {
        navbar.classList.remove("shadow-lg");
    }

});

// Smooth Scroll Animation
const cards = document.querySelectorAll(".feature-card, .crop-card");

cards.forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-10px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0px)";

    });

});