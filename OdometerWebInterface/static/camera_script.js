// ! Functions that deal with button events

let resolution_width  = 800;
let resolution_height = 600;

let curr_offset_x = 0;
let curr_offset_y = 0;
let curr_width    = 800;
let curr_height   = 600;

let frame_time = 1;

// ###################################
// #          FLASK  BINGINGS        #
// ###################################
let CAM_READ_FRAME = "/cam_read"
let CAM_PAUSE = "/cam_pause"
let CAM_EXIT = "/cam_exit"
let CAM_RESET = "/cam_reset"
let CAM_CALIBRATE = "/cam_calibrate"
let CAM_RECORD_VIDEO = "/cam_record"
let CAM_SHOW_VIDEO = "/cam_video"
let CAM_SLAM_MODE = "/cam_slam"
let CAM_DEPTH_MODE = "/cam_depth"
let CAM_SET_FRAME_RATE = "/cam_set_frame_rate"
let CAM_SET_FRAME_TIME = "/cam_set_frame_time"
let CAM_SET_RESOLUTION = "/cam_set_resolution"
let CAM_SET_GEOMETRY = "/cam_set_geometry"
let CAM_SET_VIDEO_FILE_PATH = "/cam_set_record_file_path"
let CAM_SET_CALIB_FILE_PATH = "/cam_set_calib_file_path"
let CAM_SET_DEPTH_FILE_PATH = "/cam_set_depth_file_path"
let CAM_SET_SLAM_FILE_PATH = "/cam_set_slam_file_path"
// ###################################
// #           HTML  BINGINGS        #
// ###################################
let HTML_CAM_READ_FRAME          = "button#cam-get-frame"
let HTML_CAM_PAUSE               = "button#cam-pause"
let HTML_CAM_EXIT                = "button#cam-exit"
let HTML_CAM_RESET               = "button#cam-reset"
let HTML_CAM_CALIBRATE           = "button#cam-calibrate"
let HTML_CAM_RECORD_VIDEO        = "button#cam-recording"
let HTML_CAM_SHOW_VIDEO          = "button#cam-video"
let HTML_CAM_SLAM_MODE           = "button#cam-slam"
let HTML_CAM_DEPTH_MODE          = "button#cam-depth"
let HTML_CAM_SET_FRAME_RATE      = "#cam_frame_rate"
let HTML_CAM_SET_FRAME_TIME      = "#cam_frame_time"
let HTML_CAM_SET_RESOLUTION      = "#camera_resolution_selector"
let HTML_CAM_SET_GEOMETRY        = "#cam_geometry_form"
let HTML_CAM_SET_VIDEO_FILE_PATH = ""
let HTML_CAM_SET_CALIB_FILE_PATH = ""
let HTML_CAM_SET_DEPTH_FILE_PATH = ""
let HTML_CAM_SET_SLAM_FILE_PATH  = ""

function param_request(key)
{	
	var html_node = $(key);
	if (!html_node) return { undefined, undefined };
	var node_data = html_node.serializeArray().reduce(function(acum, enumerable){ acum[enumerable.name] = enumerable.value; return acum; },{});
	return { html_node, node_data };
}

function param_post(data, url, validate_callback, post_callback)
{
     if(validate_callback != null) if(!validate_callback(data))return;

	  $.ajax({
      type: "POST",
      url: url,
      data: data,
      success: function(state)
      {
        if(post_callback != null) post_callback(state);
      },
      dataType: "application/json"
    });
}

$(HTML_CAM_SET_FRAME_RATE).bind("change",
 function()
  {
    var{html_node, node_data} = param_request(HTML_CAM_SET_FRAME_RATE);
	if(!html_node)return;
    param_post(node_data, CAM_SET_FRAME_RATE, null, null);
  })

$(HTML_CAM_SET_FRAME_TIME).bind("change",
 function()
  {
	var{html_node, node_data} = param_request(HTML_CAM_SET_FRAME_TIME);
	if(!html_node)return;
    param_post(node_data, CAM_SET_FRAME_TIME, function(){
	   var f_time = Number(Object.values(node_data)[0]);
	   if(Number.isNaN(f_time))
	   {
			html_node.value = String(frame_time) + "sec";
			return false;
	   }
	   if (f_time > 10 || f_time < 0.01)
	   {
			html_node.value = String(frame_time) + "sec";
			return false;
	   }
	   frame_time = f_time;
	   html_node.value = String(frame_time) + "sec";
	   return true;
	}, 
    function(){
    });
  })

