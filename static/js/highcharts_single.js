/*
Module for loading a single, large Highcharts chart. First displays the chart with a loading
indicator, then removes the loading indicator once some data has been loaded.

Contains all the static configuration/settings/options for the chart, and exports a function
to create and display a chart. Usage:

    SingleChart.init(
        <ID of element to contain chart>,
        <URL to get percentile series from>,
        <URL to get point series from>,
        <Title to display>
    );

Much of this used to be directly within the public/chart.html template, but as this gets more
complicated (loading data series asynchronously, fixing tooltips, etc.) it is much neater to
keep a separate file.

Created 2019-02-13 by Matthew Seiler
*/
var SingleChart = (function(context, Highcharts) {

    /* static Highcharts configuration objects */

    // https://api.highcharts.com/highcharts/xAxis
    const x_axis_options = {
        labels: {
            formatter: function() {
                if (this.value > 0 && this.value == 1){return this.value + 'st';}
                if (this.value > 1){return this.value + 'th';}
            },
            rotation: -45,
        },
        title: {
            enabled: true,
            text: 'Percentile',
        },
        crosshair: {
            label: {
                enabled: true,
                padding: 8
            },
            color: "#cccccc",
            dashStyle: "dash",
            width: 1,
        },
        min: 0,
        max: 100,
        tickInterval: 5,
    };

    // https://api.highcharts.com/highcharts/yAxis
    const y_axis_options = {
        crosshair: {
            color: "#cccccc",
            dashStyle: "dash",
            width: 1,
        }
    };

    // Wraps config objects for each series type; options defined for the series type
    // become the default for new series of that type, but can be overriden in a specific
    // series by setting the same option in the actual series object to a different value.
    // https://api.highcharts.com/highcharts/plotOptions
    const plot_options = {
        // Apply to all series types (spline, scatter, bar, etc.)
        // https://api.highcharts.com/highcharts/plotOptions.series
        series: {
            allowPointSelect: true,
            marker: {
                states: {
                    select: {
                        enabled: true,
                        fillColor: '#66b3ff',
                        symbol: 'circlepin',
                        radius: 7,
                        lineWidth: 0
                    }
                }
            },
            // Apply to all points in all series
            // https://api.highcharts.com/highcharts/plotOptions.series.point
            point: {
                events: {
                    click: function() {
                        if (cloneToolTip){
                            chart.container.firstChild.removeChild(cloneToolTip);
                        }
                        cloneToolTip = this.series.chart.tooltip.label.element.cloneNode(true);
                        chart.container.firstChild.appendChild(cloneToolTip);
                    }
                }
            }
        }
    };

    // https://api.highcharts.com/highcharts/tooltip
    const tooltip_options = {
        positioner: function () {
            return { x: 80, y: 50 };
        },
        shadow: false,
        borderWidth: 0,
        backgroundColor: 'rgba(255,255,255,0.8)'
    };

    // Complete highcharts configuration object, composed of the objects defined above;
    // this is missing a 'series' array (we will load those later) and a 'title' configuration
    // (that depends on exactly what data we're plotting, so must come from Django).
    const base_configuration = {
        tooltip: tooltip_options,
        plotOptions: plot_options,
        xAxis: x_axis_options,
        yAxis: y_axis_options
    };

    /**
     * Uses the Fetch API to request a Highchart's chart series object in JSON format.
     * When the series object is received, adds the series to the chart.
     * @param {Highcharts.chart} chart Chart instance to add data series to
     * @param {string} data_url URL to request data series from
     */
    function loadDataSeries(chart, data_url) {
        return context.fetch(data_url)
            .then(response => {
                if (response.ok) {
                    return response.json();

                } else {
                    /* Promise returned by Fetch does not reject in case of server errors,
                    only network errors. If there was a server error, cause this 'then' to
                    return a rejected promise, which will trigger our 'catch' handler */
                    throw new Error(response.text());
                }
            })
            .then(json => {
                chart.addSeries(json.config);
            })
            .catch(error => {
                // TODO: display to our user that something went wrong,
                // instead of hiding it in the console!
                context.console.log(error);
            })
    };

    /**
     * Creates a Highchart's chart, then asynchronously loads data series for it.
     * @param {string} chart_element_id DOM ID of element to contain new Highchart's chart
     * @param {string} percentile_data_url URL to load percentile data series from
     * @param {string} points_data_url URL to load data points series from
     * @param {string} chart_title Title to display on chart
     */
    function init(chart_element_id, percentile_data_url, points_data_url, chart_title) {
        // augment our base configuration with a title
        var config = base_configuration;
        config.title = {
            text: chart_title
        };

        // create a chart object
        var chart = new Highcharts.chart(chart_element_id, config);
        chart.showLoading();

        // asynchronously download the configuration object for the percentile
        // spline series, then add it to the chart
        var perc_req = loadDataSeries(chart, percentile_data_url);

        // and the same for the data points
        var pt_req = loadDataSeries(chart, points_data_url);

        // remove loading indicator when requests are finished
        // (could use .race() to hide when the *first* request completes!)
        Promise.all([perc_req, pt_req]).finally(() => {
            chart.hideLoading();
        });
    };

    // Exports: contains the members that will be made available from this module
    return { init: init };

}(this, Highcharts)); // inject our dependencies. 'this' should be 'window'
