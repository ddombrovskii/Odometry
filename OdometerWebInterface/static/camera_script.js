// ! Functions that deal with button events

var resolution_width  = 800;
var resolution_height = 600;

var curr_offset_x = 0;
var curr_offset_y = 0;
var curr_width    = 800;
var curr_height   = 600;

var frame_time = 1;


$("#cam_frame_rate").bind("change",
 function()
  {

    var data = $("#cam_frame_rate").serializeArray().reduce(
      function(acum, enumerable){
          acum[enumerable.name] = enumerable.value;
          return acum;
      },{});

    $.ajax({
      type: "POST",
      url: "/set_frame_rate",
      data: data,
      success: function(state)
      {
        var raw_data = data["cam_frame_rate"];
        raw_data = Number(raw_data.split(' ')[1]);
      },
      dataType: "application/json"
    });
  })

$("#cam_frame_time").bind("change",
 function()
  {
    var node_frame_time = $("#cam_frame_time");
    var data = node_frame_time.serializeArray().reduce(
      function(acum, enumerable){
          acum[enumerable.name] = enumerable.value;
          return acum;
      },{});

    var f_time = Number(data["cam_frame_time"].replace("sec", ""));

    if(Number.isNaN(f_time))
    {
        node_frame_time.value = String(frame_time) + "sec";
        return;
    }
    if (f_time > 10 || f_time < 0.01)
    {
        node_frame_time.value = String(frame_time) + "sec";
        return;
    }
    frame_time = f_time;
    node_frame_time.value = String(frame_time) + "sec";

    $.ajax({
      type: "POST",
      url: "/set_frame_time",
      data: data,
      success: function(state)
      {
        var raw_data = data["cam_frame_time"];
        raw_data = Number(raw_data.split(' ')[1]);
      },
      dataType: "application/json"
    });
  })


$("#camera_resolution_selector").bind("change",
 function()
  {

    var data = $("#camera_resolution_selector_form").serializeArray().reduce(
      function(acum, enumerable){
          acum[enumerable.name] = enumerable.value;
          return acum;
      },{});

    $.ajax({
      type: "POST",
      url: "/set_resolution",
      data: data,
      success: function(state)
      {
        var raw_data = data["cam_res_select"];
        raw_data = raw_data.replace('(', '');
        raw_data = raw_data.replace(')', '');
        raw_data = raw_data.split(' ').filter(Boolean).map(Number).filter(function (e) { return !Number.isNaN(e);});
        resolution_width  = raw_data[0];
        resolution_height = raw_data[1];
      },
      dataType: "application/json"
    });
  })

function clamp(value, min, max)
{
    return Math.min(Math.max(value, min), max);
}

$("#cam_geometry_form input").bind("change", function ()
 {
     var node_width    = $("#camera_width");
     var node_height   = $("#camera_height");
     var node_offset_x = $("#camera_offset_x");
     var node_offset_y = $("#camera_offset_y");

     if(!node_width   ) return;
     if(!node_height  ) return;
     if(!node_offset_x) return;
     if(!node_offset_y) return;

     node_width    = node_width   [0]
     node_height   = node_height  [0]
     node_offset_x = node_offset_x[0]
     node_offset_y = node_offset_y[0]

     width    = Number(node_width   .value);
     height   = Number(node_height  .value);
     offset_x = Number(node_offset_x.value);
     offset_y = Number(node_offset_y.value);

     if(Number.isNaN(width   )) {node_width   .value = curr_width   ; return;}
     if(Number.isNaN(height  )) {node_height  .value = curr_height  ; return;}
     if(Number.isNaN(offset_x)) {node_offset_x.value = curr_offset_x; return;}
     if(Number.isNaN(offset_y)) {node_offset_y.value = curr_offset_y; return;}

     curr_width    = width   ; // = clamp(width, 0, resolution_width)
     curr_height   = height  ; // = clamp(height, 0, current_height);
     curr_offset_x = offset_x; // = clamp(offset_x, 0, current_offset_x);
     curr_offset_y = offset_y; // = clamp(offset_y, 0, current_offset_y);

     node_width   .value = curr_width   ;
     node_height  .value = curr_height  ;
     node_offset_x.value = curr_offset_x;
     node_offset_y.value = curr_offset_y;

      var data = {"width": curr_width,
                  "height": curr_height,
                  "offset_x": curr_offset_x,
                  "offset_y": curr_offset_y};

      $.ajax({
      type: "POST",
      url: "/set_geometry",
      data: data,
      success: function(state)
      {
          console.log("geometry update");
      },
      dataType: "application/json"
    });

     console.log(width, height, offset_x, offset_y );
 })


$("button#cam-video").bind("click", function () { $.getJSON("/show_video", function (data) { console.log("show_video");})});

$("button#cam-pause").bind("click", function () { $.getJSON("/pause", function (data) { console.log("cam-pause");})});

$("button#cam-exit").bind("click", function () { $.getJSON("/exit", function (data) { console.log("cam-exit");})});

$("button#cam-calibrate").bind("click", function () { $.getJSON("/calibrate", function (data) { console.log("cam-calibrate");})});


$(function () {
  $("button#cam-recording").bind("click", function () {
    $.getJSON("/record_video", function (data) {
    console.log("cam-recording");
    });
    return false;
  });
});

$(function () {
  $("button#cam-video-mode").bind("click", function () {
    $.getJSON("/show_video", function (data) {
    console.log("cam-video-mode");
    });
    return false;
  });
});

$(function () {
  $("button#cam-get-frame").bind("click", function () {
    $.getJSON("/get_frame", function (data) {
    console.log("camera-frame");
    });
    return false;
  });
});

$(function () {
  $("button#cam-reset").bind("click", function () {
    $.getJSON("/reset", function (data) {
    console.log("camera-reset");
    });
    return false;
  });
});