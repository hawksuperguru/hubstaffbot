$(document).ready(function(){

    $("#save_output").click(function() {

        var filter_date = $(".datetime").text().trim();
        if ( filter_date == "None" ) {
            filter_date = " "
        }

        data = {
            'filter_date': filter_date
        }
        var url = "/hubbot/output/";
        var dataType = "application/json";
    
        $.ajax({
            type: "POST",
            url: url,
            data: data,
            success: function(response) {
                alert(response);
            },
            dataType: dataType
        });
    });

}); 