/**
 * Created by mhassan on 8/30/17.
 */
$(document).ready(function () {
    if(jQuery.browser.mobile){
        $('#browser-alert').show();
    }
    $('.tooltip-div').tooltip();
});

function select_checkbox(event) {
    $(event.target).find('input').prop('checked', 'checked');
}

$('#play_sound').click(function () {

    var urdu_text_area = $('#urdu_text_area').val();
    $('.alert').hide();
    if (urdu_text_area == '') {
        $('#error-message').empty().append('Kindly add some text and click play button');
        $('#error').show();
    }
    else if (/[a-zA-Z]+/.test(urdu_text_area) == true) {
        $('#error-message').empty().append('No English Alphabet is allowed');
        $('#error').show();
    }
    else {
        $('#loading-div').show();
        var settings = {
            "crossDomain": true,
            "url": "/tts/generate/voice/html/",
            "method": "POST",
            "data": {
                "text": urdu_text_area,
                "voice": $("input[name='voice_option']:checked").val()
            }
        };

        $.ajax(settings)
            .done(function (response) {
                $('#output_div').empty().append(response);
                $('#loading-div').hide();
                $('#output_div').find('.generated_voice').get(0).play();
            })
            .fail(function (response) {
                $('#loading-div').hide();
                $('#error-message').empty().append('There was some error. Try by adding small text');
                $('#error').show();
            });
    }
});

function play_evaluation_sound(sound_id) {
    var voice_option = sound_id + '_voice_option';
    var urdu_text_area = $('#text_' + sound_id).text();
    $('#loading_img_' + sound_id).show();
    var settings = {
        "crossDomain": true,
        "url": "/tts/generate/voice/html/",
        "method": "POST",
        "data": {
            "text": urdu_text_area,
            "voice": $("input[name='voice_option']:checked").val()
        }
    };

    $.ajax(settings).done(function (response) {
        var output_dev = $('#output_div_' + sound_id);
        output_dev.empty().append(response);
        $('#loading_img_' + sound_id).hide();
        output_dev.find('.generated_voice').get(0).play();
    });
}


function submit_evaluation_form() {
    $('#loading-div').show();
    var json_data = [];
    var all_forms = $('.voice_row');
    all_forms.each(function () {
        var tmp = {

            data: $(this).attr("id"),
            voice: $("input[name='voice_option']:checked").val(),
            understandability: $(this).find("input[name*='understandability']:checked").val(),
            naturalness: $(this).find("input[name*='naturalness']:checked").val(),
            pleasantness: $(this).find("input[name*='pleasantness']:checked").val(),
            overall: $(this).find("input[name*='overall']:checked").val()

        };
        json_data.push(tmp);
    });
    var settings = {
        "crossDomain": true,
        "url": "/tts/evaluate/voice/",
        "method": "POST",
        "data": {
            "form": JSON.stringify(json_data)
        }
    };
    $.ajax(settings).done(function (response) {
        $('#loading-div').hide();
        show_toast(response);
    });

}


function show_toast(msg) {
    setTimeout(function () {
        $('#snackbar').empty().html(msg);
        $('#snackbar').show();
    }, 2000);
}

function submit_personal_info_section() {
    var data = new FormData($('form')[0]);
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": "/tts/evaluation/start/",
        "method": "POST",
        "processData": false,
        "contentType": false,
        "mimeType": "multipart/form-data",
        "data": data
    };
    $.ajax(settings).done(function (response) {
        show_hide_loading_icon('hide');
        var json_response = JSON.parse(response);
        localStorage.setItem('form', json_response.id);
        evaluation_form_questions(json_response.next_url);
        $('#instruction').show();
    }).fail(function (response) {
        var json_response = JSON.parse(response.responseText);
        for (var key in json_response) {
            var error = json_response[key][0];
            var error_div = $('#' + key + '-error');
            error_div.empty().append(error);
            error_div.show();
        }
        show_hide_loading_icon('hide');
    });
}

function evaluation_form_questions(url) {
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": url,
        "method": "GET"
    };
    $.ajax(settings).done(function (response) {
        $('#evaluation-form-div').empty().append(response);
        show_hide_loading_icon('hide');
    }).fail(function (response) {
        if (response.status == 404){
            var nfe = $('#not_found_error');
            nfe.empty().append(response.responseText);
            nfe.show();
            $('#instruction').hide();
            $('#save-form').hide();
        }
        else {
            var json_response = JSON.parse(response.responseText);
            for (var key in json_response) {
                var error = json_response[key][0];
                var error_div = $('#' + key + '-error');
                error_div.empty().append(error);
                error_div.show();
            }
            show_hide_loading_icon('hide');
        }
    });
}

function show_hide_loading_icon(action) {
    var next = $('#next-icon');
    var loading = $('#loading-icon');
    if (action == 'show') {
        next.hide();
        loading.show();
    }
    else if (action == 'hide') {
        next.show();
        loading.hide();
    }

}

