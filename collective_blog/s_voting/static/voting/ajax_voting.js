function Voting(// Accessors
                upvote_button_id,
                downvote_button_id,
                error_message_id,
                score_field_id,

                // Class for pressed buttons
                pressed_class,

                // Request url
                url,

                // Colors (optional):
                color_elements,
                bad_color_threshold,
                bad_color,
                good_color_threshold,
                good_color,
                neutral_color) {

    function vote (vote) {
        d3.text(url + '?vote=' + vote)
            .header('X-Requested-With', 'XMLHttpRequest')
            .header('X-CSRFToken', Cookies.get('csrftoken'))
            .post(
                function (error, data) {
                    if (error) {
                        error = error.statusText;
                    }

                    var score = parseInt(data);

                    if (isFinite(score)) {
                        d3.select(score_field_id).text(score);
                        d3.select(upvote_button_id)
                            .classed(pressed_class, vote != 1);
                        d3.select(downvote_button_id)
                            .classed(pressed_class, vote != -1);
                        if (color_elements) {
                            d3.selectAll(color_elements)
                                .classed(neutral_color, bad_color_threshold < score && score < good_color_threshold)
                                .classed(good_color, good_color_threshold <= score)
                                .classed(bad_color, score <= bad_color_threshold);
                        }
                    } else {
                        d3.select(error_message_id).text(error || data)
                            .interrupt()
                            .classed('orange', error)
                            .style('opacity', 1)
                            .transition()
                            .duration(3000)
                            .style('opacity', 0);
                    }
                }
            )
    }

    d3.select(upvote_button_id).on('click', function (e) {
        if (d3.select(upvote_button_id).classed(pressed_class)) {
            vote(1);
        } else {
            vote(0);
        }
    });
    d3.select(downvote_button_id).on('click', function (e) {
        if (d3.select(downvote_button_id).classed(pressed_class)) {
            vote(-1);
        } else {
            vote(0);
        }
    });

}