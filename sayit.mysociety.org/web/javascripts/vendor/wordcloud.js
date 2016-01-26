(function($) {
    
  var most_common_words, // global
	  jsonUrl = '/wordcloud/', /// wordcloud as api ( location.hostname + )
	  xhr = new XMLHttpRequest();
	  
  var w = parseInt(d3.select('.wordcloud').style('width'), 10)
    , h = 200 // wordcloud wrapper
    , percent = d3.format('%');
	
  // @see http://www.jasondavies.com/wordcloud/cloud.js
  var fill = d3.scale.category20b()
	, font = '"Helvetica Neue", Helvetica, sans serif';
	
  // create the wordcloud
  var wordcloud = d3.select('.wordcloud').append('svg:svg')
  	.attr("preserveAspectRatio", "xMinYMin meet")
	.attr("width", w)
	.attr("height", h)
	.append('g')
    .attr("transform", "translate(" + [w >> 1, h >> 1] + ")");
  
  function init() {
	/// d3 json https://github.com/d3/d3-request 
	$.ajax({
		headers: {
		  contentType: "application/json; charset=utf-8",
		},
		dataType: "json",
		xhrFields: {
		  withCredentials: true
		},
		crossDomain: true,
		cache: false,
		url: jsonUrl,
		beforeSend: function(xhr) {
		  xhr.setRequestHeader('Accept', 'application/json;charset=UTF-8');
		  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
		  if(xhr && xhr.overrideMimeType) {
			xhr.overrideMimeType('application/json;charset=iso-8859-15'); 
		  }
		},
	  }).done(function(response) {
  
		most_common_words = response;
		// console.log(JSON.stringify(response));
		
		if (most_common_words.length){
		  
		// set height based on data
		// height = y.rangeExtent()[1];
		// d3.select(wordcloud.node().parentNode)
		//  .style('height', (height + margin.top + margin.bottom) + 'px')
		  
		var fontSize = d3.scale.log().range([10, 100]).domain([
            d3.min(most_common_words, function(d) { return d[1]; })
          , d3.max(most_common_words, function(d) { return d[1]; })
		]);
		  
		var words = most_common_words.map(function (d) {
				  return {
					text: d[0],
					score: d[1]
				  }
				});
		
		var cloud = d3.layout.cloud()
			  .words(words)
			  .padding(2)
			  .timeInterval(2)	
			  .size([w, h])
			  .rotate(0)
			  .font(font)
			  .fontWeight("bold")
			  .fontSize(function (d) { return fontSize(+d.score); })
			  .text(function(d) { return d.text; })
			  .on("word", function(w){ 
				w.placed = true;
		  })
		  .on("end", function (words) {
			  wordcloud.selectAll("text")
			  .data(words)
			  .enter()
			  .append("text")
			  .attr("text-anchor", "middle")
			  .attr('class', 'word_text')
			  .attr("transform", function(d) { return "translate(" + [d.x, d.y] + ")"; })
			  .style("font-family", font)
			  .style("font-weight", "bold")
              .style("cursor", "pointer")
			  .style("font-size", function(d) { return d.size + "px"; })
			  .style("fill", function(d, i) { return fill(i); })
			  .text(function(d) { return d.text; })
			  .on("click", function (d) {
				window.location = '/search/?q=' + d.text;
			  });
		  });
  
			cloud.start();
		}
	
  }).error(function (xhr, textStatus, errorThrown) {
		// console.log(xhr.responseText || textStatus);
  });

  }
  
d3.select(window).on('load', init);

}(jQuery));