
$('label.comment-vote-up').on('click', function() {
    if ($(this).hasClass('voted-up')) {
        $(this).text("  " + (parseInt($(this).text(), 10) - 1).toString(10));
        $(this).removeClass('voted-up')
        var vote = 0;

    } else {

        $(this).text("  " + (parseInt($(this).text(), 10) + 1).toString(10));
        var vote = 1;
        $(this).addClass('voted-up');
        if ($(this).next('label.comment-vote-down').hasClass('voted-down')){
            $(this).next('label.comment-vote-down').text("  " +
                (parseInt($(this).next('label.comment-vote-down')
                    .text(), 10) + 1).toString(10));
            $(this).next('label.comment-vote-down').removeClass('voted-down');
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
            console.log(data);
        }
    });

});

$('label.comment-vote-down').on('click', function() {
    if ($(this).hasClass('voted-down')) {
        $(this).text("  " + (parseInt($(this).text(), 10) + 1).toString(10));
        $(this).removeClass('voted-down');
        var vote = 0;

    } else {
        var vote = -1;
        $(this).text("  " + (parseInt($(this).text(), 10) - 1).toString(10));
        $(this).addClass('voted-down');
        if ($(this).prev('label.comment-vote-up')
                   .hasClass('voted-up')) {
            $(this).prev('label.comment-vote-up')
                   .removeClass('voted-up');
            $(this).prev('label.comment-vote-up').text("  " +
                (parseInt($(this).prev('label.comment-vote-up')
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
            console.log(data);
        }
    });
});


function forMess(mess) {
    var voters = "";
    for (voter in mess.message) {
        voters += "<tr><td>" + voter + "</td></tr>";
    }
    console.log(voters);
    return voters;
};

$('label.glyphicon-thumbs-up.comment').hover(function() {
    var mess = {}
    var ths = this

    $.ajax({
        type: 'POST',
        url: '/voters/',
        data:  {
            'comment': $(this).parents('div.comment-data').attr('data-id'),
            'vote': 1
        },
        success: function(data) {
            console.log(data);
            mess = data;
            $(ths).attr({rel: "tooltip","html": "true",
                         "title": "<b>" + forMess(mess) + "</b>"});
        }
    });
},
function() {
    console.log("Mouse leave");
});

$('label.glyphicon-thumbs-down.comment').hover(function() {
    var mess = {}
    var ths = this

    $.ajax({
        type: 'POST',
        url: '/voters/',
        data:  {
            'comment': $(this).parents('div.comment-data').attr('data-id'),
            'vote': -1
        },
        success: function(data) {
            console.log(data);
            mess = data;
            $(ths).attr({rel: "tooltip",
                title: "<b>" + forMess(mess) + "</b>"});
            //$(ths).tooltip({"data-original-title": "<b>" + forMess(mess) + "</b>",
                            //  animation: true,
                            //  html: true});

        }

    });

},
function() {
    console.log("Mouse leave");
});
