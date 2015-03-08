function jarv_load_main_list() {
    //populate initial list
    jarv_get_content("/inventory/item/all/");

    //highlight and clear nav sidebar list
    $('.jarv-sidebar-nav').click(function(){
        $('.jarv-sidebar-nav').removeClass('active');
        $(this).addClass('active');
    });

    //highlight and clear building sidebar list
    $('.jarv-sidebar-building').click(function(){
        $('.jarv-sidebar-building').not(this).each(function(){
          $(this).removeClass('active jarv-active-grey');
          $(this).find('.active').removeClass('active');
        });
        $(this).addClass('active');
        $(this).children('ul').collapse('toggle');//.slideDown();
    });
    //prevent click propagation on sidebar rooms to buildings
    $('.jarv-sidebar-room').click(function(e){
        e.stopPropagation();
    });
    //register shown event to collapse other room lists
    $('.jarv-sidebar-building').on('show.bs.collapse', function(){
        $('.jarv-sidebar-building').not(this).each(function(){
            $(this).children('.collapse.in').collapse('hide');
        });
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
        
        //setup draggable
        $('.jarv-item-row').draggable({
            revert: "invalid",
            helper: function(){
                return $(this).children().first().clone();
            },
            cursor: "no-drop",
            cursorAt: {left:-10,top: 10},
            zIndex: 1001,
            refreshPositions: true,
            containment: "document"
        });

        //setup droppable
        $('.jarv-sidebar-room').droppable({
            tolerance: "pointer",
            accept: ".jarv-item-row",
            hoverClass: "jarv-drop-hover",
            drop: function() {
                alert("Droppped");
            }
        });
    });

}


//serializes form data for submission
function jarvis_serialize_item_form(form)
{
    var attributes = {};
    
    $('.jarv-edit-attribute').each(function(){
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

function jarv_item_form2(url)
{
    $.get(url, function(data) {
        //append dialog to content div
        $('body').append(data);
        
        var dialog = $('#item-form-modal');

        //register dialog hide handler
        dialog.on('hidden.bs.modal', function(e) {
            //remove dialog
            dialog.remove();
        });

        //register save button handler
        $('#item-form-save').on('click', function() {
            $('#jarv-item-form').submit();
        });

        //launch modal
        dialog.modal({
            show: true,
            backdrop: true,
            keyboard: true
        });

        //register add_attribute button action
        $('#jarv-add-attribute').on('click', function(){
            var form_fields = '<div class="jarv-edit-attribute col-xs-6 col-sm-4 jarv-show-grid"><div class="row jarv-show-grid"><div class="col-xs-12"><input type="text" class="item-attr-key" name="attr-key" id="attr-key" class="text ui-widget-content ui-corner-all" /></div></div><div class="row jarv-show-grid"><div class="col-xs-12"><input type="text" class="item-attr-value" name="attr-value" id="attr-value" class="text ui-widget-content ui-corner-all" /></div></div></div>';
            $('#jarv-add-attr-cell').before(form_fields);
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
                        dialog.modal('hide');

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
