/***********************************************************************
   Define global lookups for the jquery code
***********************************************************************/
var submit_button = "#submit"
var products = ".product"
var checked_products = products + ":checked";
var custom_products = ".custom_product";
var checked_custom_products = custom_products + ":checked";

//class for top-level custom controls
var custom_controls = ".custom_control";
var custom_control_options = ".custom_control_options";

//these are the controls that need the resample option control
//shown or hidden
var needs_resample_opts_classname = "needs_resample_opts";
var needs_resample_opts = "." + needs_resample_opts_classname;
var needs_resample_opts_checked = needs_resample_opts + ":checked";

var resample_control = "#resample_options";
var resample_method = "#resample_method";
var select_resample_method = "#select_resample_method";
var selected_resample_option = "#select_resample_method option:selected";

var reproject = "#reproject";
var reproject_div = "#reprojection";

var indices = "#indices";
var indices_div = "#indices_select";

var resize = "#resize";
var resize_option_div = "#resize_options";

var select_target_projection = "#select_target_projection";
var selected_target_projection = select_target_projection + ":selected";

var input_product_list = "#input_product_list";

var image_extents = $("#image_extents");
var image_extents_units = $(".image_extents_units");
var image_extents_units_dd = $(".image_extents_units_dd");
var image_extents_units_meters = $(".image_extents_units_meters");
var minx = $("#minx");
var miny = $("#miny");
var maxx = $("#maxx");
var maxy = $("#maxy");


var decimal_degrees = "dd";
var meters = "meters";

//this is in milliseconds
var show_hide_delay = 200;

var statistics = "#include_statistics";
var cfmask = "#include_cfmask";


