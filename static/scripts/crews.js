var state = {
    logged_in: false,
};

var data = {
    crews: {},
    flight_rows_cnt: 100,
    flight_middle_id: 0,
};

function setState(newState) {
    state = newState;
    localStorage.setItem('airlines-state', JSON.stringify(state));
}

function refreshUser(state) {
    if (state.logged_in) {
        $('#logged-info').show();
        $('#login-form').hide();
        $('#username').text(state.username);
        $('#for-logged').show();
    } else {
        $('#logged-info').hide();
        $('#login-form').show();
        $('#for-logged').hide();
    }
}

function refreshAll(state) {
    refreshUser(state);
    requestCrews(state);
    requestMembers(state);
    requestFlights(state);
}

function make_disabled(elem) {
    elem.attr("disabled", true);
}

function make_enabled(elem) {
    elem.attr("disabled", false);
}

function make_invisible(elem) {
    elem.addClass("invisible");
}

function make_visible(elem) {
    elem.removeClass("invisible");
}

function make_error(elem, msg) {
    elem.text(msg);
    elem.removeClass("success");
    elem.addClass("error");
    make_visible(elem);
}

function make_success(elem, msg) {
    elem.text(msg);
    elem.removeClass("error");
    elem.addClass("success");
    make_visible(elem);
}

function get_change(select_list_id, chosen) {
    let change = null;
    console.log(`${select_list_id}`);
    let val = $(`${select_list_id}`).val();
    console.log("val " + val);
    console.log("chosen" + chosen);
    if (chosen != null) {
        if ($(`${select_list_id} option[value=${chosen}]`)) {
            change = chosen;
        }
        else {
            change = "add-new";
        }
    } else {
        if (!$(`${select_list_id} option[value=${val}]`)) {
            change = "add-new";
            console.log("nieaktualny");
        }
    }
    return change;
}

function refreshCrew(chosen = null) {
    let change = get_change("#crew-select", chosen);
    if (change != null) {
        $('#crew-select').val(chosen);

        if (change == "add-new") {
            $('#pilot-firstnames').val("");
            $('#pilot-lastname').val("");
            make_disabled($('#crew-delete'));
        } else {
            let c = data.crews[chosen];
            $('#pilot-firstnames').val(c.pilot_firstnames);
            $('#pilot-lastname').val(c.pilot_lastname);
            make_enabled($('#crew-delete'));
        }
        requestMembers(state);
        refreshMembers(null, true);
    }
}

function requestCrews(state, chosen = null) {
    $.post('/ajax/crews/',
        {
            username: state.username,
            password: state.password
        }, function (res) {
            data.crews = res.crews;
            let flight_crew_select = $("#flight-crew-select");
            let crew_select = $('#crew-select');
            let flight_crew_select_val = flight_crew_select.val();
            if (flight_crew_select_val == null)
                flight_crew_select_val = "";
            let crew_select_val = crew_select.val();
            if (crew_select_val == null)
                crew_select_val = "add-new";
            crew_select.empty();
            crew_select.append($(`<option value="add-new">Add a new crew</option>`));
            flight_crew_select.empty();
            for (id in data.crews) {
                let c = data.crews[id];
                let option_txt = `<option value="${id}">${id} (${c.pilot_firstnames} ${c.pilot_lastname})</option>`;
                crew_select.append($(option_txt));
                flight_crew_select.append($(option_txt));
            }
            crew_select.val(crew_select_val);
            flight_crew_select.val(flight_crew_select_val);
        }).always(function () {
           refreshCrew(chosen);
        });
}

