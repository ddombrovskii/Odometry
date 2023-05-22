var imu_gravity_scale = "";
var imu_ang_velocity = "";

var imu_accel_threshold = 0;
var imu_accel_trust_time = 0;

var imu_filter_k_arg = 1.0


let IMU_READ = "/imu_read";
let IMU_PAUSE = "/imu_pause";
let IMU_EXIT = "/imu_exit";
let IMU_RESET = "/imu_reset";
let IMU_CALIBRATE = "/imu_calibrate";
let IMU_RECORD = "/imu_record";
let IMU_SET_UPDATE_TIME = "/imu_set_update_time";
let IMU_SET_RECORD_FILE_PATH = "/imu_set_record_file_path";
let IMU_SET_CALIB_FILE_PATH = "/imu_set_calib_file_path";
let IMU_SET_GRAVITY_SCALE = "/imu_set_gravity_scale";
let IMU_SET_ANGLES_RATE = "/imu_set_angles_rate";
let IMU_SET_TRUSTABLE_TIME = "/imu_set_trustable_time";
let IMU_SET_ACCEL_THRESHOLD = "/imu_set_accel_threshold";
let IMU_K_ARG = "/imu_set_k_arg";


let HTML_IMU_UPDATE_TIME = "#imu_update_time";
let HTML_IMU_READ = "#imu_read";
let HTML_IMU_PAUSE = "#imu_pause";
let HTML_IMU_EXIT = "#imu_exit";
let HTML_IMU_RESET = "#imu_reset";
let HTML_IMU_CALIBRATE = "#imu_calibrate";

let HTML_IMU_RECORD_START = "#imu_record_start";
let HTML_IMU_RECORD_PAUSE = "#imu_record_pause";
let HTML_IMU_RECORD_END = "#imu_record_end";

let HTML_IMU_CALIBRATE_START = "#imu_record_start";
let HTML_IMU_CALIBRATE_PAUSE = "#imu_record_pause";
let HTML_IMU_CALIBRATE_END = "#imu_record_end";

let HTML_IMU_SET_UPDATE_TIME = "#imu_set_update_time";
let HTML_IMU_SET_RECORD_FILE_PATH = "#imu_set_record_file_path";
let HTML_IMU_SET_CALIB_FILE_PATH = "#imu_set_calib_file_path";
let HTML_IMU_SET_GRAVITY_SCALE = "#imu_set_gravity_scale";
let HTML_IMU_SET_ANGLES_RATE = "#imu_set_angles_rate";
let HTML_IMU_SET_TRUSTABLE_TIME = "#imu_set_trustable_time";
let HTML_IMU_SET_ACCEL_THRESHOLD = "#imu_set_accel_threshold";
let HTML_IMU_K_ARG = "#imu_set_k_arg";


$("#imu_gravity_scale_selector").bind("change",
 function()
  {
    var data = $("#imu_gravity_scale_selector").serializeArray().reduce(
      function(acum, enumerable){
          acum[enumerable.name] = enumerable.value;
          return acum;
      },{});

    $.ajax(
    { type: "POST",
      url: "/set_gravity_scale",
      data: data,
      success: function(state)
      {
        imu_gravity_scale  = data["imu_gravity_scale_select"];
      },
      dataType: "application/json"});
  })

$("#imu_velocity_scale_selector").bind("change",
 function()
  {
    var data = $("#imu_velocity_scale_selector").serializeArray().reduce(
      function(acum, enumerable){
          acum[enumerable.name] = enumerable.value;
          return acum;
      },{});

    $.ajax(
    { type: "POST",
      url: "/set_angles_velocity",
      data: data,
      success: function(state)
      {
        imu_ang_velocity = data["imu_velocity_scale_select"];
      },
      dataType: "application/json"});
  })

$("#imu_acceleration_threshold").bind("change",
 function()
  {
    var html_node = $("#imu_acceleration_threshold");
    var data = html_node.serializeArray().reduce(
      function(acum, enumerable){
          acum[enumerable.name] = enumerable.value;
          return acum;
      },{});

    data = Number(data["imu_acceleration_threshold"].replace("m/sec^2", ""));
    if(Number.isNaN(data))
    {
        html_node.value = String(imu_accel_threshold) +  "m/sec^2";
        return;
    }

    if(data <= 0.0 || data > 10.0)
    {
      html_node.value = String(imu_accel_threshold) +  "m/sec^2";
      return;
    }

    $.ajax(
    { type: "POST",
      url: "/set_accel_threshold",
      data: data,
      success: function(state)
      {
        imu_accel_threshold = data;
      },
      dataType: "application/json"});
  })

$("#imu_acceleration_trust_t").bind("change",
 function()
  {
    var html_node = $("#imu_acceleration_trust_t");
    var data = html_node.serializeArray().reduce(
      function(acum, enumerable){
          acum[enumerable.name] = enumerable.value;
          return acum;
      },{});

    data = Number(data["imu_acceleration_trust_t"].replace("sec", ""));

    if(Number.isNaN(data))
    {
        html_node.value = String(imu_accel_trust_time) +  "sec";
        return;
    }

    if(data <= 0.0 || data > 10.0)
    {
      html_node.value = String(imu_accel_trust_time) +  "sec";
      return;
    }

    $.ajax(
    { type: "POST",
      url: "/set_trust_t",
      data: data,
      success: function(state)
      {
        imu_accel_trust_time = data;
      },
      dataType: "application/json"});
  })

$("#imu_filter_k_arg").bind("change",
 function()
  {
    var html_node = $("#imu_filter_k_arg");
    var data = html_node.serializeArray().reduce(
      function(acum, enumerable){
          acum[enumerable.name] = enumerable.value;
          return acum;
      },{});

    data = Number(data["imu_filter_k_arg"]);

    if(Number.isNaN(data))
    {
        html_node.value = String(imu_filter_k_arg);
        return;
    }

    if(data < 0.0 || data > 1.0)
    {
      html_node.value = String(imu_filter_k_arg);
      return;
    }

    $.ajax(
    { type: "POST",
      url: "/set_k_arg",
      data: data,
      success: function(state)
      {
        imu_filter_k_arg = data;
      },
      dataType: "application/json"});
  })