$(document).ready(function(){

   /*******************************************************************
      Initial page load & initialization
   *******************************************************************/

   //disable the custom controls if no custom products are selected
   $(products).prop("checked", false);

   $(custom_controls).prop("checked", false);
   $(custom_controls).prop("disabled", true);
   $(submit_button).prop("disabled", true);
   $(statistics).prop("disabled", true);
   $(statistics).prop("checked", false);

   //hide the custom controls on page load
   $(custom_control_options).hide(0);

   //hide resample options on page load
   $(resample_options).hide(0);

   $('#available_input_products').hide(0);

   /*******************************************************************
       default the output format to gtiff
   *******************************************************************/

   $("input:radio[name='output_format']").filter("[value=gtiff]").click();



   /*******************************************************************
       TODO: Change this to disable cfmask completely
   *******************************************************************/
    $(cfmask).click(function(item) {
        var cfmaskpopup="#cfmask_popup";
        if ( $(cfmaskpopup).is(":hidden") && $(cfmask).is(':checked') ) {
            $(cfmaskpopup).dialog({
                height: 200, width: 500,
                title: 'Notice of Upcoming CFMask Discontinuation'
            });
       } else {
            $(cfmaskpopup).dialog('close')
       }
    });

   /*******************************************************************
       Event handling for displaying/hiding the available input product
       box.
   *******************************************************************/
   $('#available_input_products_open').click(function(item) {
        item.preventDefault();
       //if hidden show it & vice versa
       if ( $('#available_input_products').is(":hidden") ) {
           $('#available_input_products').css({"visibility":"visible"})
           $('#available_input_products').show(0);
           $('#available_input_products_open').text("Hide Available Products");
       }
       else {
           $('#available_input_products').hide(0);
           $('#available_input_products_open').text("Show Available Products");
       }
   });


   /*******************************************************************
       Event handler to enable & disable the submit button.
       Only enabled if there are products and scenes selected.
   *******************************************************************/

   $(products).click(function(item) {

       if ($(checked_products).length > 0) {
           if ($(input_product_list).val().length > 0) {
               $(submit_button).prop("disabled", false);
           }
       }
       else {
           $(submit_button).prop("disabled", true);
       }
   });


   /*******************************************************************
       Event handler to enable & disable the submit button.
       Only enabled if there are products and scenes selected.
   *******************************************************************/
  $(input_product_list).change(function(item) {

      if ( $(input_product_list).val().length > 0 ) {
           if ( $(checked_products).length > 0 ) {
               $(submit_button).prop("disabled", false);
           }
       }
       else {
           $(submit_button).prop("disabled", true);
       }
   });


   /*******************************************************************
       Event handler to disable & enable the custom controls.
       Depends on whether there are any customizable products
       selected.
   *******************************************************************/

   $(custom_products).click(function(item) {

       if ($(checked_custom_products).length > 0) {
           $(reproject).prop("disabled", false);
           $(resize).prop("disabled", false);
           $(statistics).prop("disabled", false);
           //$(custom_controls).prop("disabled", false);
       }
       else {
          $(custom_controls).prop("disabled", true);
          $(custom_controls).prop("checked", false);
          $(statistics).prop("disabled", true);
          $(statistics).prop("checked", false);
          $(custom_control_options).hide(show_hide_delay);
          $(resample_options).hide(show_hide_delay);
          $("#target_projection").val(undefined);
       }
   });

   /*******************************************************************
     Ties the availability of image_extents to reprojection
   *******************************************************************/
   $(reproject).click(function(item) {

       if ( $(reproject).prop("checked") == true ) {
           $(image_extents).prop("disabled", false);
       }
       else {
           if ($(image_extents).prop("checked") == true) {
               $(image_extents).click();
           }
           $(image_extents).prop("disabled", true);
       }

   });

   /*******************************************************************
       Updates the image extents units when they've been clicked
   *******************************************************************/
   $(image_extents_units).click(function(item) {
       update_bounding_box_placeholders(item.target.value);
   });


   /*******************************************************************
       Event handler to show & hide the custom controls
   *******************************************************************/

   $(custom_controls).click(function(item) {
       //built the lookup value for jquery
       //this will be the id of the element that was clicked
       //plus the jquery selector '~' and the class for
       //the custom control for that element.

       var lookup = "#" + item.target.id;
       lookup = lookup + " ~ " + custom_control_options;

       //if hidden show it & vice versa
       if ( $(lookup).is(":hidden") ) {
           $(lookup).css({"visibility":"visible"})
           $(lookup).show(show_hide_delay);
       }
       else {
           $(lookup).hide(show_hide_delay);
       }
   });

   /*******************************************************************
       Event handler to initially populate the default projection
   *******************************************************************/
   $(reproject).change(function(item) {
        if ( $(this).is(":checked") ) {
            handle_projection_selection();
        }
        else {
            $("#reproject_div").hide();
            $("#target_projection").val(undefined);
            update_pixelsize_units(meters);
            update_bounding_box_placeholders(meters);
        }
   });

   /*******************************************************************
       Event handler to deal with spectral indices selection
   *******************************************************************/
   $(indices).change(function(item) {
        if ( $(this).is(":checked") ) {
            $(indices_div).show();
        } else {
            $(indices_div).hide();
            $(".indice_product").prop('checked', false);
        }
   });

   /*******************************************************************
      Initial value population for pixelsize units (meters or dd)
   *******************************************************************/
   $(resize).click(function(item) {
       if ( $("#target_projection").val().length == 0 ) {
           update_pixelsize_units(meters);
       }
   });

   /*******************************************************************
      Initialize the bounding box placeholders
   *******************************************************************/
   $(image_extents).click(function(item) {
        if ( $("input:radio[name='image_extents|units']:checked").val() ==  undefined ) {
            $("input:radio[name='image_extents|units'][value='dd']").click();
        }

       //make sure dd is selected if the projection is lonlat
       //if ( $("#target_projection").val() == "lonlat") {
       //    $("input:radio[name='image_extents_units'][value='dd']").click();
       //}
       //else if ( $("input:radio[name='image_extents_unit']:checked").val() ==  undefined ) {
       //    if ( $("#target_projection").val() == "lonlat") {
       //        $("input:radio[name='image_extents_units'][value='dd']").click();
       //    }
       //    else {
       //        $("input:radio[name='image_extents_units'][value='meters']").click();
       //    }
       //}

   });


   /*******************************************************************
      Show/hide the resample options
   *******************************************************************/
   $(needs_resample_opts).change(function(item) {
       if ( $(needs_resample_opts_checked).length == 0) {
           $(resample_options).hide(show_hide_delay);
       }
       else {
           $(resample_options).show(show_hide_delay);
           $(resample_options).css({"visibility":"visible"})
       }
   });

});


/**************************************************************************
Event handler for projection changes.

Since the select box is not created during document load, we have
to use event delegation here to attach events to it.
once its parent is loaded and ready (reproject_div) then attach the
listener

**************************************************************************/

$(reproject_div).on('change', select_target_projection, function() {
      handle_projection_selection();
});


/**************************************************************************
Event handler for resample method changes.

Since the select box is not created during document load, we have
to use event delegation here to attach events to it.
once its parent is loaded and ready (resample_control) then attach the
listener

**************************************************************************/
$(resample_control).on('change', select_resample_method, function() {
  $(resample_method).val($(selected_resample_option).val());
});



