/**
 * Membership management class.
 * @constructor
 */
var MembershipManagement = function (data, selector) {
    this._loadUrl = data.url;
    this._username = data.user;
    this._data = data;
    this._loading = false;
    this._selector = selector;
    Window.apply(this, [true]);
};

MembershipManagement.prototype = Object.create(Window.prototype);

Window.prototype.setup = function () {
    var self = this;

    var loading = self._body.append('p').text('Loading... ');
    self._request(
        {type: 'fetch', username: self._username},
        function (err, data) {
            loading.remove();
            try {
                self._onLoad(err, data);
            } catch (err) {
                self._body.append('p').text('Error when loading: ' + err);
            }
        }
    )
};

Window.prototype._request = function (data, callback) {
    var self = this;
    if (!self._loading) {
        self._loading = true;
        d3.text(this._loadUrl)
            .header('X-Requested-With', 'XMLHttpRequest')
            .header('X-CSRFToken', Cookies.get('csrftoken'))
            .header("Content-Type", "application/x-www-form-urlencoded")
            .post(
                "data=" + encodeURIComponent(JSON.stringify(data)),
                function (err, data) {
                    self._loading = false;
                    callback(err ? err.statusText : err, data)
                });
    }
};

Window.prototype._onLoad = function (err, data) {
    var self = this;

    self._body.text('');

    if (err) {
        self._body.append('p').text('Error: ' + err);
        return;
    }

    data = JSON.parse(data);

    self._data.ban_perm = data.ban_perm;
    self._data.accept_perm = data.accept_perm;
    self._data.manage_perm = data.manage_perm;
    self._data.is_banned = data.banned;
    console.log(self._data, data);
    if (self._data.role != data.role) {
        self._data.role = data.role;
        self._data.role_change = data.role;
    }
    updateManager(self._data, self._selector);

    self._body.append('h1').text(self._username);
    if (data.caption) { self._body.append('p').text(data.caption); }

    if (data.accept_perm || data.success == 'accept' || data.success == 'refuse') {
        self._accept_div = self._body.append('div')
            .attr('class', 'inline display-inline');
        self._accept_div.append('hr');
    }
    if (data.accept_perm) {
        self._accept = self._accept_div.append('button').text(gettext('Accept'))
            .on('click', function () { self._sendAccept(); });
        self._accept_div.append('span').html('&nbsp;&nbsp;');
        self._refuse = self._accept_div.append('button').text(gettext('Refuse'))
            .on('click', function () { self._sendRefuse(); });
    } else if (data.success == 'accept' || data.success == 'refuse') {
        self._accept_div.append('p').text(
            data.success == 'accept' ? gettext('Accepted') : gettext('Refused')
        )
    }

    if (data.manage_perm) {
        self._manage_div = self._body.append('div');
        self._manage_div.append('hr');
        var group = self._manage_div.append('div')
            .attr('style', 'column-width: 200px');
        self.can_change_settings = group.append('label')
            .text(gettext("Can change blog's settings") + ' ')
            .append('input')
            .attr('type', 'checkbox')
            .attr('checked', data.can_change_settings ? 'checked' : null);
        group.append('br');
        self.can_delete_posts = group.append('label')
            .text(gettext("Can delete posts") + ' ')
            .append('input')
            .attr('type', 'checkbox')
            .attr('checked', data.can_delete_posts ? 'checked' : null);
        group.append('br');
        self.can_delete_comments = group.append('label')
            .text(gettext("Can delete comments") + ' ')
            .append('input')
            .attr('type', 'checkbox')
            .attr('checked', data.can_delete_comments ? 'checked' : null);
        group.append('br');
        self.can_ban = group.append('label')
            .text(gettext("Can ban a member") + ' ')
            .append('input')
            .attr('type', 'checkbox')
            .attr('checked', data.can_ban ? 'checked' : null);
        group.append('br');
        self.can_accept_new_users = group.append('label')
            .text(gettext("Can accept new users") + ' ')
            .append('input')
            .attr('type', 'checkbox')
            .attr('checked', data.can_accept_new_users ? 'checked' : null);
        group.append('br');
        self.can_manage_permissions = group.append('label')
            .text(gettext("Can manage permissions") + ' ')
            .append('input')
            .attr('type', 'checkbox')
            .attr('checked', data.can_manage_permissions ? 'checked' : null);
        group.append('br');
        var section = self._manage_div.append('section')
            .attr('class', 'inline')
            .attr('style', 'margin-top: .5rem');
        self._refuse = section.append('button').text(gettext('Update'))
            .on('click', function () { self._sendManage(); });
        if (data.success == 'manage') {
            section.append('span').text(' ' + gettext('Updated'))
                .transition().duration(1000).style('opacity', 0).remove()
        }
    }

    // TODO: to do TODO
    // TODO TODO TODO
    if (data.ban_perm) {
        self._ban_div = self._body.append('div')
            .attr('class', 'inline display-inline');
        self._ban_div.append('hr');
        if (data.banned) {
            self._unban = self._ban_div.append('button')
                .text(gettext('Unban'))
                .on('click', function () { self._sendUnban(); });
        } else {
            self._ban_div.append('span').text(gettext('Ban: '));
            var group = self._ban_div.append('span')
                .attr('class', 'badge-group');
            group.append('button').text(gettext('1h'))
                .on('click', function () { self._sendBan('1h'); });
            group.append('button').text(gettext('1d'))
                .on('click', function () { self._sendBan('1d'); });
            group.append('button').text(gettext('1w'))
                .on('click', function () { self._sendBan('1w'); });
            group.append('button').text(gettext('forever'))
                .on('click', function () { self._sendBan('forever'); });
        }
    }
};

