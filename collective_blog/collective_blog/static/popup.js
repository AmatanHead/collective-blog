/**
 * Window class.
 * @param closeable render `close` button.
 * @constructor
 */
var Window = function (closeable) {
    var self = this;

    this._holder = d3.select('body').append('div').classed('popup-holder', true);
    this._body = this._holder.append('div').classed('popup-body', true);
    this._holder.style('opacity', 0).transition().style('opacity', 1);

    if (closeable) {
        this._holder.append('div').classed('popup-close', true)
            .text('×');
        this._holder
            .on('click', function() { self.destroy() });
        this._body
            .on('click', function() { d3.event.stopPropagation() });
    }

    this.setup();
};

Window.prototype.setup = function () {
    this._body.append('p').text('Not implemented');
};

Window.prototype.destroy = function () {
    this._holder.transition().style('opacity', 0).remove();
};
