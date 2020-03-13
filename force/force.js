
var w = 1500,
    h = 600,
    fill = d3.scale.category20();

var vis = d3.select("#chart")
  .append("svg:svg")
    .attr("width", w)
    .attr("height", h);

d3.json("force.json", function(json) {
  var force = d3.layout.force()
      .charge(-120)
      .linkDistance(90)//30)
      .nodes(json.nodes)
      .links(json.links)
      .size([w, h])
      .start();

  var link = vis.selectAll("line.link")
      .data(json.links)
    .enter().append("svg:line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); })
      .attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  var node = vis.selectAll("circle.node")
      .data(json.nodes)
      .enter().append("svg:circle")
      .attr("class", "node")
      .attr("cx", function(d) { return 10-d.x; })
      .attr("cy", function(d) { return d.y; })
      //.attr("r", 15)
      //.style("fill", function(d) { return fill(d.group); })
      .attr("r", function(d) { if (d.group == 0) return 20; return 15-d.group; })
      .style("fill", function(d) { return d3.hsl(d.color).brighter(d.group/3); })
      .style("stroke-width", function(d) { if (d.group === 0) return 4; return 1; })
      .call(force.drag);
          var text = vis.selectAll("text")
            .data(json.nodes)
            .enter().append("svg:text")
            .attr("x", function(d) { return d.x ; })
            .attr("y", function(d) { return d.y ; })
            .text(function(d) { return d.label;}) //d.name; })
            .attr("font-size","10")
            //.attr("stroke", function(d) { return fill(d.color); })

  node.append("title")
      .text(function(d) { return d.name; });

/*
  node.append("text")
      .attr("x", -10)
      //.attr("dx", function(d){return -20})
      .style("font-size", "10")
      .text(function(d) { return d.name; });
*/

  vis.style("opacity", 1e-6)
    .transition()
      .duration(1000)
      .style("opacity", 1);


  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    text.attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; });
  });
});
