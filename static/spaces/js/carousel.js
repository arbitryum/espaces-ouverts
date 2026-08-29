// Carousel navigation functionality
(function() {
  // Update carousel dot indicators
  function updateCarouselButtons(carouselId, currentSlideIndex) {
    const allButtons = document.querySelectorAll(`.carousel-nav-btn[data-carousel-id="${carouselId}"]`);
    allButtons.forEach((btn, index) => {
      if (index === currentSlideIndex) {
        btn.classList.remove('bg-base-100/60', 'hover:bg-base-100/80', 'w-2');
        btn.classList.add('bg-primary', 'w-6');
      } else {
        btn.classList.remove('bg-primary', 'w-6');
        btn.classList.add('bg-base-100/60', 'hover:bg-base-100/80', 'w-2');
      }
    });
  }

  // Navigate carousel by direction (next/prev) with looping
  function navigateCarousel(carouselId, direction) {
    const carousel = document.querySelector(`.space-carousel[data-space-id="${carouselId}"]`);
    if (!carousel) return;

    const items = carousel.querySelectorAll('.carousel-item');
    const itemWidth = carousel.offsetWidth;
    const currentScroll = carousel.scrollLeft;
    let nextIndex = Math.round(currentScroll / itemWidth);

    if (direction === 'next') {
      nextIndex = (nextIndex + 1) % items.length;
    } else if (direction === 'prev') {
      nextIndex = (nextIndex - 1 + items.length) % items.length;
    }

    const scrollPosition = nextIndex * itemWidth;
    carousel.scroll({
      left: scrollPosition,
      behavior: 'smooth'
    });

    updateCarouselButtons(carouselId, nextIndex);
  }

  // Initialize carousel navigation
  function initCarouselNavigation() {
    // Dot navigation
    document.querySelectorAll('.carousel-nav-btn').forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        const carouselId = this.dataset.carouselId;
        const slideIndex = parseInt(this.dataset.slideIndex);
        const carousel = document.querySelector(`.space-carousel[data-space-id="${carouselId}"]`);

        if (!carousel) return;

        const itemWidth = carousel.offsetWidth;
        const scrollPosition = slideIndex * itemWidth;

        carousel.scroll({
          left: scrollPosition,
          behavior: 'smooth'
        });

        updateCarouselButtons(carouselId, slideIndex);
      });
    });

    // Arrow navigation
    document.querySelectorAll('.carousel-prev').forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        navigateCarousel(this.dataset.carouselId, 'prev');
      });
    });

    document.querySelectorAll('.carousel-next').forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        navigateCarousel(this.dataset.carouselId, 'next');
      });
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCarouselNavigation);
  } else {
    initCarouselNavigation();
  }
})();
