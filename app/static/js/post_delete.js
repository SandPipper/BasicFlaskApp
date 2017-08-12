$("button.post-del").on('click', function(){
        $(this).parents("div.for-del").css({'webkit-filtre': 'blur(5px)',
                                            'filter': 'blur(5px)',
                                            'pointer-events': 'none'})
                                      .fadeTo(500, 0.4);
        $
        $(this).parents("li.post").append(
            "<label class='to-show label label-lg label-success'> \
                            <h6 class='label-'>Восстановить</h6></label>")
        $(this).parents("li.post").children('label.to-show').hide().fadeIn(600);
        var person_id = $(this).parents("div.for-del").attr('data-id');

        $.ajax({
            type: "DELETE",
            url: '/post_remove/' + person_id,
            success: function(result) {

                if (result.status === 1) {
                    console.log(result);
                } else {
                    console.log("Error ", result);
                }
            }
        })

$("label.to-show").on('click', function() {
    var divForDel = $(this).parent("li.post").children("div.for-del");
    $(divForDel).css({'webkit-filtre': 'blur(0px)', 'filter': 'blur(0px)',
                     'pointer-events': 'auto'})
                .fadeTo(500, 1);

    var person_id = $(divForDel).attr('data-id');
    $(this).remove();
    if (person_id) {
        $.ajax({
            type: "PUT",
            url: '/post_remove/' + person_id,
            success: function(result) {

                if (result.status === 2) {
                    console.log(result);
                } else {
                    console.log("Error ", result);
                }
            }
        })
    }
    })
    })
