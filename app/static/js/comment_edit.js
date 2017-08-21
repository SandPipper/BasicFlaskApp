$('label.for-comment-edit').on('click', function() {
    if ($(this).parents('div.comment-content').find('textarea').val() != 0) {

    if ($(this).hasClass('second-click')) {

        $(this).text('Редактироавть').removeClass('second-click');

        $(this).parents('div.comment-content')
               .children('div.comment-body')
               .html($(this).parents('div.comment-data')
                            .find('textarea')
                            .val());

        $(this).parents('div.comment-content')
               .children('div.comment-body').show();

        $(this).parents('div.comment-data').find('form')
               .remove();

        var comment_id = $(this).parents("div.comment-data").attr('data-id');

        $.ajax({
            type: 'PUT',
            url: '/comment_edit/' + comment_id,
            data: {
                    'data': $(this).parents('div.comment-content')
                                  .find('div.comment-body')
                                  .html().trim()
                  },
            success: function(data) {
                if (data.status === 1) {
                    console.log(data);
                } else {
                    console.log("Error", data);
                }
            }

        })

    } else {
        $(this).text('Применить').addClass('second-click');

        $(this).parents('div.comment-content')
               .children('div.comment-body').hide();

        $(this).parents('div.comment-content')
               .append(
"<form class='form-comment-edit'><textarea type='text' cols='90' \
                required autofocus>"
                + $(this).parents('div.comment-content')
                         .find('div.comment-body')
                         .html().trim() + "</textarea></form>");

    }

    }
})
