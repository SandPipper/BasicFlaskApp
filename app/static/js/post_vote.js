$('label.post-vote-up').on('click', function() {
    if ($(this).hasClass('voted-up')) {
        $(this).text("  " + (parseInt($(this).text(), 10) - 1).toString(10));
        $(this).removeClass('voted-up')
        var vote = 0;

    } else {

        $(this).text("  " + (parseInt($(this).text(), 10) + 1).toString(10));
        var vote = 1;
        $(this).addClass('voted-up');
        if ($(this).next('label.post-vote-down')
                   .hasClass('voted-down')){
            $(this).next('label.post-vote-down').text("  " +
                (parseInt($(this).next('label.post-vote-down')
                    .text(), 10) + 1).toString(10));
            $(this).next('label.post-vote-down')
                   .removeClass('voted-down');
        }
    }

    $.ajax({
        type: 'POST',
        url: '/post_vote/',
        data:  {
            'post': $(this).parents('div.for-post-del').attr('data-id'),
            'vote': vote
        },
        success: function(data) {
            console.log(data);
        }
    });

});

$('label.post-vote-down').on('click', function() {
    if ($(this).hasClass('voted-down')) {
        $(this).text("  " + (parseInt($(this).text(), 10) + 1).toString(10));
        $(this).removeClass('voted-down');
        var vote = 0;

    } else {
        var vote = -1;
        $(this).text("  " + (parseInt($(this).text(), 10) - 1).toString(10));
        $(this).addClass('voted-down');
        if ($(this).prev('label.post-vote-up')
                   .hasClass('voted-up')) {
            $(this).prev('label.post-vote-up')
                   .removeClass('voted-up');
            $(this).prev('label.post-vote-up').text("  " +
                (parseInt($(this).prev('label.post-vote-up')
                .text(), 10) - 1).toString(10));
        }
    }

    $.ajax({
        type: 'POST',
        url: '/post_vote/',
        data:  {
            'post': $(this).parents('div.for-post-del').attr('data-id'),
            'vote': vote
        },
        success: function(data) {
            console.log(data);
        }
    });
});