/* Constructs html to be displayed when albers is selected as a projection */
function build_albers_options() {
var html = "";
html += "<div class='inputitem'>";
html += "<input placeholder='-90.0 to 90.0' class='projection_params_txt' type='text' id='origin_lat' name='projection|aea|latitude_of_origin'>";
html += "<label for='origin_lat'>Latitude of Origin</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input placeholder='-180.0 to 180.0' class='projection_params_txt' type='text' id='central_meridian' name='projection|aea|central_meridian'>";
html += "<label for='central_meridian'>Central Meridian</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='std_parallel_1' name='projection|aea|standard_parallel_1' placeholder='-90.0 to 90.0'>";
html += "<label for='std_parallel_1'>1st Standard Parallel</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='std_parallel_2' name='projection|aea|standard_parallel_2' placeholder='-90.0 to 90.0'>";
html += "<label for='std_parallel_2'>2nd Standard Parallel</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='false_easting' name='projection|aea|false_easting' placeholder='any float (e.g. 0.0)'>";
html += "<label for='false_easting'>False Easting</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='false_northing' name='projection|aea|false_northing' placeholder='any float (e.g. 0.0)'>";
html += "<label for='false_northing'>False Northing</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input type='hidden' id='datum' name='projection|aea|datum' />";
html += "<select class='projection_params_select' form='request_form' id='select_datum' onchange=update_datum();>";
html += "<option value='wgs84'>WGS 84</option>";
html += "<option value='nad27'>NAD 27</option>";
html += "<option value='nad83'>NAD 83</option>";
html += "</select>";

html += "<label for='datum'>Datum</label>";
html += "</div>";

return html;
}

/* Constructs html to be displayed when sinusoidal is selected as a projection */
function build_sinusoidal_options() {
  var html = "";
html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='central_meridian' name='projection|sinu|central_meridian' placeholder='-180.0 to 180.0'>";
html += "<label for='central_meridian'>Central Meridian</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='false_easting' name='projection|sinu|false_easting' placeholder='any float (e.g. 0.0)'>";
html += "<label for='false_easting'>False Easting</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='false_northing' name='projection|sinu|false_northing' placeholder='any float (e.g. 0.0)'>";
html += "<label for='false_northing'>False Northing</label>";
html += "</div>";

return html;
}

/* Constructs html to be displayed when utm is selected as a projection */
function build_utm_options() {
var html = "";
html += "<div class='inputitem'>";
html += "<label id='utm_zone_label' for='utm_zone'>UTM Zone</label>";
html += "<input class='projection_params_txt' type='text' name='projection|utm|zone' id='utm_zone' placeholder='1-60' />";
html += "<input type='hidden' id='utm_north_south' name='projection|utm|zone_ns' />";
html += "<select class='projection_params_select' form='request_form' id='select_utm_north_south' onchange=update_utm_params();>";
html += "<option value='north'>North</option>";
html += "<option value='south'>South</option>";
html += "</select>";
html += "</div>";

return html;
}

/* Constructs html to be displayed when polar stereographic is selected as a projection */
function build_ps_options() {
  var html = "";
html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='longitude_pole' name='projection|ps|longitudinal_pole' placeholder='-180.0 to 180.0'>";
html += "<label for='longitude_pole'>Longitudinal Pole</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='latitude_true_scale' name='projection|ps|latitude_true_scale' placeholder='-90.0 to -60.0 or 60.0 to 90.0'>";
html += "<label for='latitude_true_scale'>Latitude True Scale</label>";
html += "</div>";


html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='false_easting' name='projection|ps|false_easting' placeholder='any float (e.g. 0.0)'>";
html += "<label for='false_easting'>False Easting</label>";
html += "</div>";

html += "<div class='inputitem'>";
html += "<input class='projection_params_txt' type='text' id='false_northing' name='projection|ps|false_northing' placeholder='any float (e.g. 0.0)'>";
html += "<label for='false_northing'>False Northing</label>";
html += "</div>";

return html;
}


/*
Event listener for the projection selection box
*/

