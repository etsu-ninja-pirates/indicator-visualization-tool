var TypeaheadSetup = (function() {

    function setup(prefetch_url, remote_url, remote_wildcard) {
        function get_tokens(datum) {
            return datum.tokens;
        }

        function get_id(datum) {
            return datum.id;
        }

        const county_source = new Bloodhound({
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            datumTokenizer: get_tokens,
            identify: get_id,
            prefetch: prefetch_url,
            remote: {
                url: remote_url,
                wildcard: remote_wildcard
            }
        });

        $("#search_box").typeahead(
            {
                highlight: true,
                minLength: 2
            },
            {
                name: "counties",
                source: county_source,
                display: "display",
                limit: 15
            }
        );
    }

    var exports = {
        init: setup
    };

    return exports;
})();
