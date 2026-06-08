const target = process.env.npm_lifecycle_event;
let url;
let webUrl;
let hasStatistics = false; //统计代码是否开启
let uploadUrl;
let UEditorUrl;
let NODE_ENV;
if (target.indexOf("test") != -1) {
  url = '"https://test.xiaomingkeji.com';
  webUrl = '"https://mp.xiaomingkeji.com"';
  uploadUrl = '"https://haoxuezhuli.oss-cn-shenzhen.aliyuncs.com"';
  UEditorUrl = '"https://test.xiaomingkeji.com/h5/php/"'
  NODE_ENV = '"development"'
} else if (target.indexOf("class") != -1) {
  url = '"http://dev-new-student.xiaomingkeji.com';
  webUrl = '"http://dev-class.xiaomingkeji.com"';
  uploadUrl = '"http://haoxuezhuli.oss-cn-shenzhen.aliyuncs.com"';
  UEditorUrl='"https://dev-new-student.xiaomingkeji.com/h5/php/"';
  NODE_ENV = '"development"'
} else if (target.indexOf("sit") != -1) {
  url = '"https://bbb.yunhan100.com';
  webUrl = '"https://bbb.yunhan100.com"';
  uploadUrl = '"https://haoxuezhuli.oss-cn-shenzhen.aliyuncs.com"';
  UEditorUrl='"https://bbb.yunhan100.com/h5/php/"';
  NODE_ENV = '"sit'
} else {
  url = '"https://api.yunhan100.com';
  webUrl = '"https://www.yunhan100.com"';
  hasStatistics = true;
  uploadUrl = '"https://haoxuezhuli.oss-cn-shenzhen.aliyuncs.com"';
  UEditorUrl='"https://api.yunhan100.com/h5/php/"'
  NODE_ENV= '"production"'
}

module.exports = {
  NODE_ENV: NODE_ENV?NODE_ENV:'"production"',
  ENV_CONFIG: '"prod"',
  BASE_URL: url + '/"',
  BASE_API: url + '/api/index.php?r="',
  webUrl: webUrl,
  hasStatistics: hasStatistics,
  uploadUrl: uploadUrl,
  UEditorUrl:UEditorUrl
};