function handle_projection_selection(projection) {
var html = "";


 //allow the caller to override the value we go looking for.
 switchval = "";
 if (typeof projection != 'undefined') {
     switchval = projection;
 }
 else {
     switchval = $("#select_target_projection").val();
 }

switch( $('#select_target_projection').val() ) {

    case "aea":
       $("#projection_parameters").html(build_albers_options());
    $("#projection_parameters").css("display", "block");
      $("#projection_parameters").css("visibility", "visible");
       $("#target_projection").val("aea");
       $("#select_pixel_size_units").val("meters");                  //force pixel size units to meters
       update_pixelsize_units(meters);
       //update_bounding_box_placeholders(meters);
       update_available_extents_units([meters, decimal_degrees]);
       //$("input:radio[name='image_extents_units'][value='dd']").click();
       update_datum();                                               //set hidden input field for initial value
    break;

    case "sinu":
         $("#projection_parameters").html(build_sinusoidal_options());
      $("#projection_parameters").css("display", "block");
       $("#projection_parameters").css("visibility", "visible");
         $("#select_pixel_size_units").val("meters");                  //force pixel size units to meters
         update_pixelsize_units(meters);
         update_available_extents_units([meters, decimal_degrees]);
         //$("input:radio[name='image_extents_units'][value='dd']").click();
         $("#target_projection").val("sinu");
      break;

    case "ps":
          $("#projection_parameters").html(build_ps_options());
       $("#projection_parameters").css("display", "block");
         $("#projection_parameters").css("visibility", "visible");
          $("#select_pixel_size_units").val("meters");                  //force pixel size units to meters
          update_pixelsize_units(meters);
          update_available_extents_units([meters, decimal_degrees]);
          //$("input:radio[name='image_extents_units'][value='dd']").click();
          $("#target_projection").val("ps");
       break;

    case "utm":
        $("#projection_parameters").html(build_utm_options());
     $("#projection_parameters").css("display", "block");
       $("#projection_parameters").css("visibility", "visible");
        $("#target_projection").val("utm");
        $("#select_pixel_size_units").val("meters");                  //force pixel size units to meters
        update_pixelsize_units(meters);
        update_available_extents_units([meters, decimal_degrees]);
        //$("input:radio[name='image_extents_units'][value='dd']").click();
        update_utm_params();                                          //update hidden input field
        break;

    case "lonlat":
     html = "";
        $("#projection_parameters").html(html);
     $("#projection_parameters").css("display", "none");
       $("#projection_parameters").css("visibility", "hidden");
        $("#target_projection").val("lonlat");
        $("#select_pixel_size_units").val("dd");                      //force pixel size units to dd
        update_pixelsize_units(decimal_degrees);
        update_available_extents_units([decimal_degrees]);
        $("input:radio[name='image_extents|units'][value='dd']").click();
     break;

   default:
       $("#projection_parameters").html(build_albers_options());
    $("#projection_parameters").css("display", "block");
      $("#projection_parameters").css("visibility", "visible");
       $("#target_projection").val("aea");
       $("#select_pixel_size_units").val("meters");                  //force pixel size units to meters
       update_pixelsize_units(meters);
       update_available_extents_units([meters, decimal_degrees]);
       update_datum();                                               //set hidden input field for initial value
    break;
   }

   }


   function update_bounding_box_placeholders(projection_units) {
       if (projection_units == decimal_degrees) {
           minx.attr("placeholder", "-180.0 to 180.0");
           maxx.attr("placeholder", "-180.0 to 180.0");
           miny.attr("placeholder", "-90.0 to 90.0");
           maxy.attr("placeholder", "-90.0 to 90.0");
       }
       else {
           minx.attr("placeholder", "any float in projection space");
           maxx.attr("placeholder", "any float in projection space");
           miny.attr("placeholder", "any float in projection space");
           maxy.attr("placeholder", "any float in projection space");
       }

   }


   /*******************************************************************
     Shows/hides the available image_extents units
   *******************************************************************/
   function update_available_extents_units(available_units) {
       //coord_unit_dd, coord_unit_meters
       $(image_extents_units).hide();

       var i=0;
       for(i=0; i< available_units.length; i++) {
           if (available_units[i] == decimal_degrees) {
               $(image_extents_units_dd).show();
           }
           else if (available_units[i] == meters) {
               $(image_extents_units_meters).show();
           }
       }

       //if (available_units.indexOf(decimal_degrees) != -1) {
       //    $(image_extents_units_dd).show();
       //}

       //if (available_units.indexOf(meters) != -1) {
       //    $(image_extents_units_meters).show();
       //}
   }

   /*******************************************************************
   Change the pixel_size_unit label, hidden pixel_size_unit label
   to the correct values.
   *******************************************************************/

   function update_pixelsize_units(units) {
     if (units == decimal_degrees) {
          $("#pixel_size").attr("placeholder", "0.0002695 to 0.0449155");
          $("#pixel_size_unit_label").text("Decimal Degrees");
       }
       else {
          $("#pixel_size").attr("placeholder", "30.0 to 5000.0");
          $("#pixel_size_unit_label").text("Meters");
       }

       $("#pixel_size_units").val(units);
   }


   function update_utm_params() {
       $("#utm_north_south").val($("#select_utm_north_south option:selected").val());
   }

   function update_datum() {
       $("#datum").val($("#select_datum option:selected").val());
   }
