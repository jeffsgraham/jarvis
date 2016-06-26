function jarv_load_main_list() {
    //populate initial list
    jarv_get_content("/inventory/item/all/");

    //highlight and clear nav sidebar list
    $('.jarv-sidebar-nav').click(function(){
        $('.jarv-sidebar-nav').removeClass('active');
        $(this).addClass('active');
    });

    //expand building sidebar list on click
    $('.jarv-sidebar-building').click(function(){
        $(this).children('ul').collapse('toggle');//.slideDown();
    });

    //prevent click propagation on sidebar rooms to buildings
    $('.jarv-sidebar-room').click(function(e){
        e.stopPropagation();
    });
    //register show event to collapse other room lists and highlight selected
    $('.jarv-sidebar-building').on('show.bs.collapse', function(){
        $('.jarv-sidebar-building').not(this).each(function(){
            $(this).children('.collapse.in').collapse('hide');
        });
        //highlight this building
        $(this).addClass('active');
    });
    //register hide event to remove highlighting from building and rooms
    $('.jarv-sidebar-building').on('hide.bs.collapse', function(){
        $(this).removeClass('active jarv-active-grey');
        $(this).find('.active').removeClass('active');
    });

    //highlight and clear room sidebar list
    $('.jarv-sidebar-room').click(function(){
        $('.jarv-sidebar-room').removeClass('active');
        $(this).parents('.jarv-sidebar-building').addClass('jarv-active-grey');
        $(this).addClass('active');
    });


    //setup hover expand for xs screen sidebar
    $('.sidebar-show').droppable({
        tolerance: "intersect",
        hoverClass: "jarv-reject-drop",
        over: function(){
            $(this).click();
        },
        accept: function() {
            //prevents building from accepting drop without removing the
            // hover-expand functionality. Thus preserving the "revert"
            // feature when the item is dropped into a building.
            if($(this).next().hasClass("in")){
                return false;
            }
            return true;
        }
    });

    //close detail pane if click registered outside pane
    //note if more elements need this functionality, add more if statements for each
    $(document).on('click', function(event) {
        if(!$(event.target).closest('#jarv-detail-pane').length)
        {
            jarv_close_details();
        }
    });

    //register searchform submission handler
    $('#jarv-search-form').submit(function(e) {
        e.preventDefault(); //prevent default action
        jarv_get_content("/inventory/item/search/" + $("#jarv-search-box").val());
    });
}

//helper function to get cookie values.
// used to get csrf token for droppable functionality
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//handles errors in ajax communications with server and displays details
function jarv_ajax_error(jqXHR, textStatus, errorThrown, message)
{
    //add content to banner
    var banner = '<div class="alert alert-danger alert-dismissible fade in" role="alert">' +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">x</span>' +
        '</button>' +
        message +
        '<div id="jarv-error-expand" class="pull-right"><a>Toggle Error Details</a></div>' +
        '<div class="collapse pre-scrollable" style="height:0px;">' +
        '<h2>Error Details</h2>' +
        jqXHR.responseText +
        '</div>' +
        '</div>';
    $('#jarv-alerts').html(banner);
    $('#jarv-error-expand').click(function(){
        $(this).next().collapse('toggle');
    });
}

