$('label.glyphicon-star').on('click', function() {
    if ($(this).hasClass('stared')) {
        $(this).removeClass('stared');
    } else {
        $(this).addClass('stared');

    }

    $.ajax({
        type: 'POST',
        url: '/post_star/',
        data: {
            'post': $(this).parents('div.post-data').attr('data-id')
        }
    });
});