function next_section(intro_r_questions_url) {
    show_hide_loading_icon('show');
    $('.alert').hide();
    if (intro_r_questions_url == 'intro') {
        localStorage.clear();
        submit_personal_info_section();
    }
    else {
        var form_valid = save_form_data();
        if (form_valid) {
            evaluation_form_questions(intro_r_questions_url);
        }
        else {
            var form_error = $('#form-error');
            form_error.empty().append('Fill Highlighted Sections');
            form_error.show();
        }
    }
}

function save_form_data() {
    var all_cards = $('.card');
    var form_valid = check_all_question_are_answered(all_cards);
    if (form_valid) {
        var form_data = get_previously_saved_data('form_data');
        var processed = get_previously_saved_data('processed');
        for (var i = 0; i < all_cards.length; i++) {
            var card = all_cards[i];
            if ($(card).attr('data-type') == 1 || $(card).attr('data-type') == 2) {
                var card_data = get_mdrt_question_data(card);
                if ($.inArray(card_data.question, processed) == -1){
                    form_data.push(card_data);
                    processed.push(card_data.question)
                }

            }
            else {
                var card_data = get_mos_question_data(card);
                if ($.inArray(card_data.question, processed) == -1){
                    form_data.push(get_mos_question_data(card));
                    processed.push(card_data.question);
                }
            }
        }
        localStorage.setItem('form_data', JSON.stringify(form_data));
        localStorage.setItem('processed', JSON.stringify(processed));
        return true;
    }
    else {
        return false;
    }
}

function check_all_question_are_answered(questions) {
    var form_valid = true;
    for (var i = 0; i < questions.length; i++) {
        var card = questions[i];
        if ($(card).attr('data-type') == 1 || $(card).attr('data-type') == 2) {
            if (!get_mdrt_question_data(card)) {
                $(card).find('.card-header').addClass('red-bordered');
                form_valid = false;
            }
        }
        else {
            if (!get_mos_question_data(card)) {
                $(card).find('.card-header').addClass('red-bordered');
                form_valid = false;
            }
        }
    }
    return form_valid;
}

function get_mdrt_question_data(question) {
    var checked_checkbox = $(question).find('input:checked');
    if (checked_checkbox.length == 0) {
        return false;
    }
    else {
        return {
            'question': checked_checkbox.attr('name'),
            'type': $(question).attr('data-type'),
            'answer': checked_checkbox.val(),
            'answers': []
        };
    }
}

function get_mos_question_data(question) {

    var all_props = $(question).find('.form-table tr');
    var data = {
        'question': $(question).attr('data-id'),
        'type': $(question).attr('data-type'),
        'answer': ''
    };
    var tmp = [];
    for (var i = 0; i < all_props.length; i++) {
        var prop = all_props[i];
        var checked_checkbox = $(prop).find('input:checked');
        if (checked_checkbox.length == 0) {
            return false;
        }
        else {
            tmp.push({
                'property': checked_checkbox.attr('data-property'),
                'value': checked_checkbox.val()
            });
        }
    }
    data['answers'] = tmp;
    return data;
}

function get_previously_saved_data(key) {
    var form_data = localStorage.getItem(key);
    if (form_data == undefined) {
        form_data = []
    }
    else {
        form_data = JSON.parse(form_data)
    }
    return form_data
}

function submit_final_form() {
    var form_valid = save_form_data();
    if (form_valid) {
        save_from()
    }
    else {
        var form_error = $('#form-error');
        form_error.empty().append('Fill Highlighted Sections');
        form_error.show();
    }
}

function save_from() {
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": "/tts/evaluation/form/" + localStorage.getItem("form") + "/submit/",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "processData": false,
        "data": localStorage.getItem('form_data')
    };

    $.ajax(settings).done(function (response) {
        show_alert('Thank You', 'Thank you for evaluating', 'redirect_to_main_page');
    }).fail(function (response) {
            alert('There is some error');
        });

}

function play_sound(id, text, no_of_times) {
    $('#loading-icon-' + id).show();
    var settings = {
        "crossDomain": true,
        "url": "/tts/generate/voice/html/",
        "method": "POST",
        "data": {
            "text": text,
            "voice": 'voice_pucit_indic_urs_cg'
        }
    };

    $.ajax(settings)
        .done(function (response) {
            $('#output_div').empty().append(response);
            $('#loading-icon-' + id).hide();
            $('#output_div').find('.generated_voice').get(0).play();
            // if (no_of_times == 1){
            //     $('#play_' + id).addClass('disabled');
            // }
        })
        .fail(function (response) {
            $('#loading-icon-' + id).hide();
            alert('There is some error');
        });

}


function show_alert(heading, body, close_action) {
    $('#model-heading').empty().text(heading);
    $('#model-content').empty().text(body);
    var model = $('#alert-model');
    model.modal('show');
    model.on('hidden.bs.modal', function () {
        window[close_action]();
    });
}

function redirect_to_main_page() {
    location.href = '/tts/evaluate/';
}