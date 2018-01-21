var chart;
var arr;
var data;

function setup() {
  /*[ {
	    "y": 10,
	    "x": 14,
	    "value": 59,
	    "y2": -5,
	    "x2": -3,
	    "value2": 44
	  }, {
	    "y": 5,
	    "x": 3,
	    "value": 50,
	    "y2": -15,
	    "x2": -8,
	    "value2": 12
	  }, {
	    "y": -10,
	    "x": 8,
	    "value": 19,
	    "y2": -4,
	    "x2": 6,
	    "value2": 35
	  }, {
	    "y": -6,
	    "x": 5,
	    "value": 65,
	    "y2": -5,
	    "x2": -6,
	    "value2": 168
	  }, {
	    "y": 15,
	    "x": -4,
	    "value": 92,
	    "y2": -10,
	    "x2": -8,
	    "value2": 102
	  }, {
	    "y": 13,
	    "x": 1,
	    "value": 8,
	    "y2": -2,
	    "x2": 0,
	    "value2": 41
	  }, {
	    "y": 1,
	    "x": 6,
	    "value": 35,
	    "y2": 0,
	    "x2": -3,
	    "value2": 16
	  } ]);*/
	data = {
		"num_clusters": 20,
		"start_time": 1,
		"end_time": 100,
		"x-axis": "time",
		"y-axis": "reddit_sentiment", // popularity is reddit + twitter
		"value": "cluster_size",
	};
	arr = [];
	for (var i = 0; i < 50; i++)
		arr.push({y: Math.random(), x: Math.random(), value: Math.random()}); 
	display(arr);
}

function update() {
	chart.validateData();
}

function display(data) {
	chart = AmCharts.makeChart( "chartdiv", {
	  "type": "xy",
	  "theme": "dark",
	  "balloon":{
	  	"fixedPosition":true,
	  },
		// "dataLoader": {
	 //    "url": "data.json",
	 //    "format": "json"
  // 	},
  	"dataProvider": arr,
	  "valueAxes": [ {
	    "position": "bottom",
	    "axisAlpha": 0
	  }, {
	    "minMaxMultiplier": 1.2,
	    "axisAlpha": 0,
	    "position": "left"
	  } ],
	  "graphs": [ {
	    "balloonText": "x:<b>[[x]]</b> y:<b>[[y]]</b><br>value:<b>[[value]]</b>",
	    "bullet": "circle",
	    "bulletBorderAlpha": 0.2,
	    "bulletAlpha": 0.8,
	    "lineAlpha": 0,
	    "fillAlphas": 0,
	    "valueField": "value",
	    "xField": "x",
	    "yField": "y",
	    "maxBulletSize": 100
	  }, {
	    "balloonText": "x:<b>[[x]]</b> y:<b>[[y]]</b><br>value:<b>[[value]]</b>",
	    "bullet": "circle",
	    "bulletBorderAlpha": 0.2,
	    "bulletAlpha": 0.8,
	    "lineAlpha": 0,
	    "fillAlphas": 0,
	    "valueField": "value2",
	    "xField": "x2",
	    "yField": "y2",
	    "maxBulletSize": 100
	  } ],
	  "marginLeft": 46,
	  "marginBottom": 35,
	  "export": {
	    "enabled": true
	  }
	});
}

function load() {
	$.getJSON("request-data", data, function (data, status) {
		if (status === 200) {
		    console.log(data);
		    chart.dataProvider = AmCharts.parseJSON(data);
		} else {
		  	console.log("response was not 200");
		}
		update();
	});
}