function refreshMembers(chosen=null, crew_id_changed=false) {
    let change = get_change("#member-select", chosen);

    if (crew_id_changed) {
        if ($('#crew-select').val() == "add-new") {
            $('#members').empty();
            make_disabled($('#member-select'));
            make_disabled($('#member-save'));
            make_disabled($('#member-firstnames'));
            make_disabled($('#member-lastname'));
            make_invisible($('#member-save-log'));
            change = "add-new";
        } else {
            make_enabled($('#member-select'));
            make_enabled($('#member-save'));
            make_enabled($('#member-firstnames'));
            make_enabled($('#member-lastname'));
        }
    }

    if (change != null) {
        if (change == 'add-new') {
            $('#member-select').val("add-new");
            $('#member-firstnames').val("");
            $('#member-lastname').val("");
            make_disabled($('#member-delete'));
        }
         else {
            $('#member-select').val(change);
            $('#member-firstnames').val(data.members[change].firstnames);
            $('#member-lastname').val(data.members[change].lastname);
            make_enabled($('#member-delete'));
        }
    }

}

function requestMembers(state, chosen=null) {
    let crew_id = $('#crew-select').val();
    if (crew_id != "add-new") {
        $.post('/ajax/crew-members/',
            {
                username: state.username,
                password: state.password,
                crew_id: crew_id
            }, function (res) {
                data.members = res.members;
                let list = $('#members');
                let select = $('#member-select');
                let val = select.val();
                if (val == null)
                    val = "add-new";
                list.empty();
                select.empty();
                select.append($(`<option value="add-new">Add a new member</option>`));
                for (id in data.members) {
                    let m = data.members[id];
                    list.append($(`<li>${m.firstnames} ${m.lastname}</li>`))
                    select.append(
                        $(`<option value="${id}">${m.firstnames} ${m.lastname}</option>`));
                }
                select.val(val);
            }).always(function () {
            refreshMembers(chosen);
        });
    }
}

function refreshFligth(chosen = null, forced_udpate=false) {
    let change = get_change("#flight-select", chosen);
    if (change == "add-new")
        change = "blank";
    console.log("change " + change);
    if (forced_udpate) {
        change = $('#flight-select').val();
    }
    if (change != null) {
        $('#flight-select').val(change);
        console.log("zmieniam");
        switch(change) {
            case "blank":
                $('#flight-crew-select').val("");
                make_disabled($('#flight-crew-select'));
                make_disabled($('#flight-save'));
                break;
            case "prev-res":
                data.flight_middle_id -= data.flight_rows_cnt / 2;
                requestFlights(state, "blank");
                break;
            case "next-res":
                data.flight_middle_id += data.flight_rows_cnt / 2;
                requestFlights(state, "blank");
                break;
            default:
                data.flight_middle_id = change;
                $.post('/ajax/flight-crew/',
                {
                    username: state.username,
                    password: state.password,
                    flight_id: change,
                }, function (res, success) {
                    make_enabled($('#flight-crew-select'));
                    make_enabled($('#flight-save'));
                    console.log(res.flight_crew_id);
                    if (res.flight_crew_id != null) {
                        $('#flight-crew-select').val(res.flight_crew_id);
                    } else {
                        $('#flight-crew-select').val("");
                    }
                });
                break;
        }
    }
}

function requestFlights(state, chosen = null) {
    $.get(`/ajax/flights-ids/${data.flight_rows_cnt}/`,
        {
            flight_middle_id: data.flight_middle_id
        }, function (res) {
            data.flights = res.flights;
            let select = $('#flight-select');
            let val = select.val();
            console.log("przed podminaą" + val);
            console.log("poprednia val " + val);
            select.empty();
            select.append($(`<option value="blank"></option>`));
            select.append($(`<option value="prev-res">...</option>`));
            console.log(data.flights);
            for (i in data.flights) {
                let id = parseInt(data.flights[i]);
                select.append(
                    $(`<option value=${id}>${id}</option>`));
            }
            select.append($(`<option value="next-res">...</option>`));
            if (val == null) {
                val = "blank";
            }
            select.val(val);
            console.log("przywracam " + select.val());
        }).always(function () {
           refreshFligth(chosen);
        });
}