function jarv_get_content(url, placeholder)
{
    //insert placeholder element(s) while waiting on long running content
    if(placeholder) {
        $("#jarv-content").empty();
        $('#jarv-content').append("<h1 class='page-header'>" + placeholder + "</h1><img class='img-responsive center-block' src='/static/img/ajax-loader.gif' />" );

        
    }

    //ajax request for content
    $.get(url, function(data){
        $("#jarv-content").empty();
        $("#jarv-content").append(data);
        
        //hide sidebar if necessary (xs screen only)
        $('.jarv-sidebar-visible').removeClass('jarv-sidebar-visible');

        //setup dropdown buttons
        $('.jarv-dropdown-overflow').click(function (){
            var dropdowntop = $(this).offset().top + $(this).outerHeight();
            var dropdownleft = $(this).prev().offset().left;
            $(this).next().css({
                'top': dropdowntop + "px",
                'left': dropdownleft + "px"
            });
        });


        //setup draggable
        $('.jarv-item-row').draggable({
            revert: "invalid",
            appendTo: $('body').children('.container-fluid'),
            scroll: false,
            helper: function(){
                var helper = $(this).clone();
                $(helper).children().not('.jarv-draggable-helper').hide();
                return helper;
            },
            opacity: 0.7,
            cursor: "no-drop",
            cursorAt: {left:-10,top: 10},
            zIndex: 1031,
            refreshPositions: true,
            delay: 300,
            handle: '.jarv-draggable-handle',
            containment: "window",
            start: function() {
                //change cursor while hovering over non-droppables
                $('html').addClass('jarv-reject-drop');
                $('input').addClass('jarv-reject-drop');
                $('button').not('.jarv-attach-droppable').addClass('jarv-reject-drop');

                //prevent attaching parent item to another item
                if(!$(this).hasClass('jarv-parent-item'))
                {
                    
                    //update attach droppable text and action_type
                    $('.jarv-attach-droppable').text('Attach Here');
                    $('.jarv-attach-droppable').attr('action_type','attach');
                    
                    //if dragging a subitem
                    if($(this).hasClass('jarv-subitem-row'))
                    {
                        //change parent item's attach droppable text and action type
                        var pid = $(this).attr('parent_id');
                        $('#'+pid).find('.jarv-attach-droppable').text('Detach');
                        $('#'+pid).find('.jarv-attach-droppable').attr('action_type','detach');

                    }

                    //hide all elements in .jarv-actions-cell that isn't .jarv-attach-droppable
                    $('.jarv-actions-cell').children().not('.jarv-attach-droppable').hide();
                    //show .jarv-attach-droppable, but not this item's or parent items'
                    $('.jarv-attach-droppable').not($(this).find('.jarv-attach-droppable')).show();
                }

                //clear confirmations/warnings from previous actions
                $('#jarv-alerts').empty();
            },
            stop: function() {
                //workaround for bug that causes building droppables to retain
                // the reject-drop class that is applied when a draggable hovers
                $(".jarv-reject-drop").each(function(){
                    $(this).removeClass("jarv-reject-drop");
                });

                //show all elements in .jarv-actions-cell that aren't .jarv-attach-droppable
                $('.jarv-actions-cell').children().not('.jarv-attach-droppable').show();
                //hide all .jarv-attach-droppable
                $('.jarv-attach-droppable').hide();
            }
        });

        //setup hover expand for sidebar room lists
        $('.jarv-hover-expand').droppable({
            tolerance: "intersect",
            hoverClass: "jarv-reject-drop",
            over: function(){
                $(this).next().collapse('show');
            },
            accept: function() {
                //prevents building from accepting drop without removing the
                // hover-expand functionality. Thus preserving the "revert"
                // feature when the item is dropped into a building.
                if($(this).next().hasClass("in")){
                    return false;
                }
                return true;
            }
        });

        //setup room droppable
        $('.jarv-sidebar-room').droppable({
            tolerance: "pointer",
            accept: ".jarv-item-row",
            hoverClass: "jarv-drop-hover",
            greedy: true,
            drop: function(e, ui) {
                //get item id
                var item_id = $(ui.draggable).attr('id');
                //get room id
                var room_id = $(this).attr("id");
                $.ajax({
                    type: "POST",
                    url: "/inventory/item/" + item_id + "/move/",
                    data: {"room": room_id, "csrfmiddlewaretoken": getCookie('csrftoken'), "item": ""},
                    success: function(data, textStatus, jqXHR) {
                        jarv_get_content($('#jarv-content-url').text());
                        $('#jarv-alerts').html(data);
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        var item_desc = $('#'+item_id).attr('description');
                        var room_desc = $('#'+room_id).attr('description');

                        var message = "A server error occurred while trying to move " + item_desc + " to " + room_desc;
                        jarv_ajax_error(jqXHR, textStatus, errorThrown, message);
                    }
                });
            }
        });
        
        //setup item-attach droppable
        $('.jarv-attach-droppable').droppable({
            tolerance: "pointer",
            accept: ".jarv-item-row",
            hoverClass:"jarv-drop-hover",
            greedy: true,
            drop: function(e, ui) {
                //get item id
                var item_id = $(ui.draggable).attr('id');
                var target_id = $(this).attr('target_id');
                var parent_id = target_id; //store for error message use
                var action_type = $(this).attr('action_type');
                //set target_id to empty if detaching
                if( action_type == "detach" )
                {
                    target_id = "";
                }
                //get submit url
                var submit_url = '/inventory/item/' + item_id + '/' + action_type + '/';
                $.ajax({
                    type: "POST",
                    url: submit_url,
                    data: {"item": target_id, "csrfmiddlewaretoken": getCookie('csrftoken')},
                    success: function(data, textStatus, jqXHR) {
                        jarv_get_content($('#jarv-content-url').text());
                        $('#jarv-alerts').html(data);
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        var item_desc = $('#'+item_id).attr('description');
                        var parent_desc = $('#'+parent_id).attr('description');
                        var message = "A server error occurred while trying to ";
                        if(action_type == "attach")
                        {
                            message += "attach " + item_desc + " to " + parent_desc;
                        }
                        else
                        {
                            message += "detach " + item_desc + " from " + parent_desc;
                        }
                        jarv_ajax_error(jqXHR, textStatus, errorThrown, message);
                    }
                });
            }
        });
    });

}


