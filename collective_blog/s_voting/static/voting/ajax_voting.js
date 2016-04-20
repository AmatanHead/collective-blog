function VoteGroup(group_selector) {
    var self = this;

    self._init = function () {
        self.head = d3.select(group_selector);

        var meta = JSON.parse(self.head.attr('data-meta'));

        self.prefix = self.head.attr('data-prefix');
        self.url = self.head.attr('data-url');

        self.use_colors = meta.use_colors;
        self.color_tags = meta.color_tags;
        self.color_threshold = meta.color_threshold;
        self.disabled = meta.disabled;
        self.state = meta.state;

        self.color_elements = self.head.selectAll(self._pclass('color'));
        self.score_element = self.head.select(self._pid('score'));
        self.upvote_button = self.head.select(self._pid('upvote-button'));
        self.downvote_button = self.head.select(self._pid('downvote-button'));
        self.error_message = self.head.select(self._pid('error'));

        if (self.state === 1 || self.state === -1 || self.state === 0) {
            self._bind();
            self._style();
        }
    };

    /**
     * Bind callbacks to upvote and downvote buttons
     * @private
     */
    self._bind = function () {
        self.upvote_button.on('click', self._onUpvotePressed);
        self.downvote_button.on('click', self._onDownvotePressed);
    };

    self._onUpvotePressed = function () {
        if (self.disabled) {
            return;
        }

        if (self.state === 1) {
            self._request(0);
        } else {
            self._request(1);
        }
    };

    self._onDownvotePressed = function () {
        if (self.disabled) {
            return;
        }

        if (self.state === -1) {
            self._request(0);
        } else {
            self._request(-1);
        }
    };

    /**
     * Send new vote
     *
     * @param vote: +1, 0, or -1
     * @private
     */
    self._request = function (vote) {
        d3.text(self.url + '?vote=' + vote)
            .header('X-Requested-With', 'XMLHttpRequest')
            .header('X-CSRFToken', Cookies.get('csrftoken'))
            .post(self._onResponse)
    };

    self._onResponse = function (error, data) {
        if (error) {
            self._onError(error.responseText || error.statusText, 1);
            return;
        }

        try {
            data = JSON.parse(data);
        } catch (e) {
            self._onError(e.message, 1);
            return;
        }

        if (isFinite(data.score) && isFinite(data.state)) {
            self._onSuccess(data)
        } else {
            self._onError('Unknown error', 1);
        }
    };

    self._onError = function (text, is_critical) {
        self.error_message
            .interrupt()
            .classed('orange', is_critical)
            .style('opacity', 1)
            .text(text)
            .transition()
            .duration(3000)
            .style('opacity', 0);
    };

    self._onSuccess = function (data) {
        self.score_element.text(data.score);
        self.state = data.state;
        self._style();
    };

    /**
     * Apply new colors and other css based on state
     * @private
     */
    self._style = function () {
        self.upvote_button.classed('outline', self.state !== 1);
        self.downvote_button.classed('outline', self.state !== -1);

        if (self.use_colors) {
            var karma = parseInt(self.score_element.text());

            self.color_elements
                .classed(self.color_tags[2], karma < self.color_threshold[0])
                .classed(self.color_tags[1], karma >= self.color_threshold[0] && karma <= self.color_threshold[1])
                .classed(self.color_tags[0], karma > self.color_threshold[1]);
        } else {
            self.color_elements
                .classed(self.color_tags[2], false)
                .classed(self.color_tags[1], true)
                .classed(self.color_tags[0], false);
        }

        if (self.disabled) {
            self.upvote_button.style('cursor', 'not-allowed');
            self.downvote_button.style('cursor', 'not-allowed');
        } else {
            self.upvote_button.style('cursor', 'pointer');
            self.downvote_button.style('cursor', 'pointer');
        }
    };

    /**
     * Prefixed class
     * @param {string} str: class name
     * @returns {string}: .{{ prefix }}-{{ str }}
     * @private
     */
    self._pclass = function (str) {
        return '.' + self.prefix + '-' + str;
    };

    /**
     * Prefixed id
     * @param {string} str: class name
     * @returns {string}: #{{ prefix }}-{{ str }}
     * @private
     */
    self._pid = function (str) {
        return '#' + self.prefix + '-' + str;
    };


    self._init();
}