$().ready(function () {
    let cachedState = localStorage.getItem('airlines-state');
    if (cachedState != null) {
        setState(JSON.parse(cachedState));
    } else {
        setState(state);
    }

    refreshUser(state);
    requestCrews(state, "add-new");
    requestFlights(state, "blank");

    $('#pilot-firstnames').val("");
    $('#pilot-lastname').val("");
    $('#member-firstnames').val("");
    $('#member-lastname').val("");

    setInterval(function() {refreshAll(state);}, 3000);

    $('#login').click(function () {
        let username = $('#input-username').val();
        let password = $('#input-password').val();
        $.post('/ajax/login/',
            {
                username: username,
                password: password
            }, function () {
                state.logged_in = true;
                state.username = username;
                state.password = password;
                setState(state);
                refreshAll(state);
            }).fail(function () {
            alert('Error while logging in. Check username and password.');
        });
    });

    $('#logout').click(function () {
        state.logged_in = false;
        state.username = "";
        state.password = "";
        setState(state);
        refreshAll(state);
    });

    $('#crew-select').on('change', function () {
        refreshCrew(this.value);
        make_invisible($('#crew-save-log'));
        refreshMembers();
    });

    $('#crew-save').click(function () {
        id = $('#crew-select').val();
        $.post('/ajax/save-crew/', {
            username: state.username,
            password: state.password,
            pilot_firstnames: $('#pilot-firstnames').val(),
            pilot_lastname: $('#pilot-lastname').val(),
            crew_id: id
        }, function (res, success) {
            make_success($('#crew-save-log'), "Saved.");
            requestCrews(state, res.crew_id);
        }).fail(function () {
            make_error($('#crew-save-log'), "Not saved.");
            requestCrews(state);
        });
    });

    $('#crew-delete').click(function () {
        id = $('#crew-select').val();
        $.post('/ajax/delete-crew/', {
            username: state.username,
            password: state.password,
            crew_id_to_del: id
        }, function (res, success) {
            make_success($('#crew-save-log'), "Deleted.");
            requestCrews(state, "add-new");
        }).fail(function () {
            make_error($('#crew-save-log'), "Not deleted.");
            requestCrews(state);
        });
    });

    $('#member-select').on('change', function () {
        refreshMembers(this.value);
        make_invisible($('#member-save-log'));
        refreshMembers();
    });

    $('#member-save').click(function () {
        $.post('/ajax/save-member/', {
            username: state.username,
            password: state.password,
            member_firstnames: $('#member-firstnames').val(),
            member_lastname: $('#member-lastname').val(),
            member_id: $('#member-select').val(),
            crew_id: $('#crew-select').val()
        }, function (res, success) {
            make_success($('#member-save-log'), "Saved.");
            requestMembers(state, res.id);
        }).fail(function () {
            make_error($('#member-save-log'), "Not saved.");
        });
    });

    $('#member-delete').click(function () {
        $.post('/ajax/delete-member/', {
            username: state.username,
            password: state.password,
            member_id_to_del: $('#member-select').val()
        }, function (res, success) {
            make_success($('#member-save-log'), "Deleted.");
            requestMembers(state, "add-new");
        }).fail(function () {
            make_error($('#member-save-log'), "Not deleted.");
        });
    });

    $('#flight-select').on('change', function () {
        refreshFligth(this.value);
        make_invisible($('#flight-save-log'));
    });

    $('#find-flight').click(function () {
        data.flight_middle_id = $('#find-flight-id').val();
        $('#find-flight-id').val("");
        requestFlights(state, data.flight_middle_id);
    });

    $('#flight-crew-select').on('change', function () {
        make_invisible($('#flight-save-log'));
    });

    $('#flight-save').click(function () {
        $.post('/ajax/save-flight/', {
            username: state.username,
            password: state.password,
            crew_id: $('#flight-crew-select').val(),
            flight_id: $('#flight-select').val(),
        }, function (res, success) {
            make_success($('#flight-save-log'), "Saved.");
            refreshFligth(null, true);
        }).fail(function () {
            make_error($('#flight-save-log'), "Not saved.");
        });
    });
});