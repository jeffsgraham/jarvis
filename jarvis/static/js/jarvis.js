function jarv_load_main_list() {
  $("#jarv-building-list").accordion({
	 collapsible: true,
	 active: false
  });
    //populate initial list
    jarv_get_content("/ajax_main_list/");

    //highlight and clear nav sidebar list
    $('.jarv-sidebar-nav').click(function(){
        $('.jarv-sidebar-nav').removeClass('active');
        $(this).addClass('active');
    });

    //highlight and clear building sidebar list
    $('.jarv-sidebar-building').click(function(){
        $('.jarv-sidebar-building').not(this).removeClass('active jarv-active-grey');
        $(this).addClass('active');
    });
    //highlight and clear room sidebar list
    $('.jarv-sidebar-room').click(function(){
        $('.jarv-sidebar-room').removeClass('active');
        $(this).parents('.jarv-sidebar-building').addClass('jarv-active-grey');
        $(this).addClass('active');
    });
}

function jarv_get_content(url)
{
    $.get(url, function(data){
        $("#jarv-content").empty();
        $("#jarv-content").append(data);
    });
}

/* jarv_dictfield_setup()
 *  
 */
function jarv_dictfield_setup()
{
    var count = $(".jarv-edit-attribute").length;
    var row;
    if(count % 3 == 0)
    {
        //add new row
      $("#jarv-edit-body").append("<tr class='jarv-edit-attribute-row'></tr>");
    }
    //append to last row
    row = $(".jarv-edit-attribute-row").last();
    $(row).append("<td class='jarv-edit-attribute'><table><tr><td><div class='jarv-attribute-add'></div></td></tr></table></td>");

}

//serializes form data for submission
function jarvis_serialize_item_form(form)
{
    var attributes = {};
    
    //add attribute key-value pairs to dictionary
    $('table.jarv-attr-edit-table').each(function(){
            var key = $(this).find('input.item-attr-key').first().val();
            var value = $(this).find('input.item-attr-value').first().val();
            attributes[key] = value;
    });

    //serialize form data
    var data = $(form).serializeArray();

    //add attribute dictionary to array
    data.push({
        name: 'attributes',
        value: JSON.stringify(attributes)
    });
    return data;
    
}

//opens dialog to edit or add an item
//requires a url to get and post form data from/to
function jarv_item_form(url)
{
    $.get(url, function(data) {
        //append dialog to content div
        $('body').append(data);
        
        //launch edit dialog
        var dialog = $('#edit-dialog').dialog({
            autoOpen: true,
            height: "auto",
            width: "auto",
            modal: true,
            position: {
                my: "center top",
                at: "center",
                of: "#jarv-content"
            },
            buttons: {
                "Save": function() {
                    //submit form data
                    $('#jarv-item-form').submit();
                },
                "Cancel": function() {
                    dialog.dialog("close");
                }
            },
            open: jarv_dictfield_setup,
            close: function(){
                //make way for future dialogs by removing closed one.
                dialog.remove();
            }
        });
        
        //register form submission handler
        $('#jarv-item-form').submit(function(e) {
            var postData = jarvis_serialize_item_form($(this));//$(this).serializeArray();
            var formURL = $(this).attr("action");
            $.ajax({
                url: formURL,
                type: "POST",
                data: postData,
                success: function(data, textStatus, jqXHR) {
                    if(data == "Saved")
                    {
                        //edit complete, close dialog
                        dialog.dialog("close");

                        //update content frame with new data
                        //note:every item view contains a hidden content url to be reloaded after changes
                        jarv_get_content($('#jarv-content-url').text());
                    }
                    else
                    {
                        //append error data to template
                        $('#jarv-error-message').empty(data);
                        $('#jarv-error-message').append(data);
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                   document.write(jqXHR.responseText); 
                }
            });
            e.preventDefault(); //prevent default action
        });
        
    });
}
