function check() {
    if (temp_task_id) {
        start_checking_result({'task_id': temp_task_id});
    }
}

check();

$('#dota_process').click(function () {
    $.ajax({
        type: "POST",
        url: temp_dota_start_url,
        data: {'csrfmiddlewaretoken': temp_csrf_token},
        dataType: "json",
        success: start_checking_result,
        error: function (rs, e) {
            {
                // alert(rs.responseText);
            }
        }
    });
})

function start_checking_result(response) {
    if (check_errors(response)) return;
    document.getElementById("dota_process").style.visibility = "hidden";
    document.getElementById("score_num").style.visibility = "hidden";
    update_score_line("В процессе обработки...")
    check_res(response.task_id);
}

function check_res(task_id) {
    var timerId = setInterval(function () {
        $.ajax({
            type: "GET",
            url: `/analyse/status/${task_id}`,
            dataType: "json",
            success: function (response) {
                console.log(response);
                if (response.status === "SUCCESS") {
                    document.getElementById("dota_process").style.visibility = "";
                    document.getElementById("score_num").style.visibility = "";
                    document.getElementById("score_num").innerText = response.result;
                    update_score_line("Твой score: ");
                    clearInterval(timerId);
                }
                if (response.status === "FAILURE") {
                    check_errors(response);
                    document.getElementById("dota_process").style.visibility = "";
                    update_score_line("Что-то пошло не так");
                    clearInterval(timerId);
                }
            },
            error: function (rs, e) {
                {
                    alert(rs.responseText);

                }
            }
        });

    }, 1000);
}

function update_score_line(message) {
    document.getElementById("score_line").innerText = message;
}

function check_errors(response) {
    if (response.error) {
        alert(response.error)
        return true;
    }
    return false;
}