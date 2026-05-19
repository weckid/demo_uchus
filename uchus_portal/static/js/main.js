// слайдер на главной (кабинет), переключение раз в 3 сек
document.addEventListener('DOMContentLoaded', function () {
    var carouselEl = document.getElementById('courseCarousel');
    if (!carouselEl) {
        return;
    }

    var carousel = new bootstrap.Carousel(carouselEl, {
        interval: 3000,
        ride: 'carousel',
        pause: false
    });

    // плавное появление карточек заявок по очереди
    var cards = document.querySelectorAll('.app-card');
    cards.forEach(function (card, i) {
        card.style.animationDelay = (i * 0.08) + 's';
        card.classList.add('card-show');
    });
});
