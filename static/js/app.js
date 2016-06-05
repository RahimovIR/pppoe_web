//

$( document ).ready(function() {
    updateStatus();
});

function updateStatus() {
    $('#status-connect').hide();
    $('#status-disconnect').hide();
    $.getJSON('get_status', function(result){
        if (result.data.type == 'pppoe_status') {
            if(result.data.attributes.connect){
                $('#status-connect').show();
                $('#status-disconnect').hide();
            }else {
                $('#status-connect').hide();
                $('#status-disconnect').show();
            }
        }
    })
}

function updateLog() {
    $.getJSON('get_log', function(result){
        if (result.data.type == 'pppoe_log') {
            $('#log-container').val(result.data.attributes.rawLog);
        }
    })
}

function Connect() {
    $.getJSON('set_connect', function(result){
        console.log(result);
    })
}

function Disconnect() {
    $.getJSON('set_disconnect', function(result){
        console.log(result);
    })
}