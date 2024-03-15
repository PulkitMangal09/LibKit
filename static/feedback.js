const stars = document.querySelectorAll('.star');
const ratingInput = document.getElementById('rating');

stars.forEach(star => {
  star.addEventListener('click', () => {
    const ratingValue = star.dataset.index;
    ratingInput.value = ratingValue;
    stars.forEach(star => star.classList.remove('active'));
    for (let i = 0; i < ratingValue; i++) {
      stars[i].classList.add('active');
    }
  });
});
