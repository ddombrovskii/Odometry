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

let imu_data;
let imu_time;
let accelLines;
let omegasLines;
let anglesLines;

class Line2D
{
  constructor()
  {
	this.points = [];
	this.pointsFilt = [];
	this.pointsCap = 1024;
	for(var i = 0; i < this.pointsCap; i++) this.points.push({ x: 0.0, y: 0.0 });
  }
  appendPoint(_x, _y)
  {
	this.points.push({ x: _x, y: _y});
	if(this.points.length > this.pointsCap)this.points.shift();
  }

}
class TripleLinesPlot
{
  constructor(_container, _title, _x_title, _y_title, _line_1_title, _line_2_title, _line_3_title)
  {
	this.line1 = new Line2D();
	this.line2 = new Line2D();
	this.line3 = new Line2D();
	this.chart = new CanvasJS.Chart(_container,
	{
		title: { text: _title },
		axisX: { title: _x_title },
		axisY: { title: _y_title },
		data:[
		{
			name: _line_1_title,
			showInLegend: true,
			type: "line",
			lineThickness: 2,
			markerSize: 0,
			dataPoints: this.line1.points
		},
		{
			name: _line_2_title,
			showInLegend: true,
			type: "line",
			lineThickness: 2,
			markerSize: 0,
			dataPoints: this.line2.points
		},
		{
			name: _line_3_title,
			showInLegend: true,
			type: "line",
			lineThickness: 2,
			markerSize: 0,
			dataPoints: this.line3.points,
		}
		]
	});
  }
  updateLine1(x, y)
  {
	  this.line1.appendPoint(x, y);
  }
  updateLine2(x, y)
  {
	  this.line2.appendPoint(x, y);
  }
  updateLine3(x, y)
  {
	  this.line3.appendPoint(x, y);
  }
  update(x1, y1, x2, y2, x3, y3)
  {
	 this.line1.appendPoint(x1, y1);
     this.line2.appendPoint(x2, y2);
     this.line3.appendPoint(x3, y3);
  }
}

initCharts = function()
{
    accelLines = new TripleLinesPlot("accelContainer","Acceleration",
                                      "Time,[sec]",
                                      "Accel,[m/sec^2]",
                                      "acceleration_x",
                                      "acceleration_y",
                                      "acceleration_z");

    omegasLines = new TripleLinesPlot("omegaContainer","Omega",
                                      "Time,[sec]",
                                      "Omega,[rad/sec]",
                                      "omega_x",
                                      "omega_y",
                                      "omega_z");

	anglesLines = new TripleLinesPlot("anglsContainer", "Angles",
                                      "Time,[sec]",
                                      "Angles,[rad]",
                                      "angle_x",
                                      "angle_y",
                                      "angle_z");
}

window.onload = function()
{
    initCharts();
    var _data;
    imu_time = 0.0;
    var readBackIMU = function()
    {
        $.get("/imu_read", function(data, status)
        {
            imu_data = JSON.parse(data);
        });

        if(!imu_data)return;
        /// console.log(imu_data)
        var time = Number(imu_data["dtime"]);

        var x1 = Number(imu_data["accel"]["x"]);
        var y1 = Number(imu_data["accel"]["y"]);
        var z1 = Number(imu_data["accel"]["z"]);

        var x2 = Number(imu_data["omega"]["x"]);
        var y2 = Number(imu_data["omega"]["y"]);
        var z2 = Number(imu_data["omega"]["z"]);

        var x3 = Number(imu_data["angles"]["x"]);
        var y3 = Number(imu_data["angles"]["y"]);
        var z3 = Number(imu_data["angles"]["z"]);

        accelLines. update(imu_time, x1, imu_time, y1, imu_time, z1);
        omegasLines.update(imu_time, x2, imu_time, y2, imu_time, z2);
        anglesLines.update(imu_time, x3, imu_time, y3, imu_time, z3);
        imu_time += time;
        accelLines. chart.render();
        omegasLines.chart.render();
        anglesLines.chart.render();
    }
    setInterval(function(){readBackIMU()}, 33);
};