Window.prototype._sendAccept = function () {
    var self = this;

    self._accept.attr('disabled', 'disabled');
    self._refuse.attr('disabled', 'disabled');

    self._request(
        {type: 'accept', username: self._username},
        function (err, data) { self._onLoad(err, data); }
    );
};

Window.prototype._sendRefuse = function () {
    var self = this;

    self._accept.attr('disabled', 'disabled');
    self._refuse.attr('disabled', 'disabled');

    self._request(
        {type: 'refuse', username: self._username},
        function (err, data) { self._onLoad(err, data); }
    );
};

Window.prototype._sendUnban = function () {
    var self = this;

    self._unban.attr('disabled', 'disabled');

    self._request(
        {type: 'unban', username: self._username},
        function (err, data) { self._onLoad(err, data); }
    );
};

Window.prototype._sendBan = function (time) {
    var self = this;

    self._request(
        {type: 'ban', username: self._username, time: time},
        function (err, data) { self._onLoad(err, data); }
    );
};

Window.prototype._sendManage = function () {
    var self = this;

    self._request(
        {
            type: 'manage',
            username: self._username,
            can_change_settings: self.can_change_settings.node().checked,
            can_delete_posts: self.can_delete_posts.node().checked,
            can_delete_comments: self.can_delete_comments.node().checked,
            can_ban: self.can_ban.node().checked,
            can_accept_new_users: self.can_accept_new_users.node().checked,
            can_manage_permissions: self.can_manage_permissions.node().checked
        },
        function (err, data) { self._onLoad(err, data); }
    );
};

Window.prototype.destroy = function () {
    if (!this._loading) {
        this._holder.transition().style('opacity', 0).remove();
    }
};


/**
 * Setup new member manager.
 */
function setupManager () {
    var d = {};
    var selector = d3.select(this);

    d.user = selector.attr('data-user');
    d.url = selector.attr('data-url');
    d.ban_perm = selector.attr('data-ban_perm') == 'True';
    d.accept_perm = selector.attr('data-accept_perm') == 'True';
    d.manage_perm = selector.attr('data-manage_perm') == 'True';
    d.is_banned = selector.attr('data-is_banned') == 'True';
    d.rating = parseInt(selector.attr('data-rating'));
    d.role = selector.attr('data-role');

    selector.select('.member-manager')
        .on('click', function () {
            new MembershipManagement(d, selector);
        });

    updateManager(d, selector);
}

function updateManager (d, selector) {
    if (d.ban_perm || d.accept_perm || d.manage_perm) {
        selector.select('.member-manager').style('display', 'inherit')
    } else {
        selector.select('.member-manager').style('display', 'none')
    }
    if (d.is_banned) {
        selector.style('opacity', 0.5)
    } else {
        selector.style('opacity', 1)
    }
    if (d.role_change && d.role_change != 'B') {
        selector.select('.ad').text(' (' + d.role_change + ')');
    }
}