$(HTML_CAM_SET_RESOLUTION).bind("change",
 function()
  {
    var{html_node, node_data} = param_request(HTML_CAM_SET_RESOLUTION);
	if(!html_node)return;
    param_post(node_data, CAM_SET_RESOLUTION, null,
    function(data)
    {
        var raw_data = Object.values(node_data)[0];
        raw_data = raw_data.replace('(', '');
        raw_data = raw_data.replace(')', '');
        raw_data = raw_data.split(' ').filter(Boolean).map(Number).filter(function (e) { return !Number.isNaN(e);});

        resolution_width  = raw_data[0];
        resolution_height = raw_data[1];
    });
  })

function clamp(value, min, max)
{
    return Math.min(Math.max(value, min), max);
}

$(HTML_CAM_SET_GEOMETRY + " " + "input").bind("change", function ()
 {
     var{html_node_width, node_width_data} = param_request("#camera_width");
     var{html_node_height, node_height_data} = param_request("#camera_height");
     var{html_node_off_x, node_off_x_data} = param_request("#camera_offset_x");
     var{html_node_off_y, node_off_y_data} = param_request("#camera_offset_y");

     console.log(html_node_width, html_node_height, html_node_off_x, html_node_off_y);

     if(!html_node_width ) return;
     if(!html_node_height) return;
     if(!html_node_off_x ) return;
     if(!html_node_off_y ) return;


     node_width    =  Object.values(node_width_data )[0];
     node_height   =  Object.values(node_height_data)[0];
     node_offset_x =  Object.values(node_off_x_data )[0];
     node_offset_y =  Object.values(node_off_y_data )[0];

     width    = Number(node_width   .value);
     height   = Number(node_height  .value);
     offset_x = Number(node_offset_x.value);
     offset_y = Number(node_offset_y.value);

     if(Number.isNaN(width   )) {html_node_width .value = curr_width   ; return;}
     if(Number.isNaN(height  )) {html_node_height.value = curr_height  ; return;}
     if(Number.isNaN(offset_x)) {html_node_off_x .value = curr_offset_x; return;}
     if(Number.isNaN(offset_y)) {html_node_off_y .value = curr_offset_y; return;}

     curr_width    = width   ; // = clamp(width, 0, resolution_width)
     curr_height   = height  ; // = clamp(height, 0, current_height);
     curr_offset_x = offset_x; // = clamp(offset_x, 0, current_offset_x);
     curr_offset_y = offset_y; // = clamp(offset_y, 0, current_offset_y);

     html_node_width .value = curr_width   ;
     html_node_height.value = curr_height  ;
     html_node_off_x .value = curr_offset_x;
     html_node_off_y .value = curr_offset_y;

      var data = {"width": curr_width,
                  "height": curr_height,
                  "offset_x": curr_offset_x,
                  "offset_y": curr_offset_y};
      console.log(data);
      $.ajax({
      type: "POST",
      url: CAM_SET_GEOMETRY,
      data: data,
      success: function(state)
      {
          console.log("geometry update");
      },
      dataType: "application/json"
    });

     console.log(width, height, offset_x, offset_y );
 })

$("button#cam-video").bind("click", function () { $.getJSON("/cam_video", function (data) { console.log("camera-video-mode");})});

$("button#cam-pause").bind("click", function () { $.getJSON("/cam_pause", function (data) { console.log("camera-pause");})});

$("button#cam-exit").bind("click", function () { $.getJSON("/cam_exit", function (data) { console.log("camera-exit");})});

$("button#cam-calibrate").bind("click", function () { $.getJSON("/cam_calibrate", function (data) { console.log("camera-calibrate-mode");})});

$("button#cam-recording").bind("click", function () { $.getJSON("/cam_record", function (data) { console.log("camera-record-mode");})});

$("button#cam-video-mode").bind("click", function () { $.getJSON("/cam_video", function (data) { console.log("camera-video-mode");})});

$("button#cam-get-frame").bind("click", function () { $.getJSON("/cam_read", function (data) { console.log("camera-read");})});

$("button#cam-reset").bind("click", function () { $.getJSON("/cam_reset", function (data) { console.log("camera-reset");})});
