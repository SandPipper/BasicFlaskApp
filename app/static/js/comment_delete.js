$('label.for-comment-del').on('click', function() {
    $(this).parents('div.comment-data').css({'webkit-filtre': 'blur(5px)',
                                                'filter': 'blur(5px)',
                                                'pointer-events': 'none'})
                                          .fadeTo(500, 0.4);
    $(this).parents("li.comment").append(
        "<label class='to-show-comment label label-lg label-success'> \
            <h6 class='label'>Восстановить</h6></label>");
    $(this).parents("li.comment").children('label.to-show-comment')
           .hide().fadeIn(600);
    var comment_id = $(this).parents("div.comment-data").attr('data-id');

    $.ajax({
        type: 'DELETE',
        url: '/comment_remove/' + comment_id,
        success: function(data) {

            if (data.status === 1) {
                console.log(data);
            } else {
                console.log("Error", data);
            }
        }
    });

    $("label.to-show-comment").on('click', function() {
        var divForCommentDel = $(this).parent("li.comment")
                                      .children("div.comment-data");
        $(divForCommentDel).css({'webkit-filtre': 'blur(0px)',
                                 'filter': 'blur(0px)',
                                 'pointer-events': 'auto'}).fadeTo(500, 1);
        var comment_id = $(divForCommentDel).attr('data-id');
        $(this).remove();
        if (comment_id) {
            $.ajax({
                type: "PUT",
                url: '/comment_remove/' + comment_id,
                success: function(data) {
                    if (data.status === 2) {
                        console.log(data);
                    } else {
                        console.log("Error", data);
                    }
                }
            });
        }
    })
})
