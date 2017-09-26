
$('label.comment-vote-up').on('click', function() {
    var ths = this
    if ($(this).hasClass('voted-up')) {
        $(this).text("  " + (parseInt($(this).text(), 10) - 1).toString(10));
        $(this).removeClass('voted-up')
        var vote = 0;

    } else {

        $(this).text("  " + (parseInt($(this).text(), 10) + 1).toString(10));
        vote = 1;
        $(this).addClass('voted-up');
        if ($(this).siblings('label.comment-vote-down').hasClass('voted-down')){
            $(this).siblings('label.comment-vote-down').text("  " +
                (parseInt($(this).siblings('label.comment-vote-down')
                    .text(), 10) + 1).toString(10));
            $(this).siblings('label.comment-vote-down')
                   .removeClass('voted-down');
        }
    }

    $.ajax({
        type: 'POST',
        url: '/comment_vote/',
        data:  {
            'comment': $(this).parents('div.comment-data').attr('data-id'),
            'vote': vote
        },
        success: function(data) {
            var vote = 1;
            $.ajax({
                type: 'PUT',
                url: '/voters/',
                data:  {
                    'comment': $(ths).parents('div.comment-data').attr('data-id'),
                    'vote': vote
                },
                success: function(data) {
                    $(ths).attr({title: data.message})
                           .popover("fixTitle")
                           .popover("show")
                }
            });
        }
    });

});

$('label.comment-vote-down').on('click', function() {
    var ths = this;
    if ($(this).hasClass('voted-down')) {
        $(this).text("  " + (parseInt($(this).text(), 10) + 1).toString(10));
        $(this).removeClass('voted-down');
        var vote = 0;

    } else {
        vote = -1;
        $(this).text("  " + (parseInt($(this).text(), 10) - 1).toString(10));
        $(this).addClass('voted-down');
        if ($(this).siblings('label.comment-vote-up')
                   .hasClass('voted-up')) {
            $(this).siblings('label.comment-vote-up')
                   .removeClass('voted-up');
            $(this).siblings('label.comment-vote-up').text("  " +
                (parseInt($(this).siblings('label.comment-vote-up')
                .text(), 10) - 1).toString(10));
        }
    }

    $.ajax({
        type: 'POST',
        url: '/comment_vote/',
        data:  {
            'comment': $(this).parents('div.comment-data').attr('data-id'),
            'vote': vote
        },
        success: function(data) {
            var vote = -1;
            $.ajax({
                type: 'PUT',
                url: '/voters/',
                data:  {
                    'comment': $(ths).parents('div.comment-data').attr('data-id'),
                    'vote': vote
                },
                success: function(data) {
                    $(ths).attr({title: data.message})
                           .popover("fixTitle")
                           .popover("show")
                }
            });
        }
    });
});


$('label.comment').hover(function() {
    var ths = this;

    if ($(this).hasClass("glyphicon-thumbs-up")) {
        var vote = 1;
    } else if ($(this).hasClass("glyphicon-thumbs-down")) {
        vote = -1;
    }

    $.ajax({
        type: 'PUT',
        url: '/voters/',
        data:  {
            'comment': $(this).parents('div.comment-data').attr('data-id'),
            'vote': vote
        },
        success: function(data) {
            $(ths).attr({title: data.message})
                   .popover("fixTitle")
                   .popover("show")
        }
    });
},
function() {
    var ths = this;
    setTimeout(function() {
        if ($('div.popover:hover').length === 0) {
            $(ths).popover("destroy");
        } else {
            $(ths).next('div.popover').mouseleave(function() {
                if ($(ths).next('label.comment:hover').length === 0) {
                    $(ths).popover("destroy");
                }
            });
        }
    }, 100)
});