//serializes form data for submission
function jarvis_serialize_item_form(form)
{
    var attributes = {};
    
    $('.jarv-edit-attribute').each(function(){
            var key = $(this).find('select.item-attr-key').first().val();
            var value = $(this).find('input.item-attr-value').first().val();
            //only store if a value has been specified
            if (value.trim()) {
                attributes[key] = value;
            }
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
function jarv_item_form2(url, initial_data)
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
            $.get("inventory/item/attribute/add/", function(data) {
              $('#jarv-add-attr-cell').before(data);
            });
        });
        
        //set initial item data if any
        if(initial_data) {
            if(initial_data.itemType){
                $(dialog).find('select#itemType').val(initial_data.itemType);
            }
            if(initial_data.model){
                $(dialog).find('select#model').val(initial_data.model);
            }
            if(initial_data.manufacturer){
                $(dialog).find('select#manufacturer').val(initial_data.manufacturer);
            }
            $.each(initial_data.attributes, function(key, value){
                $.get("inventory/item/attribute/add/", function(data) {
                    $('#jarv-add-attr-cell').before(data);
                    $('.jarv-edit-attribute:last').find('select.item-attr-key').val(key)
                    $('.jarv-edit-attribute:last').find('input.item-attr-value').val(value)
                });

            });
        }

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

//opens details pane for selected item.
//requires url to get data from
function jarv_show_details(url) 
{
    $.get(url, function(data) {
        $('#jarv-detail-content').html(data);
        $('#jarv-detail-pane').scrollTop(0); //scroll to top of pane
        $('#jarv-detail-pane').animate({"right":"0px"}, "fast");
    });
}

//close details pane
function jarv_close_details()
{
    var paneWidth = $('#jarv-detail-pane').outerWidth();
    $('#jarv-detail-pane').animate({"right":"-" + paneWidth + "px"}, "fast");
}

function jarv_archive_item(submit_url, item_id)
{
    $.ajax({
        type: "POST",
        url: submit_url,
        data: {"active":'false', "csrfmiddlewaretoken": getCookie('csrftoken')},
        success: function(data, textStatus, jqXHR) {
            jarv_get_content($('#jarv-content-url').text());
            $('#jarv-alerts').html(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var item_desc = $('#'+item_id).attr('description');
            var message = "A server error occurred while trying to archive " + item_desc;
            jarv_ajax_error(jqXHR, textStatus, errorThrown, message);
        }
    });
}

//remove attribute form
function jarv_remove_attr_form(e, element)
{
    e.preventDefault();
    $(element).closest('.jarv-edit-attribute').remove();
}
