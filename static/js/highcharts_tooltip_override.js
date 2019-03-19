/* Extension to HighCharts that forces tooltips to behave differently by overriding methods on the
   Tooltip class. The 'hide' method is replaced with a no-op procedure, so that the tooltip is
   never hidden from the chart. The 'refresh' method is overriden to include a conditional check
   for whether a point is selected before calling the original 'refresh' method. This stops the
   content of the tooltip from being updated if a point is currently selected.

   To use this, the file simply has to be sourced into the HTML *after* the Highcharts library
   (and preferrably before our other customizations, but not necessarily).

   Also, point selection *must* be enabled for the refresh-blocking function to work (the always
   show feature should work either way).

   Resources:
   + https://ahumbleopinion.com/customizing-highcharts-tooltip-visibility/
   + https://www.highcharts.com/docs/extending-highcharts/extending-highcharts

   Created 2019-03-19 by Matthew Seiler
 */
(function(H) {
    var pointSelected = false;

    // receive an event when a point is selected
    H.addEvent(H.Point, 'select', function(ev) {
        // indicate that a point is in the selected state
        pointSelected = true;
        // make sure the tooltip is updates with the selected point
        this.series.chart.tooltip.refresh(ev.target);
    });

    // receieve an event when a point is *de*selected
    H.addEvent(H.Point, 'unselect', function(ev) {
        // record that there is no longer a point selected
        console.log(ev);
        pointSelected = false;
    });

    // stop the tooltip from hiding by overriding the "hide" method
    H.wrap(H.Tooltip.prototype, 'hide', function(original) {
        // do nothing
    });

    // override the tooltip refresh method to prevent updating if a point is selected
    H.wrap(H.Tooltip.prototype, 'refresh', function(original, points) {
        if (!pointSelected) {
            // TBH I don't know what this means, but it's from here:
            // https://www.highcharts.com/docs/extending-highcharts/extending-highcharts
            // ...and what it does, is call the original refresh method
            original.apply(this, Array.prototype.slice.call(arguments, 1));
        }
    });

}(Highcharts));