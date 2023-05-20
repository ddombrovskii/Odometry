let _cameraSettings = null;
let _imuSettings = null;
let _odometerSettings = null;

let _cameraSettingsContent = null;
let _imuSettingsContent = null;
let _odometerSettingsContent = null;

function cameraSettings() {
if (_cameraSettings == null) _cameraSettings = document.getElementById("CameraSettings");
return _cameraSettings;
}

function imuSettings() {
    if (_imuSettings == null) _imuSettings = document.getElementById("IMUSettings");
    return _imuSettings;
}

function odometerSettings() {
    if (_odometerSettings == null) _odometerSettings = document.getElementById("OdometerSettings");
    return _odometerSettings;
}

function cameraSettingsContent() {
    if (_cameraSettingsContent == null) _cameraSettingsContent = document.getElementById("CameraSettingsContent");
    return _cameraSettingsContent;
}

function imuSettingsContent() {
    if (_imuSettingsContent == null) _imuSettingsContent = document.getElementById("IMUSettingsContent");
    return _imuSettingsContent;
}

function odometerSettingsContent() {
    if (_odometerSettingsContent == null) _odometerSettingsContent = document.getElementById("OdometerSettingsContent");
    return _odometerSettingsContent;
}

function HideAll() {
    cameraSettings().classList.remove("selected"); //  style.display = "none";
    imuSettings().classList.remove("selected");
    odometerSettings().classList.remove("selected");

    HideElement(cameraSettingsContent());
    HideElement(imuSettingsContent());
    HideElement(odometerSettingsContent());
}

function HideElement(element) {
    element.style.display = "none";
}

function ShowElement(element) {
    element.style.display = "block";
}

function CameraSettingsShow() {
    HideAll();
    cameraSettings().classList.add("selected");
    ShowElement(cameraSettingsContent());
}

function ImuSettingsShow() {
    HideAll();
    imuSettings().classList.add("selected");
    ShowElement(imuSettingsContent());
}

function OdometerSettingsShow() {
    HideAll();
    odometerSettings().classList.add("selected");
    ShowElement(odometerSettingsContent());
}